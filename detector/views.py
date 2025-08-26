# detector/views.py - VERSÃO ATUALIZADA PARA O WEBHOOK

import json
from django.conf import settings # Importa as configurações do Django
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .serializers import SpamRequestSerializer, SpamResponseSerializer
from .services import verificar_texto_spam

@swagger_auto_schema(
    method='post',
    request_body=SpamRequestSerializer,
    responses={200: SpamResponseSerializer},
    operation_description="Verifica se um texto é spam"
)
@api_view(['GET', 'POST']) # AGORA ACEITA GET E POST
def verificar_spam(request):

    # LÓGICA PARA O DESAFIO DA META (GET)
    if request.method == 'GET':
        verify_token = settings.WHATSAPP_VERIFY_TOKEN
        if request.query_params.get('hub.verify_token') == verify_token:
            return Response(int(request.query_params.get('hub.challenge')), status=200)
        else:
            return Response({"error": "Token de verificação inválido"}, status=403)

    # LÓGICA ANTIGA PARA RECEBER MENSAGENS (POST)
    if request.method == 'POST':
        dados = request.data

        # Verificando se é uma mensagem do WhatsApp ou um teste do Swagger
        if 'entry' in dados:
            try:
                texto_recebido = dados['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
                dados_para_serializer = {'texto': texto_recebido}
            except (KeyError, IndexError):
                return Response(status=204) # Ignora outros tipos de notificação
        else: # Mantém a lógica para o teste do Swagger
            if '_content' in dados:
                dados = json.loads(dados['_content'][0])
            dados_para_serializer = dados

        serializer = SpamRequestSerializer(data=dados_para_serializer)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        texto = serializer.validated_data["texto"]
        resultado = verificar_texto_spam(texto)

        return Response(resultado, status=status.HTTP_200_OK)