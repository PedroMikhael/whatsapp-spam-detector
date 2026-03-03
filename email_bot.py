
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
from detector.services import analisar_com_IA
from detector.models import Feedback 


SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
CHECK_INTERVAL_SECONDS = 10 

def authenticate():
    """Autentica com a API do Gmail usando o fluxo manual para servidores."""
    creds = None
    
    token_json_env = os.environ.get("TOKEN_JSON")
    if token_json_env:
        try:
            import json
            token_data = json.loads(token_json_env)
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
            print("Token carregado de variável de ambiente.")
        except Exception as e:
            print(f"Erro ao carregar token de env: {e}")
    
    if not creds and os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Renovando token de acesso...")
            creds.refresh(Request())
            if not token_json_env:
                with open("token.json", "w") as token:
                    token.write(creds.to_json())
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
    """Verifica por e-mails não lidos, analisa com IA e responde."""
    try:
        results = service.users().messages().list(userId="me", labelIds=["INBOX"], q="is:unread").execute()
        messages = results.get("messages", [])

        if not messages:
            print(f"[{time.strftime('%d/%m/%Y %H:%M:%S')}] Nenhum e-mail novo. Próxima verificação em {CHECK_INTERVAL_SECONDS}s.")
            return

        print(f"\n[{time.strftime('%d/%m/%Y %H:%M:%S')}] 📬 {len(messages)} e-mail(s) não lido(s) encontrado(s)!")

        for message_info in messages:
            msg = service.users().messages().get(userId="me", id=message_info["id"], format='full').execute()

            headers = msg["payload"]["headers"]
            subject = next((header["value"] for header in headers if header["name"].lower() == "subject"), "Sem Assunto")
            sender = next((header["value"] for header in headers if header["name"].lower() == "from"), "Remetente Desconhecido")

            print(f"\n{'='*60}")
            print(f" NOVO E-MAIL RECEBIDO")
            print(f"   De: {sender}")
            print(f"   Assunto: {subject}")
            print(f"   ID: {message_info['id']}")
            print(f"{'='*60}")

            if "data" in msg["payload"]["body"]:
                email_body_encoded = msg["payload"]["body"]["data"]
            else:
                parts = msg["payload"].get("parts", [])
                part = next(iter(p for p in parts if p["mimeType"] == "text/plain"), None)
                email_body_encoded = part["body"]["data"] if part else ""

            email_body = base64.urlsafe_b64decode(email_body_encoded).decode("utf-8", errors='ignore')
            
            preview = email_body[:200].replace('\n', ' ')
            print(f"   Preview: {preview}...")

            print(f"\n Analisando com IA...")
            resultado_analise = analisar_com_IA(email_body)
            
            risk_level = resultado_analise.get('risk_level', 'INDETERMINADO')
            mensagem_de_resposta = resultado_analise["user_response"]
            
            print(f"    Classificação: {risk_level}")
            print(f"    Resposta: {mensagem_de_resposta[:150]}...")

            nova_analise = Feedback.objects.create(
                mensagem_original=email_body,
                remetente=sender,
                risco_ia=risk_level,
                analise_ia=str(resultado_analise.get('analysis_details', ''))
            )
            
            print(f"    Salvo no banco (Feedback ID: {nova_analise.id})")

            send_reply(service, sender, subject, mensagem_de_resposta, nova_analise.id, risk_level)

            service.users().messages().modify(userId="me", id=message_info["id"], body={'removeLabelIds': ['UNREAD']}).execute()
            print(f"    Resposta enviada e e-mail marcado como lido!")
            print(f"{'='*60}\n")

    except HttpError as error:
        print(f"[{time.strftime('%d/%m/%Y %H:%M:%S')}] ❌ Erro na API do Gmail: {error}")
    except Exception as e:
        print(f"[{time.strftime('%d/%m/%Y %H:%M:%S')}] ❌ Erro inesperado: {e}")


def _formatar_resposta_html(message_text):
    """Converte markdown básico (**bold**) e quebras de linha para HTML."""
    # Converter **texto** para <b>texto</b>
    texto_html = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', message_text)
    # Converter quebras de linha para <br>
    texto_html = texto_html.replace('\n', '<br>')
    return texto_html


def send_reply(service, to, subject, message_text, feedback_id, risk_level="INDETERMINADO"):
    """Cria e envia um e-mail de resposta em HTML com semáforo e links de feedback."""
    
    base_url = os.environ.get("FEEDBACK_BASE_URL", "https://pedromikhael-verificai.hf.space")
    link_correto = f"{base_url}/feedback/{feedback_id}/correto/"
    link_incorreto = f"{base_url}/feedback/{feedback_id}/incorreto/"

    # Mapear risk_level para imagem e cor
    semaforo_map = {
        "SAFE": {"img": "semaforoVerde.png", "cor": "#28a745"},
        "SUSPICIOUS": {"img": "semaforoAmarelo.png", "cor": "#ffc107"},
        "MALICIOUS": {"img": "semaforoVermelho.png", "cor": "#dc3545"},
    }
    semaforo = semaforo_map.get(risk_level, semaforo_map["SUSPICIOUS"])
    semaforo_url = f"https://huggingface.co/spaces/PedroMikhael/VerificAI/resolve/main/media/{semaforo['img']}"

    # Converter markdown bold para HTML
    resposta_html = _formatar_resposta_html(message_text)

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="text-align: center; margin-bottom: 20px;">
                <img src="{semaforo_url}" alt="Semáforo {risk_level}" style="width: 80px; height: auto;">
            </div>
            <p>{resposta_html}</p>
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
    print(f"\n{'='*60}")
    print(f" VerificAI Email Bot iniciado")
    print(f"   Intervalo de verificação: {CHECK_INTERVAL_SECONDS}s")
    print(f"{'='*60}\n")
    gmail_service = authenticate()
    print(f"[{time.strftime('%d/%m/%Y %H:%M:%S')}] ✅ Autenticação concluída. Monitorando e-mails...\n")
    while True:
        check_and_process_emails(gmail_service)
        time.sleep(CHECK_INTERVAL_SECONDS)