# detector/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

VERIFY_TOKEN = "tokenfacil123"  # o mesmo que você colocou no painel da Meta

@api_view(['GET', 'POST'])
def verificar_spam(request):

    # Verificação inicial do webhook (Meta envia GET)
    if request.method == 'GET':
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print(f"Webhook verificado com sucesso! challenge={challenge}")
            return Response(challenge, status=200)
        else:
            print("Token inválido na verificação do webhook")
            return Response({"error": "Token inválido"}, status=403)

    # Recebendo mensagens (Meta envia POST)
    if request.method == 'POST':
        print(f"Recebida mensagem para análise: {request.data}")
        return Response({"status": "mensagem recebida com sucesso"}, status=200)

    return Response({"error": "Requisição inválida"}, status=400)

@csrf_exempt
def webhook_view(request):
    if request.method == "GET":
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")
        
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return HttpResponse(challenge, status=200)
        else:
            return HttpResponse("Token inválido", status=403)

    elif request.method == "POST":
        # Aqui você recebe mensagens
        print("Mensagem recebida:", request.body)
        return HttpResponse("OK", status=200)