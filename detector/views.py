from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services import verificar_texto_spam

def home(request):
    return render(request, "detector/home.html")

@api_view(['POST'])
def verificar_spam(request):
    texto = request.data.get("texto", "")
    resultado = verificar_texto_spam(texto)
    return Response(resultado)






