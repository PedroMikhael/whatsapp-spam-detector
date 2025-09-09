
import os
import requests
import json
import re
from django.conf import settings
import google.generativeai as genai

# Configuração da API do Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

def verificar_link_com_safe_browsing(link: str) -> str:
    """
    Verifica uma URL com a API Google Safe Browsing v4.
    Retorna uma string descrevendo o status do link.
    """
    url_api = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    api_key = settings.SAFE_BROWSING_API_KEY
    
    payload = {
        "client": {"clientId": "spamapiproject", "clientVersion": "1.0.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": link}]
        }
    }
    params = {'key': api_key}

    try:
        response = requests.post(url_api, params=params, json=payload)
        response.raise_for_status()
        data = response.json()
        if 'matches' in data:
            threat_type = data['matches'][0]['threatType']
            print(f"SAFE BROWSING: Ameaça encontrada no link '{link}': {threat_type}")
            return f"PERIGOSO (Ameaça detectada: {threat_type})"
        else:
            print(f"SAFE BROWSING: Nenhuma ameaça encontrada para o link '{link}'.")
            return "SEGURO"
    except requests.exceptions.RequestException as e:
        print(f"Erro ao chamar a API Safe Browsing: {e}")
        return "INDETERMINADO (Falha na verificação)"

def analisar_com_gemini(texto: str) -> dict:
    """
    Analisa uma mensagem com a IA Gemini usando um prompt avançado e estruturado.
    """
    links_encontrados = re.findall(r'(https?://\S+)', texto)
    resultado_safe_browsing = "Nenhum link na mensagem."

    if links_encontrados:
        primeiro_link = links_encontrados[0]
        resultado_safe_browsing = verificar_link_com_safe_browsing(primeiro_link)

    
    prompt = f"""
    Você é um sistema de cibersegurança autônomo, o "Guardião Digital", especializado em detectar spam e phishing em mensagens de WhatsApp em português do Brasil. Sua missão é proteger o usuário e, se a mensagem for segura, conversar normalmente.

    **CONTEXTO PARA ANÁLISE:**
    - MENSAGEM DO USUÁRIO: "{texto}"
    - RESULTADO DA ANÁLISE DE LINK (Google Safe Browsing): "{resultado_safe_browsing}"

    **INSTRUÇÕES:**
    1.  **ANÁLISE METÓDICA:** Baseado no CONTEXTO, analise os seguintes vetores: Análise de URL (encurtadores, domínios suspeitos), Engenharia Social (urgência, ganância), Personificação de Marca e Linguagem/Formatação. Se o resultado da análise de link for 'PERIGOSO', a mensagem é automaticamente maliciosa.
    2.  **AVALIAÇÃO DE RISCO:** Classifique o risco como 'SAFE', 'SUSPICIOUS', ou 'MALICIOUS'.
    3.  **FORMULAÇÃO DA RESPOSTA:** Crie uma resposta amigável e protetora para o usuário.

    **FORMATO DE SAÍDA (OBRIGATÓRIO):**
    Responda APENAS com um objeto JSON válido, sem nenhum texto ou formatação extra. A estrutura é:
    {{
      "risk_level": "SAFE, SUSPICIOUS, ou MALICIOUS",
      "analysis_details": ["Um item da lista para cada ponto importante da sua análise.", "Seja específico."],
      "user_response": "O texto exato para ser enviado de volta ao usuário."
    }}

    **EXEMPLO (SPAM):**
    {{
      "risk_level": "MALICIOUS",
      "analysis_details": ["Usa tática de ganância (prêmio) e urgência.", "Contém um link encurtado suspeito."],
      "user_response": "🚨 Cuidado! Esta mensagem tem características de um golpe. Ela usa um tom de urgência e um link suspeito. Recomendo não clicar e apagar a mensagem. Fique seguro! 👍"
    }}

    **EXEMPLO (SEGURO):**
    {{
      "risk_level": "SAFE",
      "analysis_details": ["A mensagem é uma saudação simples sem indicadores de risco."],
      "user_response": "Olá! Este é um projeto acadêmico para detecção de spam. Como posso te ajudar?"
    }}
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("`", "").replace("json", "")
        resultado_json = json.loads(cleaned_response)

        if "risk_level" not in resultado_json or "user_response" not in resultado_json:
             raise ValueError("A resposta da IA não contém as chaves esperadas.")

        print("Análise do Gemini (V4.1) recebida com sucesso:", resultado_json)
        return resultado_json

    except Exception as e:
        print(f"Erro ao chamar a API do Gemini: {e}")
        return {
            "risk_level": "SAFE",
            "analysis_details": [f"Erro interno ao processar a mensagem com a IA: {e}"],
            "user_response": "Desculpe, não consegui processar sua mensagem neste momento. "
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
