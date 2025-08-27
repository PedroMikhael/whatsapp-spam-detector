from django.contrib import admin
# Importe re_path em vez de path
from django.urls import path
from django.urls import re_path
from django.views.generic import RedirectView
from detector.views import webhook_whatsapp

urlpatterns = [
    path('admin/', admin.site.urls),

    # Esta linha agora aceita '/api/spam' E '/api/spam/'
    re_path(r'^api/spam/?$', webhook_whatsapp, name="webhook_whatsapp"),

    # Redireciona a página inicial para a URL do webhook para facilitar
    path('', RedirectView.as_view(url='/api/spam/', permanent=False)),
]