# spamapi/urls.py - VERSÃO FINAL COMPLETA

from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import RedirectView

# Imports para o Webhook
from detector.views import webhook_whatsapp

# Imports para o Swagger
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configuração do Schema do Swagger
schema_view = get_schema_view(
   openapi.Info(
      title="WhatsApp Spam Detector API",
      default_version='v1',
      description="API para detectar spam em mensagens do WhatsApp, implantada na AWS.",
      contact=openapi.Contact(email="seu-email@exemplo.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# Lista final de URLs
urlpatterns = [
    # Redireciona a página inicial para a documentação do Swagger
    path('', RedirectView.as_view(url='/swagger/', permanent=False)),
    
    # URL do painel de administração do Django
    path('admin/', admin.site.urls),
    
    # URL do Webhook do WhatsApp (aceita com ou sem a barra no final)
    re_path(r'^api/spam/?$', webhook_whatsapp, name="webhook_whatsapp"),
    
    # URLs para a documentação do Swagger UI
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]