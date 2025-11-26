# Arquivo: detector/serializers.py

from rest_framework import serializers

# Este serializer está perfeito, não precisa mudar
class SpamRequestSerializer(serializers.Serializer):
    texto = serializers.CharField(
        required=True,
        max_length=1000,
        help_text="Mensagem que será verificada como spam ou não"
    )

# ATUALIZE ESTE SERIALIZER para refletir a nova resposta da API
class SpamResponseSerializer(serializers.Serializer):
    spam = serializers.BooleanField(help_text="Indica se a mensagem é considerada spam.")
    pontuacao = serializers.IntegerField(help_text="A pontuação total de spam calculada.")
    mensagem = serializers.CharField(help_text="Uma mensagem descritiva do resultado.")
    detalhes = serializers.ListField(
        child=serializers.CharField(),
        help_text="Uma lista de motivos que contribuíram para a pontuação."
    )