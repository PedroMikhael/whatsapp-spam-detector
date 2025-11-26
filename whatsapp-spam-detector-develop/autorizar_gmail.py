# autorizar_gmail.py
import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def authorize():
    print("Iniciando fluxo de autorização AUTOMÁTICO...")

    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    
    # 🔥 ESTE MÉTODO AUTOMATIZA O PROCESSO — FUNCIONA EM "app para desktop"
    creds = flow.run_local_server(port=8080, prompt='consent')

    # Salva o token
    with open("token.json", "w") as token:
        token.write(creds.to_json())

    print("\n✅ Autorização concluída e 'token.json' criado com sucesso!")

if __name__ == "__main__":
    authorize()
