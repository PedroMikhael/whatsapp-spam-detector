import os
import time
import base64
from email.mime.text import MIMEText

# Imports do Google
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configura o Django para podermos usar nossa função de análise
import django
# ATENÇÃO: Substitua 'spamapi' pelo nome da sua pasta de configuração, se for diferente
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spamapi.settings') 
django.setup()
from detector.services import analisar_com_gemini

# --- CONFIGURAÇÃO ---
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"] # Permissão para ler, enviar e modificar (marcar como lido)
CHECK_INTERVAL_SECONDS = 60 # Verificar por novos e-mails a cada 60 segundos

def authenticate():
    """Autentica com a API do Gmail usando o fluxo manual para servidores."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Renovando token de acesso...")
            creds.refresh(Request())
        else:
            print("Nenhum token válido encontrado. Iniciando autorização manual.")
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)

            # 1. Gera a URL de autorização
            auth_url, _ = flow.authorization_url(prompt='consent')

            print('Por favor, visite este URL para autorizar o acesso:')
            print(auth_url)

            # 2. Pede o código de autorização para o usuário
            code = input('Digite o código de autorização do navegador aqui: ')

            # 3. Troca o código pelo token de acesso
            flow.fetch_token(code=code)
            creds = flow.credentials

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    print("Autenticação bem-sucedida.")
    return build("gmail", "v1", credentials=creds)

def check_and_process_emails(service):
    """Verifica por e-mails não lidos, os analisa com Gemini e responde."""
    try:
        results = service.users().messages().list(userId="me", labelIds=["INBOX"], q="is:unread").execute()
        messages = results.get("messages", [])

        if not messages:
            print(f"[{time.ctime()}] Nenhum e-mail novo encontrado.")
            return

        for message_info in messages:
            msg = service.users().messages().get(userId="me", id=message_info["id"], format='full').execute()

            headers = msg["payload"]["headers"]
            subject = next(header["value"] for header in headers if header["name"].lower() == "subject")
            sender = next(header["value"] for header in headers if header["name"].lower() == "from")

            print(f"\n--- NOVO E-MAIL RECEBIDO ---")
            print(f"De: {sender}")
            print(f"Assunto: {subject}")

            if "data" in msg["payload"]["body"]:
                email_body_encoded = msg["payload"]["body"]["data"]
            else:
                parts = msg["payload"].get("parts", [])
                part = next(iter(p for p in parts if p["mimeType"] == "text/plain"), None)
                email_body_encoded = part["body"]["data"] if part else ""

            email_body = base64.urlsafe_b64decode(email_body_encoded).decode("utf-8")

            resultado_analise = analisar_com_gemini(email_body)
            mensagem_de_resposta = resultado_analise["user_response"]

            print(f"Análise da IA: {resultado_analise.get('analysis_details', 'N/A')}")

            send_reply(service, sender, subject, mensagem_de_resposta)

            service.users().messages().modify(userId="me", id=message_info["id"], body={'removeLabelIds': ['UNREAD']}).execute()
            print("--- RESPOSTA ENVIADA E E-MAIL MARCADO COMO LIDO ---")


    except HttpError as error:
        print(f"Ocorreu um erro na API: {error}")

def send_reply(service, to, subject, message_text):
    """Cria e envia um e-mail de resposta."""
    message = MIMEText(message_text)
    message["to"] = to
    # Extrai o e-mail do remetente, ignorando o nome
    match = re.search(r'<(.+?)>', to)
    if match:
        message["to"] = match.group(1)

    message["subject"] = f"Re: {subject}"

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {"raw": encoded_message}

    service.users().messages().send(userId="me", body=create_message).execute()

if __name__ == "__main__":
    print("Iniciando o bot de e-mail...")
    gmail_service = authenticate()
    print("Verificação inicial de e-mails...")
    while True:
        check_and_process_emails(gmail_service)
        time.sleep(CHECK_INTERVAL_SECONDS)
