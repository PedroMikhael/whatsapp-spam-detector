
import os
import time
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spamapi.settings') 
django.setup()
from detector.services import analisar_com_gemini
from detector.models import Feedback 


SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
CHECK_INTERVAL_SECONDS = 60 

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
            auth_url, _ = flow.authorization_url(prompt='consent')
            print('Por favor, visite este URL para autorizar o acesso:')
            print(auth_url)
            code = input('Digite o código de autorização do navegador aqui: ')
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
            subject = next((header["value"] for header in headers if header["name"].lower() == "subject"), "Sem Assunto")
            sender = next((header["value"] for header in headers if header["name"].lower() == "from"), "Remetente Desconhecido")

            print(f"\n--- NOVO E-MAIL RECEBIDO ---")
            print(f"De: {sender}")
            print(f"Assunto: {subject}")

            if "data" in msg["payload"]["body"]:
                email_body_encoded = msg["payload"]["body"]["data"]
            else:
                parts = msg["payload"].get("parts", [])
                part = next(iter(p for p in parts if p["mimeType"] == "text/plain"), None)
                email_body_encoded = part["body"]["data"] if part else ""

            email_body = base64.urlsafe_b64decode(email_body_encoded).decode("utf-8", errors='ignore')

            resultado_analise = analisar_com_gemini(email_body)
            mensagem_de_resposta = resultado_analise["user_response"]

            nova_analise = Feedback.objects.create(
                mensagem_original=email_body,
                remetente=sender,
                risco_ia=resultado_analise.get('risk_level', 'INDETERMINADO'),
                analise_ia=str(resultado_analise.get('analysis_details', ''))
            )
            
            print(f"Análise da IA salva no banco com ID: {nova_analise.id}")

            send_reply(service, sender, subject, mensagem_de_resposta, nova_analise.id)

            service.users().messages().modify(userId="me", id=message_info["id"], body={'removeLabelIds': ['UNREAD']}).execute()
            print("--- RESPOSTA ENVIADA E E-MAIL MARCADO COMO LIDO ---")

    except HttpError as error:
        print(f"Ocorreu um erro na API do Gmail: {error}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado no processamento: {e}")

def send_reply(service, to, subject, message_text, feedback_id):
    """Cria e envia um e-mail de resposta em formato HTML com links de feedback."""
    
    link_correto = f"https://chatbot-spam.duckdns.org/feedback/{feedback_id}/correto/"
    link_incorreto = f"https://chatbot-spam.duckdns.org/feedback/{feedback_id}/incorreto/"

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <p>{message_text.replace(chr(10), '<br>')}</p>
            <hr style="border: 0; border-top: 1px solid #ccc; margin: 20px 0;">
            <p style="font-size: 14px; color: #555;"><i>Minha análise foi útil?</i></p>
            <a href="{link_correto}" style="display: inline-block; padding: 10px 18px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px; margin-right: 10px; font-weight: bold;">👍 Sim, acertou</a>
            <a href="{link_incorreto}" style="display: inline-block; padding: 10px 18px; background-color: #dc3545; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">👎 Não, errou</a>
        </body>
    </html>
    """
    message = MIMEMultipart("alternative")
    message["subject"] = f"Re: {subject}"
    
    match = re.search(r'<(.+?)>', to)
    if match:
        message["to"] = match.group(1)
    else:
        message["to"] = to
        
    message.attach(MIMEText(html_content, "html"))
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {"raw": encoded_message}
    
    service.users().messages().send(userId="me", body=create_message).execute()

if __name__ == "__main__":
    print("Iniciando o bot de e-mail...")
    gmail_service = authenticate()
    print("Autenticação concluída. Iniciando verificação de e-mails...")
    while True:
        check_and_process_emails(gmail_service)
        time.sleep(CHECK_INTERVAL_SECONDS)