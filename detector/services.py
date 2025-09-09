# dentro de detector/services.py

# ... (imports no topo do arquivo) ...
import os
import requests
import json
import re
from django.conf import settings
import google.generativeai as genai

genai.configure(api_key=settings.GEMINI_API_KEY)

def analisar_com_gemini(texto: str) -> dict:
    """
    Analisa uma mensagem com a IA Gemini para atuar como um "Guardião Digital".
    """
    
    links_encontrados = re.findall(r'(https?://\S+)', texto)
    primeiro_link = links_encontrados[0] if links_encontrados else "Nenhum link encontrado."

    prompt = f"""
    Você é um sistema de cibersegurança autônomo, inspirado na abordagem AutoML do AutoPhish, e atua como um assistente de IA amigável chamado "Guardião Digital".
    Sua especialidade é detectar spam, phishing e golpes em mensagens de texto do WhatsApp em português do Brasil.

    Sua missão é dupla:
    1.  **PROTEGER (Prioridade Máxima):** Sua análise deve ser metódica e baseada em características (features) estruturais e de engenharia social.
    2.  **CONVERSAR (Se Seguro):** Se a mensagem for 100% segura (uma saudação, pergunta legítima), sua missão é agir como um assistente prestativo e responder de forma natural.

    ---
    **VETORES DE ANÁLISE DE AMEAÇAS (CHECKLIST OBRIGATÓRIO):**

    Analise a mensagem abaixo focando nos seguintes vetores de ataque:
    1.  **Análise de URL (se houver):** Verifique a estrutura do link: "{primeiro_link}". Procure por encurtadores (bit.ly, tinyurl), TLDs suspeitos (.xyz, .club), subdomínios excessivos, ou tentativas de imitar domínios famosos (ex: `banco-ltaú.com`).
    2.  **Engenharia Social:** Identifique táticas de **urgência** ("última chance!", "só hoje"), **autoridade** ("aviso importante do seu banco"), **escassez** ("vagas limitadas") ou **ganância** ("você ganhou", "dinheiro fácil").
    3.  **Personificação de Marca:** A mensagem tenta se passar por uma empresa conhecida (bancos, lojas, governo)?
    4.  **Linguagem e Formatação:** Procure por erros gramaticais grosseiros, formatação estranha (espaços entre letras), ou uso excessivo de emojis e pontos de exclamação.
    ---

    **FORMATO DA RESPOSTA (OBRIGATÓRIO):**
    Sua resposta deve ser SEMPRE e APENAS um objeto JSON, sem nenhum texto ou formatação extra.
    A estrutura do JSON deve ser a seguinte:
    {{
      "spam": boolean,
      "analise": "Sua análise técnica e detalhada em bullet points, baseada nos vetores de ataque. Seja específico.",
      "resposta_usuario": "O texto exato, em português, com tom amigável e protetor, para ser enviado de volta ao usuário."
    }}

    **EXEMPLO DE RESPOSTA (SPAM):**
    ```json
    {{
      "spam": true,
      "analise": "- Engenharia Social: Utiliza tática de ganância ('prêmio') e urgência ('agora mesmo').\n- Análise de URL: Contém um link encurtado (`bit.ly`), o que é um forte indicador de risco pois oculta o destino final.",
      "resposta_usuario": " Cuidado! Esta mensagem tem características de um golpe. Ela usa um tom de urgência e um link suspeito para te pressionar a agir. O ideal é não clicar e apagar a mensagem. Fique seguro! "
    }}
    ```
    
    **EXEMPLO DE RESPOSTA (SEGURA):**
    ```json
    {{
      "spam": false,
      "analise": "- A mensagem é uma pergunta direta e não contém nenhum dos vetores de ataque analisados.",
      "resposta_usuario": "Olá! Este é um projeto acadêmico para detecção de spam, mas fico feliz em ajudar se tiver alguma outra pergunta. "
    }}
    ```
    
    ---
    **MENSAGEM REAL PARA ANÁLISE:**
    "{texto}"
    """
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("`", "").replace("json", "")
        resultado_json = json.loads(cleaned_response)
        
        if "spam" not in resultado_json or "resposta_usuario" not in resultado_json:
             raise ValueError("A resposta da IA não contém as chaves esperadas.")

        print("Análise do Gemini (V3) recebida com sucesso:", resultado_json)
        return resultado_json

    except Exception as e:
        print(f"Erro ao chamar a API do Gemini: {e}")
        return {
            "spam": False,
            "analise": f"Erro interno ao processar a mensagem com a IA: {e}",
            "resposta_usuario": "Desculpe, não consegui processar sua mensagem neste momento. "
        }

def enviar_mensagem_whatsapp(numero_destinatario: str, mensagem: str):
    """
    Envia uma mensagem de texto para um número de WhatsApp usando a API da Meta.
    """
    
    print("\n--- TENTANDO ENVIAR MENSAGEM DE RESPOSTA ---")

    
    access_token = settings.WHATSAPP_ACCESS_TOKEN
    phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID

    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    data = {
        "messaging_product": "whatsapp",
        "to": numero_destinatario,
        "type": "text",
        "text": {"body": mensagem},
    }

   
    print(f"URL de Destino: {url}")
    print(f"Token de Acesso Utilizado: ...{access_token[-4:]}") # 
    print(f"Payload (Dados Enviados): {json.dumps(data, indent=2)}")
   

    try:
        response = requests.post(url, headers=headers, json=data)
        
        print(f"Resposta da Meta - Status: {response.status_code}")
        print(f"Resposta da Meta - Conteúdo: {response.text}")
        response.raise_for_status()

        return True, response.json()

    except requests.exceptions.RequestException as e:
        print(f"Erro CRÍTICO na requisição: {e}")
        return False, str(e)
