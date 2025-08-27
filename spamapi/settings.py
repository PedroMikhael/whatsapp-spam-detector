from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-(bcp0_$=z9nylls(cp8p%!it+*(d2ap3p(9t40^%s@_gg+1t#f'
DEBUG = False  
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
STATIC_ROOT = BASE_DIR / 'static' 

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
        'DIRS': [], 
        'APP_DIRS': True,  
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # 
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



WHATSAPP_VERIFY_TOKEN = "tokenfacil123"

WHATSAPP_ACCESS_TOKEN = 'EAFUA6anUjL0BPfnvbN72YffEJaU8quQRxRBycai7yY0SsX0vOqf1dZCGPWzXJSMZCWa5ZBSWUNEYV8YBmSX4mmvcZBWnaJLQlxssz93nNMVSh1Lkg1MNTv5goPc3Nx7DlUQpspQZBZALovRhpw3diKFU59xEGKfPsjZBRQj9v5IZBZAbuc1cUAsywETOh6feGyJI6fDDdfw2yIvXQFyRxCzgZBbO3Bo8f6D8tYdA1qELyuiB1v3XPLxoarE5vGPR27dwZDZD'
WHATSAPP_PHONE_NUMBER_ID = '765888489941122'
