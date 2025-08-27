PONTUACAO_SPAM = {
    
    "renda extra": 8, "trabalhe em casa": 8, "liberdade financeira": 10,
    "dinheiro rápido": 10, "ganhe dinheiro": 8, "investimento seguro": 12,
    "ganhos garantidos": 12, "oportunidade única": 7, "crédito pré-aprovado": 10,
    "limpe seu nome": 9, "sem consulta": 8, "bitcoin": 5, "criptomoeda": 5,
    "lucro certo": 12, "multiplique seu dinheiro": 12,

    "promoção": 3, "oferta imperdível": 5, "compre agora": 4, "desconto exclusivo": 4,
    "liquidação total": 6, "queima de estoque": 6, "só hoje": 5, "última chance": 5,
    "não perca": 4, "tempo limitado": 6, "vagas limitadas": 7, "exclusivo": 3, "grátis": 4,
    "brinde": 3, "amostra grátis": 4, "100% gratuito": 5,

    
    "urgente": 7, "importante": 3, "parabéns": 6, "você foi sorteado": 10,
    "você ganhou": 10, "prêmio": 8, "ganhador": 8, "clique aqui": 5,
    "clique já": 6, "acesse agora": 5, "visite nosso site": 3,

   
    "emagreça": 8, "perca peso": 8, "remédio": 4, "cura milagrosa": 15,
    "rejuvenescimento": 9, "aumento de": 7, "desempenho sexual": 9, "viagra": 10,

   
    "confidencial": 8, "sua conta": 7, "verifique sua conta": 15,
    "senha expirada": 15, "fatura pendente": 12, "boleto": 4, "aviso importante": 7,

   
    "marketing multinível": 10, "mlm": 10, "isso não é spam": 15
}

PADROES_REGEX_SPAM = {
    r"(https?://\S*)": 5,  
    r"(bit\.ly|tinyurl\.com|goo\.gl|cutt\.ly|is\.gd|t\.co)": 15, # 
    r"[\!¡\?¿]{3,}": 7,
    r"\b([A-Z]\.){3,}\b": 12, 
    r"\b[A-Z\s]{5,}\b": 10, 
    r"(?i)\b\w*[@$!#%&]\w*\b": 7, 
    r"(\(?\d{2}\)?\s?)?(\d{5}\-?\d{4})": 3, 
    r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b": 8, 
    r"pix|transferência|depósito": 8, 
    r"urgente|imediato|agora": 7,
}



LIMITE_SPAM_NORMALIZADO = 11.5