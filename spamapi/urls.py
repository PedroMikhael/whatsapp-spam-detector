

from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import RedirectView
from detector.views import webhook_whatsapp
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from detector.views import webhook_whatsapp, registrar_feedback
from detector.views import processar_feedback_treinamento

schema_view = get_schema_view(
   openapi.Info(
      title="WhatsApp Spam Detector API",
      default_version='v1',
      description="API inteligente para detectar spam em mensagens do WhatsApp.",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    
    path('', RedirectView.as_view(url='/swagger/', permanent=False)),
    
    # Health check endpoint simples
    path('health/', lambda request: __import__('django.http', fromlist=['JsonResponse']).JsonResponse({'status': 'ok', 'message': 'VerificAI is running!'})),

    path('admin/', admin.site.urls),

    # URL do Webhook do WhatsApp
    re_path(r'^api/spam/?$', webhook_whatsapp, name="webhook_whatsapp"),

    # URL da documentação do Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('feedback/<int:feedback_id>/<str:resultado>/', registrar_feedback, name='registrar_feedback'),
    path('feedback/', processar_feedback_treinamento, name='feedback_treinamento'),
]