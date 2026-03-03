# detector/views.py

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
from .models import Feedback
from .services import analisar_com_IA, enviar_mensagem_whatsapp, adicionar_ao_chromadb
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import (
    AnalisarEmailSerializer,
    AnaliseResponseSerializer,
    FeedbackSerializer,
    TreinarRAGSerializer,
    TreinarRAGResponseSerializer,
)


@swagger_auto_schema(
    method='post',
    operation_id='analisar_mensagem',
    operation_summary='Analisar Email/Mensagem',
    operation_description='Envia um texto para análise de spam/phishing pela IA.',
    request_body=AnalisarEmailSerializer,
    responses={200: AnaliseResponseSerializer, 400: 'Texto não fornecido'},
    tags=['Análise'],
)
@api_view(['POST'])
def analisar_mensagem(request):
    """Analisa um email/mensagem e retorna a classificação de risco."""
    serializer = AnalisarEmailSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    texto = serializer.validated_data['texto']
    remetente = serializer.validated_data.get('remetente', 'swagger-test')

    try:
        resultado_analise = analisar_com_IA(texto, debug=True)
        
        Feedback.objects.create(
            mensagem_original=texto,
            remetente=remetente,
            risco_ia=resultado_analise.get('risk_level', 'INDETERMINADO'),
            analise_ia=str(resultado_analise.get('analysis_details', ''))
        )
        
        return Response(resultado_analise, status=status.HTTP_200_OK)
    
    except Exception as e:
        print(f"Erro ao processar análise: {e}")
        return Response(
            {"error": f"Erro interno: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='get',
    operation_id='listar_analises',
    operation_summary='Listar Análises',
    operation_description='Lista todas as análises realizadas, da mais recente à mais antiga.',
    responses={200: FeedbackSerializer(many=True)},
    tags=['Histórico'],
)
@api_view(['GET'])
def listar_analises(request):
    """Retorna todas as análises salvas no banco de dados."""
    analises = Feedback.objects.all().order_by('-timestamp')
    serializer = FeedbackSerializer(analises, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_id='detalhe_analise',
    operation_summary='Detalhe de Análise',
    operation_description='Retorna os detalhes de uma análise específica pelo ID.',
    responses={200: FeedbackSerializer, 404: 'Não encontrada'},
    tags=['Histórico'],
)
@api_view(['GET'])
def detalhe_analise(request, analise_id):
    """Retorna detalhes de uma análise específica."""
    try:
        analise = Feedback.objects.get(id=analise_id)
        serializer = FeedbackSerializer(analise)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Feedback.DoesNotExist:
        return Response({"error": "Análise não encontrada."}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='post',
    operation_id='treinar_rag',
    operation_summary='Treinar RAG',
    operation_description='Adiciona um exemplo ao ChromaDB. Rótulos: SPAM, HAM, PHISHING, etc.',
    request_body=TreinarRAGSerializer,
    responses={200: TreinarRAGResponseSerializer, 400: 'Parâmetros inválidos'},
    tags=['Treinamento'],
)
@api_view(['POST'])
def treinar_rag(request):
    """Adiciona um novo exemplo ao banco vetorial ChromaDB."""
    serializer = TreinarRAGSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    texto = serializer.validated_data['texto']
    rotulo = serializer.validated_data['rotulo']

    sucesso = adicionar_ao_chromadb(texto=texto, rotulo=rotulo)
    
    if sucesso:
        return Response(
            {"status": "sucesso", "mensagem": f"Exemplo adicionado com rótulo: {rotulo}"},
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {"status": "erro", "mensagem": "Falha ao adicionar ao ChromaDB."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Webhook WhatsApp (não aparece no Swagger)
@api_view(['GET', 'POST'])
@csrf_exempt
def webhook_whatsapp(request):
    if request.method == 'GET':
        if request.GET.get("hub.mode") == "subscribe" and request.GET.get("hub.verify_token") == settings.WHATSAPP_VERIFY_TOKEN:
            return HttpResponse(request.GET.get("hub.challenge"), status=200)
        return HttpResponse("Token de verificação inválido", status=403)

    elif request.method == 'POST':
        try:
            data = request.data
            texto_mensagem = None
            remetente = None
            origem = "desconhecida"

            if 'entry' in data and data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}).get('messages', [{}])[0].get('text'):
                texto_mensagem = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
                remetente = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
                origem = "whatsapp"
            elif 'texto' in data:
                texto_mensagem = data.get('texto')
                origem = "script_evaluate"

            if texto_mensagem:
                resultado_analise = analisar_com_IA(texto_mensagem)

                if origem == "whatsapp":
                    Feedback.objects.create(
                        mensagem_original=texto_mensagem,
                        remetente=remetente,
                        risco_ia=resultado_analise.get('risk_level', 'INDETERMINADO'),
                        analise_ia=str(resultado_analise.get('analysis_details', ''))
                    )
                    return HttpResponse("OK", status=200)
                elif origem == "script_evaluate":
                    return JsonResponse(resultado_analise, status=200)
            
            return HttpResponse("Formato de POST não reconhecido", status=400)
        except Exception as e:
            return HttpResponse(f"Erro interno: {e}", status=500)


def registrar_feedback(request, feedback_id, resultado):
    try:
        analise = Feedback.objects.get(id=feedback_id)
        
        if analise.feedback_usuario_correto is not None:
            status_antigo = "Correto" if analise.feedback_usuario_correto else "Incorreto"
            return HttpResponse(f"""
            <html><head><title>Feedback Já Registrado</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: #ffc107;">⚠️ Feedback Já Registrado</h1>
                <p>Registrado como: <strong>{status_antigo}</strong>.</p>
            </body></html>""")

        analise.feedback_usuario_correto = (resultado == 'correto')
        analise.save()
        
        return HttpResponse("""
        <html><head><title>Obrigado!</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1 style="color: #28a745;">✅ Obrigado pelo seu feedback!</h1>
            <p>Sua resposta foi registrada com sucesso.</p>
        </body></html>""")
        
    except Feedback.DoesNotExist:
        return HttpResponse("<h1>Análise não encontrada.</h1>", status=404)
    

def processar_feedback_treinamento(request):
    """Recebe feedback do usuário e aciona treinamento RAG."""
    if request.method == 'GET':
        feedback_id = request.GET.get('id')
        novo_rotulo = request.GET.get('rotulo') 

        if not feedback_id or not novo_rotulo:
            return JsonResponse({'status': 'erro', 'mensagem': 'Parâmetros ID e RÓTULO são obrigatórios.'}, status=400)
        
        try:
            feedback_registro = get_object_or_404(Feedback, id=feedback_id)

            if feedback_registro.treinamento_concluido:
                return HttpResponse("Este feedback já foi processado anteriormente.")

            sucesso_treinamento = adicionar_ao_chromadb(
                texto=feedback_registro.mensagem_original,
                rotulo=novo_rotulo
            )

            if sucesso_treinamento:
                feedback_registro.treinamento_concluido = True
                feedback_registro.save()
                return HttpResponse("✅ Feedback processado com sucesso!")
            else:
                return HttpResponse("❌ Erro ao atualizar o modelo.", status=500)

        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=500)
    
    return JsonResponse({'status': 'erro', 'mensagem': 'Método não permitido.'}, status=405)