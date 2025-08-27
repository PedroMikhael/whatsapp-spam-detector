
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Importa a lógica de análise E a nova lógica de envio
from .services import verificar_texto_spam, enviar_mensagem_whatsapp

VERIFY_TOKEN = "tokenfacil123"

@csrf_exempt
def webhook_whatsapp(request):
    # Lógica do GET (Verificação) - não muda
    if request.method == 'GET':
        # ... (código do GET continua o mesmo) ...
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("WEBHOOK VERIFICADO COM SUCESSO!")
            return HttpResponse(challenge, status=200)
        else:
            print("FALHA NA VERIFICAÇÃO: Tokens não bateram.")
            return HttpResponse("Token de verificação inválido", status=403)

    # Lógica do POST (Receber e Responder) - ATUALIZADA
    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))

            if 'entry' in data and data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}).get('messages', [{}])[0].get('text'):

                texto_mensagem = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
                remetente = data['entry'][0]['changes'][0]['value']['messages'][0]['from']

                print(f"--- MENSAGEM RECEBIDA de '{remetente}': {texto_mensagem} ---")

                # 1. Analisa o texto
                resultado_analise = verificar_texto_spam(texto_mensagem)
                print(f"Resultado da Análise: {resultado_analise['mensagem']}")

                # 2. **ENVIA A RESPOSTA DE VOLTA!**
                mensagem_de_resposta = resultado_analise['mensagem']
                enviar_mensagem_whatsapp(remetente, mensagem_de_resposta)

                print("---------------------------------------------------------")

            else:
                print("Webhook recebido, mas não é uma mensagem de texto. Ignorando.")

            return HttpResponse("OK", status=200)

        except Exception as e:
            print(f"Erro ao processar o webhook: {e}")
            return HttpResponse(status=400)

    return HttpResponse("Método não permitido", status=405)
