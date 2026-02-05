#!/bin/bash
# Startup script para rodar Django + Email Bot

echo "===== Application Startup at $(date) ====="

# Rodar migrações do banco de dados
echo "Aplicando migrações do banco de dados..."
python manage.py migrate --noinput

# Rodar o email bot em background (se TOKEN_JSON estiver configurado)
if [ -n "$TOKEN_JSON" ]; then
    echo "Iniciando email_bot em background..."
    python email_bot.py &
else
    echo "TOKEN_JSON não configurado, email_bot não será iniciado."
fi

# Rodar o Django com gunicorn
exec python -m gunicorn spamapi.wsgi:application --bind 0.0.0.0:7860 --workers 2 --threads 4 --timeout 120

