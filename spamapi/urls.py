from rest_framework.documentation import include_docs_urls
from django.contrib import admin
from django.urls import path, re_path, include 
from django.views.generic import RedirectView
from detector.views import webhook_whatsapp


urlpatterns = [
    
    path('', include_docs_urls(title='WhatsApp Spam Detector API')),

    path('admin/', admin.site.urls),

    re_path(r'^api/spam/?$', webhook_whatsapp, name="webhook_whatsapp"),
]