from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/spam/', views.verificar_spam, name='verificar_spam'),
]





