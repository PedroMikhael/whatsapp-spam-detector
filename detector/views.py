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
@api_view(['POST'])
def verificar_spam(request):
    """
    Endpoint para verificar se um texto é spam.
    """
    serializer = SpamRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    texto = serializer.validated_data["texto"]
    resultado = verificar_texto_spam(texto)

    return Response(resultado, status=status.HTTP_200_OK)
