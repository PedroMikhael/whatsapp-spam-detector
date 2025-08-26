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
@api_view(['GET', 'POST'])  # webhook precisa aceitar GET e POST
def verificar_spam(request):
    """
    Endpoint usado como Webhook do WhatsApp e também para verificar spam via POST.
    """

    # 🔹 1) LÓGICA DO GET → validação do webhook do WhatsApp (Meta)
    if request.method == 'GET':
        verify_token = getattr(settings, "WHATSAPP_VERIFY_TOKEN", "tokenfacil123")
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")

        if mode == "subscribe" and token == verify_token:
            print("✅ Webhook verificado com sucesso pelo Meta")
            return HttpResponse(challenge, status=200)  # tem que ser texto puro
        else:
            return HttpResponse("Token de verificação inválido", status=403)

    # 🔹 2) LÓGICA DO POST → recebe mensagens reais do WhatsApp
    if request.method == 'POST':
        dados = request.data

        # Se veio do WhatsApp (mensagem real)
        if 'entry' in dados:
            try:
                texto_recebido = dados['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
                dados_para_serializer = {'texto': texto_recebido}
            except (KeyError, IndexError):
                return Response(status=204)  # ignora notificações sem mensagem
        else:
            # 🔹 Se for teste via Swagger, ainda funciona
            if '_content' in dados:
                dados = json.loads(dados['_content'][0])
            dados_para_serializer = dados

        serializer = SpamRequestSerializer(data=dados_para_serializer)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        texto = serializer.validated_data["texto"]
        resultado = verificar_texto_spam(texto)

        return Response(resultado, status=status.HTTP_200_OK)
