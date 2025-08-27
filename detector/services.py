import re
import requests
import json
import os
from django.conf import settings
from .constants import PONTUACAO_SPAM, PADROES_REGEX_SPAM, LIMITE_SPAM_NORMALIZADO



def analisar_palavras_chave(texto_lower: str, detalhes: list) -> int:
    pontos = 0
    for palavra, valor in PONTUACAO_SPAM.items():
        if palavra in texto_lower:
            ocorrencias = texto_lower.count(palavra)
            pontos += valor * ocorrencias
            detalhes.append(f"Palavra-chave: '{palavra}' ({ocorrencias}x) -> +{valor * ocorrencias} pts")
    return pontos

def analisar_padroes_regex(texto: str, detalhes: list) -> int:
    pontos = 0
    for padrao, valor in PADROES_REGEX_SPAM.items():
        matches = re.findall(padrao, texto, re.IGNORECASE)
        if matches:
            ocorrencias = len(matches)
            pontos += valor * ocorrencias
            detalhes.append(f"Padrão Regex: '{padrao}' ({ocorrencias}x) -> +{valor * ocorrencias} pts")
    return pontos

def analisar_formato(texto: str, detalhes: list) -> int:
    pontos = 0
    letras = sum(1 for char in texto if char.isalpha())
    if not letras: return 0

    
    maiusculas = sum(1 for char in texto if char.isupper())
    percentual_caps = (maiusculas / letras) * 100
    if percentual_caps > 50:
        pontos += 8
        detalhes.append(f"ALERTA: Excesso de maiúsculas ({percentual_caps:.1f}%) -> +8 pts")
    
    
    especiais = sum(1 for char in texto if not char.isalnum() and not char.isspace())
    percentual_especiais = (especiais / len(texto)) * 100
    if percentual_especiais > 20: 
        pontos += 10
        detalhes.append(f"ALERTA: Excesso de caracteres especiais ({percentual_especiais:.1f}%) -> +10 pts")
        
    return pontos

def aplicar_bonus_combinacao(detalhes: list) -> int:
    pontos = 0
   
    achou_link = any("link" in d.lower() for d in detalhes)
    achou_termo_financeiro = any("dinheiro" in d.lower() or "pix" in d.lower() or "crédito" in d.lower() for d in detalhes)
    
    if achou_link and achou_termo_financeiro:
        pontos += 15
        detalhes.append("BÔNUS: Combinação de link com termo financeiro -> +15 pts")
    return pontos



def verificar_texto_spam(texto: str) -> dict:
    """
    Verifica se um texto é spam usando uma lógica modular e aprimorada.
    """
    detalhes = []
    texto_lower = texto.lower()
    
    
    pontuacao_bruta = 0
    pontuacao_bruta += analisar_palavras_chave(texto_lower, detalhes)
    pontuacao_bruta += analisar_padroes_regex(texto, detalhes)
    pontuacao_bruta += analisar_formato(texto, detalhes)
    pontuacao_bruta += aplicar_bonus_combinacao(detalhes)

    
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
