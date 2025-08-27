# detector/views.py - VERSÃO FINAL COMPLETA

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Importa a sua lógica de análise de spam
from .services import verificar_texto_spam

# Defina seu token secreto aqui
VERIFY_TOKEN = "tokenfacil123" # Use o mesmo token que está no painel da Meta

@csrf_exempt
def webhook_whatsapp(request):
    # --- Lógica para o DESAFIO DE VERIFICAÇÃO (GET) ---
    if request.method == 'GET':
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("WEBHOOK VERIFICADO COM SUCESSO!")
            return HttpResponse(challenge, status=200)
        else:
            print("FALHA NA VERIFICAÇÃO: Tokens não bateram.")
            return HttpResponse("Token de verificação inválido", status=403)

    # --- Lógica para RECEBER E ANALISAR MENSAGENS (POST) ---
    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))

            # Verifica se é uma notificação de mensagem de texto
            if 'entry' in data and data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}).get('messages', [{}])[0].get('text'):
                
                # Extrai o texto da mensagem
                texto_mensagem = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
                remetente = data['entry'][0]['changes'][0]['value']['messages'][0]['from']

                print(f"--- MENSAGEM RECEBida de '{remetente}' ---")
                print(f"Conteúdo: {texto_mensagem}")

                # **AQUI A MÁGICA ACONTECE!**
                # Chama sua função para analisar o texto
                resultado_analise = verificar_texto_spam(texto_mensagem)

                # Imprime o resultado detalhado no console do servidor
                print(f"Resultado da Análise: {resultado_analise['mensagem']}")
                print("------------------------------------------")
            
            else:
                # Se não for uma mensagem de texto, apenas ignore
                print("Webhook recebido, mas não é uma mensagem de texto do usuário. Ignorando.")

            # Responde ao WhatsApp que o evento foi recebido com sucesso
            return HttpResponse("OK", status=200)

        except Exception as e:
            # Captura qualquer erro inesperado para depuração
            print(f"Erro ao processar o webhook: {e}")
            return HttpResponse(status=400) # Bad Request

    # Se for qualquer outro método (DELETE, PUT, etc.)
    return HttpResponse("Método não permitido", status=405)