# detector/views.py - VERSÃO FINAL COM SWAGGER FUNCIONAL

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
from .models import Feedback
from .services import analisar_com_gemini, enviar_mensagem_whatsapp

# Importa o decorador que o Swagger precisa
from rest_framework.decorators import api_view

@api_view(['GET', 'POST']) # <-- A ETIQUETA DE API QUE FALTAVA
@csrf_exempt
def webhook_whatsapp(request):

    # --- LÓGICA DO GET (Verificação) ---
    if request.method == 'GET':
        if request.GET.get("hub.mode") == "subscribe" and request.GET.get("hub.verify_token") == settings.WHATSAPP_VERIFY_TOKEN:
            print("WEBHOOK VERIFICADO COM SUCESSO!")
            return HttpResponse(request.GET.get("hub.challenge"), status=200)
        else:
            print("FALHA NA VERIFICAÇÃO: Tokens não bateram.")
            return HttpResponse("Token de verificação inválido", status=403)

    # --- LÓGICA DO POST (Receber, Analisar, Responder e Coletar Feedback) ---
    elif request.method == 'POST':
        try:
            # Usamos request.data que vem do @api_view, é mais robusto
            data = request.data

            texto_mensagem = data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}).get('messages', [{}])[0].get('text', {}).get('body')
            remetente = data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}).get('messages', [{}])[0].get('from')

            if not texto_mensagem or not remetente:
                print("Webhook recebido, mas não é uma mensagem de texto do usuário. Ignorando.")
                return HttpResponse("OK", status=200)

            texto_lower = texto_mensagem.lower().strip()

            if texto_lower == 'sim' or texto_lower == 'não' or texto_lower == 'nao':
                ultima_analise = Feedback.objects.filter(remetente=remetente, feedback_usuario_correto__isnull=True).order_by('-timestamp').first()

                if ultima_analise:
                    ultima_analise.feedback_usuario_correto = (texto_lower == 'sim')
                    ultima_analise.save()

                    mensagem_agradecimento = "Obrigado pelo seu feedback! Você está me ajudando a aprender. 👍"
                    enviar_mensagem_whatsapp(remetente, mensagem_agradecimento)
                    print(f"--- FEEDBACK de '{remetente}' foi salvo! ---")
                    return HttpResponse("OK", status=200)

            print(f"--- MENSAGEM RECEBIDA de '{remetente}': {texto_mensagem} ---")

            resultado_analise = analisar_com_gemini(texto_mensagem)
            print(f"Análise da IA: {resultado_analise.get('analysis_details')}")

            Feedback.objects.create(
                mensagem_original=texto_mensagem,
                remetente=remetente,
                risco_ia=resultado_analise.get('risk_level', 'INDETERMINADO'),
                analise_ia=str(resultado_analise.get('analysis_details', ''))
            )

            mensagem_de_resposta = resultado_analise['user_response']
            mensagem_com_feedback = mensagem_de_resposta + "\n\nMinha análise foi útil? Responda com 'Sim' ou 'Não'."
            enviar_mensagem_whatsapp(remetente, mensagem_com_feedback)

            print("--- RESPOSTA E PEDIDO DE FEEDBACK ENVIADOS ---")

            return HttpResponse("OK", status=200)

        except Exception as e:
            print(f"Erro ao processar o webhook POST: {e}")
            return HttpResponse(status=400)

    return HttpResponse("Método não permitido", status=405)