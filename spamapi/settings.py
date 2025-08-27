from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-(bcp0_$=z9nylls(cp8p%!it+*(d2ap3p(9t40^%s@_gg+1t#f'
DEBUG = False  # Produção
ALLOWED_HOSTS = ['18.221.25.182', '127.0.0.1', 'localhost', '.ngrok-free.app']

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

# Token usado para validar o webhook do WhatsApp
WHATSAPP_VERIFY_TOKEN = "tokenfacil123"

WHATSAPP_ACCESS_TOKEN = 'EAFUA6anUjL0BPV3vXG8ZCydhAZBJmsI98OTRMQ7JOcubLpKCR3oLZCzBKsZC6zZAJM9wTwPPZBMGox70CazN2yKmqNXmhf6MMCKyZCuMZAbj6fyTNO0R0SFIE9e7V1BcZC08ZBdEvWG5dZCJwi4Rurf4ycy7ujZBt6r64PdhDOizuLWMuwVCneeGJZAnLk3BLS2FscyZAc0zLlhPKdWBa6qAwXGqE3ni88xh3hxxuY8ZBaZBD5hRM019T5Y9ZCL8KDQqXRMBQZAwZDZD'
WHATSAPP_PHONE_NUMBER_ID = '765888489941122'