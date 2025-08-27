import json
import re
import requests
from django.conf import settings
from .constants import PONTUACAO_SPAM, PADROES_REGEX_SPAM, LIMITE_SPAM_NORMALIZADO

def calcular_percentual_maiusculas(texto: str) -> float:
    if not texto:
        return 0
    maiusculas = sum(1 for char in texto if char.isupper())
    letras = sum(1 for char in texto if char.isalpha())
    if letras == 0:
        return 0
    return (maiusculas / letras) * 100

def verificar_texto_spam(texto: str) -> dict:
    texto_lower = texto.lower()
    pontuacao_bruta = 0
    detalhes = []
    for palavra, pontos in PONTUACAO_SPAM.items():
        if palavra in texto_lower:
            ocorrencias = texto_lower.count(palavra)
            pontuacao_bruta += pontos * ocorrencias
            detalhes.append(f"Palavra: '{palavra}' ({ocorrencias}x) -> Pontos: +{pontos * ocorrencias}")
    for padrao, pontos in PADROES_REGEX_SPAM.items():
        if re.search(padrao, texto, re.IGNORECASE):
            pontuacao_bruta += pontos
            detalhes.append(f"Padrão: '{padrao}' -> Pontos: +{pontos}")
    percentual_caps = calcular_percentual_maiusculas(texto)
    if percentual_caps > 50:
        pontuacao_bruta += 8
        detalhes.append(f"ALERTA: Excesso de maiúsculas ({percentual_caps:.1f}%) -> Pontos: +8")
    achou_link = any("bit.ly" in d for d in detalhes)
    achou_termo_financeiro = any("dinheiro" in d or "investimento" in d or "ganhos" in d for d in detalhes)
    if achou_link and achou_termo_financeiro:
        pontuacao_bruta += 15
        detalhes.append("BÔNUS: Combinação de link suspeito com termo financeiro -> Pontos: +15")
    numero_de_palavras = len(texto.split())
    pontuacao_final_normalizada = 0
    if numero_de_palavras > 0:
        pontuacao_final_normalizada = (pontuacao_bruta / numero_de_palavras) * 10
    is_spam = pontuacao_final_normalizada >= LIMITE_SPAM_NORMALIZADO
    mensagem_final = f"Este texto parece ser {'spam' if is_spam else 'seguro'}. (Pontuação Final: {pontuacao_final_normalizada:.2f})"
    return {
        "spam": is_spam,
        "pontuacao": round(pontuacao_final_normalizada, 2),
        "mensagem": mensagem_final,
        "detalhes": detalhes
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
