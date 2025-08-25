from django.contrib import admin
from django.urls import path
from detector.views import verificar_spam
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.generic import RedirectView

schema_view = get_schema_view(
   openapi.Info(
      title="Zap Spam Detector API",
      default_version='v1',
      description="API para detectar spam em mensagens",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),  # garante acesso público
)

urlpatterns = [
    path('', RedirectView.as_view(url='/swagger/', permanent=True)),  # redireciona / para swagger
    path('admin/', admin.site.urls),
    path('api/spam/', verificar_spam, name="verificar_spam"),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
