

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings

from .services import analisar_com_gemini, enviar_mensagem_whatsapp

@csrf_exempt
def webhook_whatsapp(request):
    
    if request.method == 'GET':
        if request.GET.get("hub.mode") == "subscribe" and request.GET.get("hub.verify_token") == settings.WHATSAPP_VERIFY_TOKEN:
            print("WEBHOOK VERIFICADO COM SUCESSO!")
            return HttpResponse(request.GET.get("hub.challenge"), status=200)
        else:
            print("FALHA NA VERIFICAÇÃO: Tokens não bateram.")
            return HttpResponse("Token de verificação inválido", status=403)

    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            
            
            if 'entry' in data and data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}).get('messages', [{}])[0].get('text'):
                
                texto_mensagem = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
                remetente = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
                
                print(f"--- MENSAGEM RECEBIDA de '{remetente}': {texto_mensagem} ---")
                
                
                resultado_analise = analisar_com_gemini(texto_mensagem)
                print(f"Análise da IA: {resultado_analise.get('analise')}")
                
                
                mensagem_de_resposta = resultado_analise['resposta_usuario']
                
                
                enviar_mensagem_whatsapp(remetente, mensagem_de_resposta)
                
                print("--- RESPOSTA ENVIADA ---")
            else:
                
                print("Webhook recebido, mas não é uma mensagem de texto do usuário. Ignorando.")
            
            
            return HttpResponse("OK", status=200)

        except Exception as e:
            print(f"Erro ao processar o webhook POST: {e}")
            return HttpResponse(status=400) # Bad Request

   
    return HttpResponse("Método não permitido", status=405)