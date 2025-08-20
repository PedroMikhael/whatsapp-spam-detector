PONTUACAO_SPAM = {
    # Financeiro / Dinheiro Fácil (Alta Pontuação)
    "renda extra": 8, "trabalhe em casa": 8, "liberdade financeira": 10,
    "dinheiro rápido": 10, "ganhe dinheiro": 8, "investimento seguro": 12,
    "ganhos garantidos": 12, "oportunidade única": 7, "crédito pré-aprovado": 10,
    "limpe seu nome": 9, "sem consulta": 8, "bitcoin": 5, "criptomoeda": 5,
    "lucro certo": 12, "multiplique seu dinheiro": 12,

    # Ofertas e Promoções Agressivas (Média Pontuação)
    "promoção": 3, "oferta imperdível": 5, "compre agora": 4, "desconto exclusivo": 4,
    "liquidação total": 6, "queima de estoque": 6, "só hoje": 5, "última chance": 5,
    "não perca": 4, "tempo limitado": 6, "vagas limitadas": 7, "exclusivo": 3, "grátis": 4,
    "brinde": 3, "amostra grátis": 4, "100% gratuito": 5,

    # Urgência e Prêmios (Alta Pontuação)
    "urgente": 7, "importante": 3, "parabéns": 6, "você foi sorteado": 10,
    "você ganhou": 10, "prêmio": 8, "ganhador": 8, "clique aqui": 5,
    "clique já": 6, "acesse agora": 5, "visite nosso site": 3,

    # Saúde e Produtos "Milagrosos" (Alta Pontuação)
    "emagreça": 8, "perca peso": 8, "remédio": 4, "cura milagrosa": 15,
    "rejuvenescimento": 9, "aumento de": 7, "desempenho sexual": 9, "viagra": 10,

    # Phishing e Assuntos Confidenciais (Altíssima Pontuação)
    "confidencial": 8, "sua conta": 7, "verifique sua conta": 15,
    "senha expirada": 15, "fatura pendente": 12, "boleto": 4, "aviso importante": 7,

    # Outros
    "marketing multinível": 10, "mlm": 10, "isso não é spam": 15
}

# Dicionário com a pontuação de cada padrão regex (COM ADIÇÕES)
PADROES_REGEX_SPAM = {
    r"(bit\.ly|tinyurl\.com|goo\.gl|cutt\.ly|is\.gd|t\.co)": 10, # Links encurtados
    r"[\!]{2,}|[\?]{2,}": 5, # Excesso de pontuação
    r"\b([A-Z]\.){3,}\b": 12, # Letras separadas por ponto (C.L.I.Q.U.E)
    r"(\(?\d{2}\)?\s?)?(\d{4,5}\-?\d{4})": 3, # Números de telefone
    r"\b[A-Z\s\.]{5,}\b": 10,  # Palavras em maiúsculas com espaços ou pontos entre (G R A T I S)
    r"(?i)\b\w*[@$!#]\w*\b": 7, # Palavras com caracteres especiais no meio (C@ix@)
}

# <<< MUDANÇA PRINCIPAL AQUI >>>
# Aumentamos o limite para tornar o filtro menos rígido.
LIMITE_SPAM_NORMALIZADO = 11.5