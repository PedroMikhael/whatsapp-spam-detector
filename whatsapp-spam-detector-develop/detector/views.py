# detector/views.py - VERSÃO FINAL (Entende WhatsApp, E-mail e o Script)

from django.http import HttpResponse, JsonResponse # Importa JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
from .models import Feedback
from .services import analisar_com_gemini, enviar_mensagem_whatsapp
from rest_framework.decorators import api_view # Importa o decorador de API

@api_view(['GET', 'POST']) # Marca como uma view de API
@csrf_exempt
def webhook_whatsapp(request):
    
    # --- LÓGICA DO GET (Verificação do Webhook) ---
    if request.method == 'GET':
        if request.GET.get("hub.mode") == "subscribe" and request.GET.get("hub.verify_token") == settings.WHATSAPP_VERIFY_TOKEN:
            print("WEBHOOK VERIFICADO COM SUCESSO!")
            return HttpResponse(request.GET.get("hub.challenge"), status=200)
        else:
            print("FALHA NA VERIFICAÇÃO: Tokens não bateram.")
            return HttpResponse("Token de verificação inválido", status=403)

    # --- LÓGICA DO POST (Recebe WhatsApp OU Script) ---
    elif request.method == 'POST':
        try:
            data = request.data # .data é mais robusto que json.loads
            
            texto_mensagem = None
            remetente = None
            origem_da_chamada = "desconhecida" # Para sabermos quem chamou

            # --- Tenta extrair como MENSAGEM DO WHATSAPP ---
            if 'entry' in data and data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}).get('messages', [{}])[0].get('text'):
                texto_mensagem = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
                remetente = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
                origem_da_chamada = "whatsapp"
            
            # --- Tenta extrair como MENSAGEM DO SCRIPT DE AVALIAÇÃO ---
            elif 'texto' in data:
                texto_mensagem = data.get('texto')
                origem_da_chamada = "script_evaluate"

            # Se conseguimos extrair um texto, vamos analisar
            if texto_mensagem:
                print(f"--- MENSAGEM RECEBIDA ({origem_da_chamada}): {texto_mensagem[:50]}... ---")
                
                resultado_analise = analisar_com_gemini(texto_mensagem)
                print(f"Análise da IA: {resultado_analise.get('analysis_details')}")

                # Se a origem for o WhatsApp, execute a lógica do WhatsApp (silenciada)
                if origem_da_chamada == "whatsapp":
                    Feedback.objects.create(
                        mensagem_original=texto_mensagem,
                        remetente=remetente,
                        risco_ia=resultado_analise.get('risk_level', 'INDETERMINADO'),
                        analise_ia=str(resultado_analise.get('analysis_details', ''))
                    )
                    print("--- ANÁLISE CONCLUÍDA (Respostas WhatsApp desativadas) ---")
                    # Retorna 200 OK para a Meta
                    return HttpResponse("OK", status=200)
                
                # Se a origem for o SCRIPT DE AVALIAÇÃO, devolve o JSON completo
                elif origem_da_chamada == "script_evaluate":
                    print("--- RETORNANDO RESULTADO PARA SCRIPT DE AVALIAÇÃO ---")
                    return JsonResponse(resultado_analise, status=200)
            
            # Se não for nenhum dos formatos esperados
            return HttpResponse("Formato de POST não reconhecido", status=400)

        except Exception as e:
            print(f"Erro CRÍTICO ao processar o webhook POST: {e}")
            return HttpResponse(f"Erro interno: {e}", status=500)


def registrar_feedback(request, feedback_id, resultado):
    try:
        analise = Feedback.objects.get(id=feedback_id)
        
        # Previne que o mesmo feedback seja alterado várias vezes
        if analise.feedback_usuario_correto is not None:
            status_antigo = "Correto" if analise.feedback_usuario_correto else "Incorreto"
            html_response = f"""
            <html>
                <head><title>Feedback Já Registrado</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px; color: #333;">
                    <h1 style="color: #ffc107;">⚠️ Feedback Já Registrado</h1>
                    <p>O feedback para esta análise já foi registrado como: <strong>{status_antigo}</strong>.</p>
                    <p>Obrigado por sua colaboração!</p>
                    <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 100px;">
                    <p style="font-size: 12px; color: #888;">Guardião Digital - Um projeto de pesquisa do LARCES/UECE</p>
                </body>
            </html>
            """
            return HttpResponse(html_response)

        analise.feedback_usuario_correto = (resultado == 'correto')
        analise.save()
        
        html_response = """
        <html>
            <head><title>Obrigado!</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px; color: #333;">
                <h1 style="color: #28a745;">✅ Obrigado pelo seu feedback!</h1>
                <p>Sua resposta foi registrada com sucesso.</p>
                <p>Você está ajudando o Guardião Digital a ficar mais inteligente.</p>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 100px;">
                <p style="font-size: 12px; color: #888;">Guardião Digital - Um projeto de pesquisa do LARCES/UECE</p>
            </body>
        </html>
        """
        return HttpResponse(html_response)
        
    except Feedback.DoesNotExist:
        return HttpResponse("<h1>Erro: Análise não encontrada.</h1><p>Este link de feedback pode ter expirado ou ser inválido.</p>", status=404)