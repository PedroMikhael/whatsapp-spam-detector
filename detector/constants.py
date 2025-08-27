CATEGORIAS_SPAM = {
    "financeiro": {
        "palavras": ["renda extra", "trabalhe em casa", "liberdade financeira", "dinheiro rápido",
                     "ganhe dinheiro", "investimento seguro", "ganhos garantidos", "pix",
                     "transferência", "depósito", "crédito", "limpe seu nome"],
        "peso": 10
    },
    "promocao": {
        "palavras": ["promoção", "oferta imperdível", "compre agora", "desconto exclusivo",
                     "liquidação total", "queima de estoque", "só hoje", "última chance",
                     "não perca", "vagas limitadas", "exclusivo", "grátis", "brinde"],
        "peso": 6
    },
    "urgencia": {
        "palavras": ["urgente", "imediato", "agora", "importante", "alerta"],
        "peso": 8
    },
    "saude": {
        "palavras": ["emagreça", "perca peso", "cura milagrosa", "rejuvenescimento",
                     "viagra", "aumento de", "desempenho sexual", "remédio"],
        "peso": 12
    },
    "seguranca": {
        "palavras": ["confidencial", "verifique sua conta", "senha expirada", "fatura pendente",
                     "boleto", "aviso importante", "marketing multinível", "mlm"],
        "peso": 9
    },
}

# Regex suspeitos
PADROES_REGEX_SPAM = {
    r"https?://\S+": 5,  
    r"\b(bit\.ly|tinyurl\.com|goo\.gl|cutt\.ly|is\.gd|t\.co)\b": 15,  
    r"[\!¡\?¿]{3,}": 7,  
    r"\b([A-Z]\.){3,}\b": 12,  
    r"\b[A-Z\s]{5,}\b": 10,  
    r"\w*[@$!#%&]\w*": 7,  
    r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b": 8,  
    r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b": 8,  
    r"\b\d{5}-?\d{4}\b": 3,  
}



LIMITE_SPAM_NORMALIZADO = 12