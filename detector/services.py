
import re
from .constants import PONTUACAO_SPAM, PADROES_REGEX_SPAM, LIMITE_SPAM_NORMALIZADO

def calcular_percentual_maiusculas(texto: str) -> float:
    """Função auxiliar para calcular a porcentagem de letras maiúsculas."""
    if not texto:
        return 0
    maiusculas = sum(1 for char in texto if char.isupper())
    letras = sum(1 for char in texto if char.isalpha())
    if letras == 0:
        return 0
    return (maiusculas / letras) * 100

def verificar_texto_spam(texto: str) -> dict:
    """
    Verifica se um texto é spam usando uma lógica avançada de pontuação,
    bônus por combinação, análise de maiúsculas e normalização.
    """
    texto_lower = texto.lower()
    pontuacao_bruta = 0
    detalhes = []

    # 1. Calcula pontuação pelas palavras-chave
    for palavra, pontos in PONTUACAO_SPAM.items():
        if palavra in texto_lower:
            ocorrencias = texto_lower.count(palavra)
            pontuacao_bruta += pontos * ocorrencias
            detalhes.append(f"Palavra: '{palavra}' ({ocorrencias}x) -> Pontos: +{pontos * ocorrencias}")

    # 2. Calcula pontuação pelos padrões regex
    for padrao, pontos in PADROES_REGEX_SPAM.items():
        if re.search(padrao, texto, re.IGNORECASE):
            pontuacao_bruta += pontos
            detalhes.append(f"Padrão: '{padrao}' -> Pontos: +{pontos}")

    # 3. Análise de Excesso de Letras Maiúsculas
    percentual_caps = calcular_percentual_maiusculas(texto)
    if percentual_caps > 50: # Se mais de 50% das letras forem maiúsculas
        pontuacao_bruta += 8
        detalhes.append(f"ALERTA: Excesso de maiúsculas ({percentual_caps:.1f}%) -> Pontos: +8")

    # 4. Bônus por Combinação de Fatores de Risco
    achou_link = any("bit.ly" in d for d in detalhes)
    achou_termo_financeiro = any("dinheiro" in d or "investimento" in d or "ganhos" in d for d in detalhes)

    if achou_link and achou_termo_financeiro:
        pontuacao_bruta += 15
        detalhes.append("BÔNUS: Combinação de link suspeito com termo financeiro -> Pontos: +15")

    # 5. Normalização da Pontuação (Cálculo Final)
    numero_de_palavras = len(texto.split())
    pontuacao_final_normalizada = 0
    if numero_de_palavras > 0:
        pontuacao_final_normalizada = (pontuacao_bruta / numero_de_palavras) * 10
    
    # 6. Verificação Final
    is_spam = pontuacao_final_normalizada >= LIMITE_SPAM_NORMALIZADO
    
    mensagem_final = f"Este texto parece ser {'spam' if is_spam else 'seguro'}. (Pontuação Final: {pontuacao_final_normalizada:.2f})"

    # 7. Retorna o dicionário completo
    return {
        "spam": is_spam,
        "pontuacao": round(pontuacao_final_normalizada, 2),
        "mensagem": mensagem_final,
        "detalhes": detalhes
    }