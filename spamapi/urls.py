
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import RedirectView
from detector.views import webhook_whatsapp
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="WhatsApp Spam Detector API",
      default_version='v1',
      description="API inteligente para detectar spam em mensagens do WhatsApp.",
      contact=openapi.Contact(email="seu-email-profissional@exemplo.com"),
   ),
   public=True, 
   permission_classes=(permissions.AllowAny,), # 
)

urlpatterns = [
   
    path('', RedirectView.as_view(url='/swagger/', permanent=False)),

    path('admin/', admin.site.urls),

    
    re_path(r'^api/spam/?$', webhook_whatsapp, name="webhook_whatsapp"),

    
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]