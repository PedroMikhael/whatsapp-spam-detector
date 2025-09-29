# autorizar_gmail.py
import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Define as permissões que o token terá
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def authorize():
    """Roda o fluxo de autorização local e cria o token.json."""
    print("Iniciando fluxo de autorização...")
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)

    # Esta função vai abrir o seu navegador local
    creds = flow.run_local_server(port=0)

    # Salva o token de autorização permanente
    with open("token.json", "w") as token:
        token.write(creds.to_json())

    print("\nArquivo 'token.json' criado com sucesso!")
    print("A autorização está completa. Você já pode enviar este arquivo para o servidor.")

if __name__ == "__main__":
    authorize()