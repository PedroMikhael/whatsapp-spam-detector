from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-(bcp0_$=z9nylls(cp8p%!it+*(d2ap3p(9t40^%s@_gg+1t#f'
DEBUG = False  # Produção
ALLOWED_HOSTS = ['18.221.25.182', '127.0.0.1', 'localhost', '.ngrok-free.app', 'chatbot-spam.duckdns.org']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'detector',
    'drf_yasg',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'spamapi.urls'

WSGI_APPLICATION = 'spamapi.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'  # para collectstatic

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:9000",
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # se você tiver templates personalizados, coloque o caminho aqui
        'APP_DIRS': True,  # isso permite que Django encontre templates dentro das apps
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # necessário para admin e Swagger
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

UTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Token usado para validar o webhook do WhatsApp
WHATSAPP_VERIFY_TOKEN = "tokenfacil123"

WHATSAPP_ACCESS_TOKEN = 'EAFUA6anUjL0BPXLD70ZCWZBvuBiZBvdZAO72ZBOdiFsV3QuLPTMZAzvShjl8gkkUzg1sK3dqgH4R3kCvgAfxnjBES6aV1rYZCgZA0JEgyUfUfLGZAUSKL01zVBUyoQEjZA8CXVL6Wk73KKs05PDcxZC0tAB3erh9qsLH7nci2ZAyNr64Et7kI8RRaZBnvxitqNI5TS18nW8uX5XuLzvKItSBKpWyrZBeuaMImoRleAK4TufwjS3uMWiW8wFdEAinGFGcBSey4ZD'
WHATSAPP_PHONE_NUMBER_ID = '765888489941122'