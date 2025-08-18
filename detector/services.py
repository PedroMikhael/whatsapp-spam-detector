from .constants import PALAVRAS_SPAM, MENSAGEM_SPAM, MENSAGEM_LEGAL

def verificar_texto_spam(texto: str) -> dict:
    texto_lower = texto.lower()
    is_spam = any(p in texto_lower for p in PALAVRAS_SPAM)
    return {
        "spam": is_spam,
        "mensagem": MENSAGEM_SPAM if is_spam else MENSAGEM_LEGAL
    }
