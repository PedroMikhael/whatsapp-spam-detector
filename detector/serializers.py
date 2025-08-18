from rest_framework import serializers

class SpamRequestSerializer(serializers.Serializer):
    texto = serializers.CharField(
        required=True,
        max_length=1000,
        help_text="Mensagem que será verificada como spam ou não"
    )

class SpamResponseSerializer(serializers.Serializer):
    spam = serializers.BooleanField()
    mensagem = serializers.CharField()
