# detector/models.py
from django.db import models

class Feedback(models.Model):
    mensagem_original = models.TextField()
    remetente = models.CharField(max_length=20)

    # Como a IA classificou
    risco_ia = models.CharField(max_length=20) # SAFE, SUSPICIOUS, MALICIOUS
    analise_ia = models.TextField()

    # O feedback do usuário
    feedback_usuario_correto = models.BooleanField(null=True, blank=True) # True = IA acertou, False = IA errou

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Análise para {self.remetente} em {self.timestamp.strftime('%d/%m/%Y %H:%M')}"