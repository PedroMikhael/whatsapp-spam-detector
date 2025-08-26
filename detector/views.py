import json
import os
from django.conf import settings
from django.http import HttpResponse
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
@api_view(['GET', 'POST'])
def verificar_spam(request):
    # 🔹 Verificação do Webhook (GET)
    if request.method == 'GET':
        verify_token = settings.WHATSAPP_VERIFY_TOKEN
        if request.query_params.get('hub.verify_token') == verify_token:
            return Response(request.query_params.get('hub.challenge'), status=200)
        else:
            return Response({"error": "Token de verificação inválido"}, status=403)

    # 🔹 Recebimento de mensagens (POST)
    if request.method == 'POST':
        dados = request.data

        if 'entry' in dados:  # Chamado pelo WhatsApp
            try:
                texto_recebido = dados['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
                dados_para_serializer = {'texto': texto_recebido}
            except (KeyError, IndexError):
                return Response(status=204)
        else:  # Chamado pelo Swagger
            if '_content' in dados:
                dados = json.loads(dados['_content'][0])
            dados_para_serializer = dados

        serializer = SpamRequestSerializer(data=dados_para_serializer)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        texto = serializer.validated_data["texto"]
        resultado = verificar_texto_spam(texto)

        return Response(resultado, status=status.HTTP_200_OK)
