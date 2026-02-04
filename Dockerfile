# =============================================================================
# Dockerfile para WhatsApp Spam Detector - Hugging Face Spaces
# Este é um projeto Django com ChromaDB, LangChain e Gemini API
# =============================================================================

# Usar imagem Python slim para reduzir tamanho
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root (requerido pelo Hugging Face Spaces)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Definir diretório de trabalho do usuário
WORKDIR $HOME/app

# Copiar requirements primeiro (para aproveitar cache do Docker)
COPY --chown=user:user requirements.txt .

# Instalar dependências Python
RUN pip install --user --no-cache-dir -r requirements.txt

# Copiar o código do projeto
COPY --chown=user:user . .

# Criar diretório para ChromaDB e static files
RUN mkdir -p chroma_db static

# Coletar arquivos estáticos do Django
RUN python manage.py collectstatic --noinput

# Expor porta (Hugging Face usa 7860 por padrão)
EXPOSE 7860

# Comando de inicialização
# Usar gunicorn para produção com uvicorn workers para melhor performance
CMD ["python", "-m", "gunicorn", "spamapi.wsgi:application", "--bind", "0.0.0.0:7860", "--workers", "2", "--threads", "4", "--timeout", "120"]
