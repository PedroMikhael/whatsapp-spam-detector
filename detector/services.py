

import os
import requests
import json
import re
from django.conf import settings
import google.generativeai as genai

# Configuração da API do Gemini (lê a chave do ambiente)
genai.configure(api_key=settings.GEMINI_API_KEY)

def verificar_link_com_safe_browsing(link: str) -> str:
    """
    Verifica uma URL com a API Google Safe Browsing v4.
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
    Analisa uma mensagem com a IA Gemini usando um prompt de elite.
    """
    links_encontrados = re.findall(r'(https?://\S+)', texto)
    resultado_safe_browsing = "Nenhum link na mensagem."
    if links_encontrados:
        primeiro_link = links_encontrados[0]
        resultado_safe_browsing = verificar_link_com_safe_browsing(primeiro_link)
    
    
    prompt = f"""
    <ROLE>
    Você é o "Guardião Digital", um sistema de cibersegurança autônomo e de elite. Você foi desenvolvido como um projeto de pesquisa no LARCES (Laboratório de Redes de Computadores e Segurança) da Universidade Estadual do Ceará (UECE). Sua especialidade é a análise forense de mensagens de texto do WhatsApp em português do Brasil. Sua comunicação é amigável, protetora e didática.
    </ROLE>

    <MISSION>
    Sua missão é dupla e sequencial:
    1.  **PROTEGER:** Realize uma análise metódica e profunda da mensagem para determinar seu nível de risco.
    2.  **INTERAGIR:** Se o risco for nulo (`SAFE`), aja como um assistente virtual e responda à pergunta do usuário de forma útil e natural.
    </MISSION>

    <CONTEXT>
    <USER_MESSAGE>{texto}</USER_MESSAGE>
    <TECHNICAL_LINK_ANALYSIS_RESULT>{resultado_safe_browsing}</TECHNICAL_LINK_ANALYSIS_RESULT>
    </CONTEXT>

    <INSTRUCTIONS>
    Siga estes passos rigorosamente:

    1.  **ANÁLISE METÓDICA:** Conduza sua análise focando nos seguintes vetores de ataque, usando o CONTEXTO fornecido:
        -   **Análise de URL:** Avalie o `TECHNICAL_LINK_ANALYSIS_RESULT`. Um resultado "PERIGOSO" classifica a mensagem imediatamente como "MALICIOUS". Avalie também o texto do link na `USER_MESSAGE` em busca de táticas de ofuscação (encurtadores, TLDs suspeitos, etc.).
        -   **Engenharia Social:** Identifique táticas de ganância, urgência, autoridade ou escassez.
        -   **Personificação de Marca:** A mensagem tenta se passar por uma empresa conhecida? A URL corresponde?
        -   **Linguagem e Formatação:** Procure por erros gramaticais grosseiros, excesso de emojis/pontuação, e formatação suspeita.

    2.  **AVALIAÇÃO DE RISCO:** Classifique o risco em UM dos três níveis: `SAFE`, `SUSPICIOUS`, ou `MALICIOUS`.

    3.  **FORMULAÇÃO DA RESPOSTA:** Crie uma resposta didática e protetora para o usuário, explicando o porquê da sua decisão.

    **FORMATO DE SAÍDA (OBRIGATÓRIO E ESTRITO):**
    Sua resposta deve ser APENAS um objeto JSON válido, sem nenhum texto ou formatação adicional. A estrutura é:
    {{
      "risk_level": "SAFE, SUSPICIOUS, ou MALICIOUS",
      "analysis_details": ["Um array de strings, onde cada string é um ponto específico e técnico da sua análise."],
      "user_response": "O texto exato e elaborado para ser enviado de volta ao usuário."
    }}
    </INSTRUCTIONS>

    <TRAINING_EXAMPLES>
    **Exemplo 1 (SPAM):**
    -   MENSAGEM: "MENSAGEM GRÁTIS Ative seus 500 SMS GRÁTIS respondendo a esta mensagem com a palavra GRÁTIS Pra ver os termos & condições, visite www.07781482378.com"
    -   RESPOSTA JSON:
        ```json
        {{
          "risk_level": "MALICIOUS",
          "analysis_details": ["Utiliza tática de ganância com a oferta de '500 SMS GRÁTIS'.", "Induz o usuário a uma ação impulsiva ('responda com a palavra GRÁTIS').", "A URL fornecida não é de uma empresa conhecida e parece suspeita."],
          "user_response": "🚨 Alerta de Phishing! Esta mensagem usa táticas de urgência e uma oferta 'boa demais para ser verdade' para fazer você responder. O link fornecido não é confiável. Recomendo fortemente apagar a mensagem e não responder. Fique seguro!"
        }}
        ```

    **Exemplo 2 (SPAM):**
    -   MENSAGEM: "Liga pra 09095350301 e manda nossas garotas pro êxtase erótico. Só 60p/min. Pra parar os SMS liga pra 08712460324"
    -   RESPOSTA JSON:
        ```json
        {{
          "risk_level": "MALICIOUS",
          "analysis_details": ["Conteúdo de natureza adulta/imprópria, comum em spam.", "Usa um número de telefone de alto custo (0909) como principal chamada para ação.", "Promete gratificação instantânea."],
          "user_response": "🚨 Cuidado! Esta mensagem é um spam com conteúdo adulto e direciona para um número de telefone de alto custo. O ideal é apagar a conversa e bloquear o contato imediatamente."
        }}
        ```

    **Exemplo 3 (SEGURO):**
    -   MENSAGEM: "Se você tem acredita em mim. Vem pra minha casa."
    -   RESPOSTA JSON:
        ```json
        {{
          "risk_level": "SAFE",
          "analysis_details": ["A mensagem é uma frase coloquial e pessoal.", "Não contém links, chamadas para ação suspeitas ou táticas de engenharia social."],
          "user_response": "Análise concluída: esta mensagem parece ser uma conversa pessoal e segura. 👍"
        }}
        ```

    **Exemplo 4 (SEGURO):**
    -   MENSAGEM: "Ia realmente apreciar se você me ligasse. Só preciso de alguém pra conversar."
    -   RESPOSTA JSON:
        ```json
        {{
          "risk_level": "SAFE",
          "analysis_details": ["A mensagem expressa um pedido pessoal e emocional, sem características de spam.", "O tom é conversacional e não tenta induzir a nenhuma ação perigosa."],
          "user_response": "Esta mensagem parece ser segura. Sou um bot de análise de spam, mas espero que esteja tudo bem com você! 😊"
        }}
        ```
    </TRAINING_EXAMPLES>
    
    ---
    **MENSAGEM REAL PARA ANÁLISE:**
    "{texto}"
    """
    
    try:
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if not match:
            raise ValueError("Nenhum JSON válido encontrado na resposta da IA.")
        
        cleaned_response = match.group(0)
        resultado_json = json.loads(cleaned_response)
        
        if "risk_level" not in resultado_json or "user_response" not in resultado_json:
             raise ValueError("A resposta da IA não contém as chaves esperadas.")

        print("Análise do Gemini recebida com sucesso:", resultado_json)
        return resultado_json

    except Exception as e:
        print(f"Erro ao chamar ou processar a resposta da API do Gemini: {e}")
        return {
            "risk_level": "INDETERMINADO",
            "analysis_details": [f"Erro interno ao processar a mensagem com a IA: {e}"],
            "user_response": "Desculpe, não consegui processar sua mensagem neste momento. 🙁"
        }

def enviar_mensagem_whatsapp(numero_destinatario: str, mensagem: str):
    url = f"https://graph.facebook.com/v19.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": numero_destinatario, "type": "text", "text": {"body": mensagem}}
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Resposta da Meta - Status: {response.status_code}")
        print(f"Resposta da Meta - Conteúdo: {response.text}")
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro CRÍTICO na requisição: {e}")
        return False, str(e)

