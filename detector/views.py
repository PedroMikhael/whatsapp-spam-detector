# detector/views.py - VERSÃO DE TESTE SIMPLIFICADA

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET', 'POST']) # Aceita GET e POST
def verificar_spam(request):
    
    # Se for a visita de verificação da Meta (GET)
    if request.method == 'GET' and 'hub.challenge' in request.query_params:
        # Responda "SIM" imediatamente, sem checar o token.
        challenge = request.query_params.get('hub.challenge')
        print(f"Desafio da Meta recebido: {challenge}. Respondendo com sucesso.")
        return Response(challenge, status=200)

    # Se for uma mensagem de SPAM (POST)
    if request.method == 'POST':
        # Por enquanto, só vamos confirmar que recebemos e depois faremos a análise.
        print(f"Recebida mensagem para análise: {request.data}")
        return Response({"status": "mensagem recebida com sucesso"}, status=200)

    # Se não for nenhum dos dois, retorne um erro.
    return Response({"error": "Requisição inválida"}, status=400)