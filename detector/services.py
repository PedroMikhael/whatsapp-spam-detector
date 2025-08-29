import re
import requests
import json
import os
from django.conf import settings
from detector.constants import CATEGORIAS_SPAM, PADROES_REGEX_SPAM, LIMITE_SPAM_NORMALIZADO



def analisar_categorias(texto_lower: str, detalhes: list) -> int:
    pontos = 0
    categorias_detectadas = set()
    
    for categoria, info in CATEGORIAS_SPAM.items():
        for palavra in info["palavras"]:
            if palavra in texto_lower:
                ocorrencias = texto_lower.count(palavra)
                pontos += info["peso"] * ocorrencias
                detalhes.append(f"[{categoria.upper()}] Palavra detectada: '{palavra}' ({ocorrencias}x)")
                categorias_detectadas.add(categoria)
    
    # Bônus por múltiplas categorias
    if len(categorias_detectadas) > 1:
        bonus = 5 * (len(categorias_detectadas) - 1)
        pontos += bonus
        detalhes.append(f"BÔNUS: Múltiplas categorias ({len(categorias_detectadas)}) -> +{bonus} pts")
    
    return pontos

# -----------------------------
# Regex suspeitos
# -----------------------------
def analisar_regex(texto: str, detalhes: list) -> int:
    pontos = 0
    for padrao, peso in PADROES_REGEX_SPAM.items():
        matches = re.findall(padrao, texto, re.IGNORECASE)
        if matches:
            pontos += peso * len(matches)
            detalhes.append(f"Padrão suspeito: '{padrao}' ({len(matches)}x)")
    return pontos

# -----------------------------
# Formato e estilo
# -----------------------------
def analisar_formato(texto: str, detalhes: list) -> int:
    pontos = 0
    letras = sum(c.isalpha() for c in texto)
    if letras == 0:
        return 0

    maiusculas = sum(c.isupper() for c in texto)
    percentual_caps = (maiusculas / letras) * 100
    if percentual_caps > 50:
        pontos += 8
        detalhes.append(f"Excesso de maiúsculas ({percentual_caps:.1f}%)")

    especiais = sum(1 for c in texto if not c.isalnum() and not c.isspace())
    percentual_especiais = (especiais / len(texto)) * 100
    if percentual_especiais > 20:
        pontos += 10
        detalhes.append(f"Excesso de caracteres especiais ({percentual_especiais:.1f}%)")

    emojis = re.findall(r"[^\w\s,]", texto)
    if len(emojis) > 5:
        pontos += 5
        detalhes.append(f"Excesso de emojis/símbolos ({len(emojis)})")

    return pontos

# -----------------------------
# Bônus combinatório
# -----------------------------
def aplicar_bonus_combinacao(detalhes: list) -> int:
    pontos = 0
    achou_link = any("https" in d.lower() for d in detalhes)
    achou_financeiro = any(word in d.lower() for d in detalhes for word in ["dinheiro", "pix", "crédito", "transferência", "depósito"])
    achou_urgencia = any(word in d.lower() for d in detalhes for word in ["urgente", "imediato", "agora"])
    
    if achou_link and achou_financeiro:
        pontos += 20
        detalhes.append("Combinação: link + termo financeiro")
    if achou_financeiro and achou_urgencia:
        pontos += 15
        detalhes.append("Combinação: termo financeiro + urgência")
    return pontos

# -----------------------------
# Função principal “ML fake”
# -----------------------------
def verificar_texto_spam(texto: str) -> dict:
    detalhes = []
    texto_lower = texto.lower()

    pontos = 0
    pontos += analisar_categorias(texto_lower, detalhes)
    pontos += analisar_regex(texto, detalhes)
    pontos += analisar_formato(texto, detalhes)
    pontos += aplicar_bonus_combinacao(detalhes)

    numero_palavras = len(texto.split())
    pontuacao_normalizada = (pontos / numero_palavras) * 10 if numero_palavras > 0 else pontos

    # Convertendo para pseudo-probabilidade de 0 a 100%
    probabilidade_spam = min(round(pontuacao_normalizada * 2), 100)

    # Nível de risco
    if probabilidade_spam >= 75:
        nivel_risco = "Alto risco"
    elif probabilidade_spam >= 40:
        nivel_risco = "Médio risco"
    else:
        nivel_risco = "Baixo risco"

    # Mensagem final estilosa
    if probabilidade_spam >= 50:
        mensagem_final = f"🚨 ALERTA: Esta mensagem parece ser SPAM! ({nivel_risco})"
    else:
        mensagem_final = f"✅ Esta mensagem parece ser segura. ({nivel_risco})"

    return {
        "spam": probabilidade_spam >= 50,
        "probabilidade": probabilidade_spam,
        "nivel_risco": nivel_risco,
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
