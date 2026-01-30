"""
Django settings for youtube_project project.
UTH Hermosillo - Ingeniería en Sistemas 2026
"""

import os
from pathlib import Path

# ===============================
# BASE DIRECTORY
# ===============================
BASE_DIR = Path(__file__).resolve().parent.parent

# ===============================
# YOUTUBE API CONFIG
# ===============================
YOUTUBE_API_KEY = 'AIzaSyCqoDUHs_rvicGdqZ2uOFD9yUQZ7_aQZWo'

GOOGLE_CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, 'client_secrets.json')

GOOGLE_REDIRECT_URI = 'http://localhost:8000/oauth/callback/'

YOUTUBE_SCOPES = [
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/yt-analytics.readonly',
]

# ===============================
# SECURITY
# ===============================
SECRET_KEY = 'django-insecure-p!n3!45=0@^z548*d2ybpks4(2%_sbqmdacegcu^c#5(t8t+%m'
DEBUG = True
ALLOWED_HOSTS = []

# ===============================
# APPLICATIONS
# ===============================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'videos',
]

# ===============================
# MIDDLEWARE (IMPORTANTE)
# ===============================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # ❌ NO XFrameOptionsMiddleware (rompe YouTube iframe)
]

# ===============================
# URLS & TEMPLATES
# ===============================
ROOT_URLCONF = 'youtube_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'youtube_project.wsgi.application'

# ===============================
# DATABASE
# ===============================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ===============================
# PASSWORD VALIDATION
# ===============================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===============================
# INTERNATIONALIZATION
# ===============================
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Hermosillo'
USE_I18N = True
USE_TZ = True

# ===============================
# STATIC & MEDIA FILES
# ===============================
STATIC_URL = 'static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ===============================
# SESSIONS
# ===============================
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 horas

# ===============================
# DEFAULT PK
# ===============================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===============================
# IFRAMES (YOUTUBE FIX)
# ===============================
X_FRAME_OPTIONS = 'ALLOWALL'

# Permitir que el navegador comparta el origen con YouTube
SECURE_REFERRER_POLICY = "no-referrer-when-downgrade"

# Evitar bloqueos de Cross-Origin en navegadores modernos
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"

