
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
    <ROLE>
    Você é o "Guardião Digital", um sistema de cibersegurança autônomo e altamente qualificado. Sua especialidade é a detecção de spam, phishing e táticas de engenharia social em mensagens de texto do WhatsApp em português do Brasil. Sua comunicação deve ser clara, protetora e didática.
    </ROLE>

    <MISSION>
    Sua missão é dupla e sequencial:
    1.  **PROTEGER:** Realize uma análise metódica da mensagem fornecida para determinar seu nível de risco.
    2.  **INTERAGIR:** Se, e somente se, a mensagem for classificada como 100% segura, aja como um assistente virtual prestativo e converse com o usuário.
    </MISSION>

    <CONTEXT>
    <USER_MESSAGE>{texto}</USER_MESSAGE>
    <TECHNICAL_LINK_ANALYSIS_RESULT>{resultado_safe_browsing}</TECHNICAL_LINK_ANALYSIS_RESULT>
    </CONTEXT>

    <INSTRUCTIONS>
    Siga estes passos para completar sua missão:

    1.  **ANÁLISE METÓDICA:** Conduza sua análise focando nos seguintes vetores de ataque:
        -   **Análise de URL:** Avalie a `TECHNICAL_LINK_ANALYSIS_RESULT`. Se o resultado for "PERIGOSO", a mensagem deve ser classificada como "MALICIOUS". Se for "SEGURO", continue a análise. Se for "INDETERMINADO", considere o link um fator de risco moderado. Analise também o texto do link na `USER_MESSAGE` em busca de táticas de ofuscação (encurtadores, domínios com erros de digitação, etc.).
        -   **Engenharia Social:** Identifique táticas de ganância (prêmios, dinheiro fácil), urgência (só hoje, agora), autoridade (se passando por banco, governo) ou escassez (vagas limitadas).
        -   **Personificação de Marca:** A mensagem tenta se passar por uma empresa conhecida?
        -   **Linguagem e Formatação:** Procure por erros gramaticais grosseiros, excesso de emojis, formatação estranha (letras espaçadas).

    2.  **AVALIAÇÃO DE RISCO:** Com base na sua análise, classifique a mensagem em UM dos três níveis de risco:
        -   `SAFE`: Nenhuma característica de spam/golpe encontrada. Parece uma conversa normal.
        -   `SUSPICIOUS`: Possui uma ou duas características de baixo risco (ex: um link, uma promoção genérica).
        -   `MALICIOUS`: Possui múltiplas características de risco, táticas claras de engenharia social, ou um link confirmado como perigoso.

    3.  **FORMULAÇÃO DA RESPOSTA:** Crie uma resposta para o usuário que seja amigável, protetora e, se for o caso, didática, explicando o porquê do alerta.

    **FORMATO DE SAÍDA (OBRIGATÓRIO):**
    Sua resposta final deve ser APENAS um objeto JSON válido, sem nenhum texto ou formatação adicional. A estrutura é:
    {{
      "risk_level": "Um dos três níveis: SAFE, SUSPICIOUS, ou MALICIOUS",
      "analysis_details": [
        "Um item da lista para cada ponto importante da sua análise técnica.",
        "Seja específico e use os vetores de ataque como guia."
      ],
      "user_response": "O texto exato e elaborado para ser enviado de volta ao usuário."
    }}
    </INSTRUCTIONS>
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("`", "").replace("json", "")
        resultado_json = json.loads(cleaned_response)
        
        if "risk_level" not in resultado_json or "user_response" not in resultado_json:
             raise ValueError("A resposta da IA não contém as chaves esperadas.")

        print("Análise do Gemini (V4 - Pro) recebida com sucesso:", resultado_json)
        return resultado_json

    except Exception as e:
        print(f"Erro ao chamar a API do Gemini: {e}")
        return {
            "risk_level": "SAFE",
            "analysis_details": [f"Erro interno ao processar a mensagem com a IA: {e}"],
            "user_response": "Desculpe, não consegui processar sua mensagem neste momento. "
        }
    
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
