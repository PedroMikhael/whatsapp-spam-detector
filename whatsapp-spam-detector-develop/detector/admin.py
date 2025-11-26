# detector/admin.py - VERSÃO COM DASHBOARD DE PERFORMANCE

from django.contrib import admin, messages
from django.db.models import Count, Q
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    # Campos que aparecerão na lista principal
    list_display = ('id', 'timestamp', 'risco_ia', 'feedback_formatado', 'remetente')
    
    # Adiciona um filtro na lateral
    list_filter = ('risco_ia', 'feedback_usuario_correto')
    
    # Adiciona uma barra de busca
    search_fields = ('mensagem_original', 'remetente')
    
    # Define a ordem padrão (os mais recentes primeiro)
    ordering = ('-timestamp',)

    def feedback_formatado(self, obj):
        if obj.feedback_usuario_correto is True:
            return '✅ Correto'
        if obj.feedback_usuario_correto is False:
            return '❌ Incorreto'
        return '⏳ Pendente'
    feedback_formatado.short_description = 'Feedback do Usuário'

    def changelist_view(self, request, extra_context=None):
        """
        Esta função é sobreposta para adicionar nossas estatísticas à página.
        """
        # Pega todos os feedbacks que já foram respondidos pelo usuário
        queryset = self.get_queryset(request).filter(feedback_usuario_correto__isnull=False)
        
        total_com_feedback = queryset.count()
        acertos = queryset.filter(feedback_usuario_correto=True).count()
        
        percentual_acertos = 0
        if total_com_feedback > 0:
            percentual_acertos = (acertos / total_com_feedback) * 100
        
        # Cria a mensagem de status para exibir no topo da página
        mensagem = f"📊 Performance da IA: {acertos} acertos de {total_com_feedback} feedbacks recebidos. Precisão de {percentual_acertos:.2f}%."
        self.message_user(request, mensagem, level=messages.SUCCESS)

        return super().changelist_view(request, extra_context=extra_context)