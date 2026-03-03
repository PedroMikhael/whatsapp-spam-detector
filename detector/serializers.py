# Arquivo: detector/serializers.py

from rest_framework import serializers
from .models import Feedback


# ========================
# REQUEST SERIALIZERS
# ========================

class AnalisarEmailSerializer(serializers.Serializer):
    """Serializer para o endpoint de análise de email/mensagem."""
    texto = serializers.CharField(
        required=True,
        help_text="Texto do email ou mensagem a ser analisado pelo VerificAI."
    )
    remetente = serializers.CharField(
        required=False,
        default="swagger-test",
        help_text="Identificação do remetente (opcional, padrão: 'swagger-test')."
    )


class TreinarRAGSerializer(serializers.Serializer):
    """Serializer para o endpoint de treinamento manual do RAG."""
    texto = serializers.CharField(
        required=True,
        help_text="Texto da mensagem para adicionar ao banco de dados vetorial."
    )
    rotulo = serializers.CharField(
        required=True,
        help_text="Classificação da mensagem: SPAM, HAM, PHISHING, etc."
    )


# ========================
# RESPONSE SERIALIZERS
# ========================

class AnaliseResponseSerializer(serializers.Serializer):
    """Serializer da resposta de análise da IA."""
    risk_level = serializers.CharField(help_text="Nível de risco: SAFE, SUSPICIOUS, MALICIOUS ou INDETERMINADO.")
    analysis_details = serializers.ListField(
        child=serializers.CharField(),
        help_text="Lista de pontos técnicos da análise."
    )
    user_response = serializers.CharField(help_text="Resposta em português para o usuário.")


class FeedbackSerializer(serializers.ModelSerializer):
    """Serializer do modelo Feedback para listagem de análises."""
    class Meta:
        model = Feedback
        fields = '__all__'


class TreinarRAGResponseSerializer(serializers.Serializer):
    """Serializer da resposta de treinamento do RAG."""
    status = serializers.CharField(help_text="Status da operação: 'sucesso' ou 'erro'.")
    mensagem = serializers.CharField(help_text="Mensagem descritiva do resultado.")