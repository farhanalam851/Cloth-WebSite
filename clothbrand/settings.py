"""
Django settings for clothbrand project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------------------------
# SECURITY
# In production, move SECRET_KEY, DEBUG and RAZORPAY keys into real
# environment variables (or a .env file loaded with python-decouple).
# -------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-CHANGE-THIS-BEFORE-GOING-LIVE-a7szzkmps3'
)

DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # local apps
    'accounts',
    'products',
    'cart',
    'orders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'clothbrand.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart_summary',
            ],
        },
    },
]

WSGI_APPLICATION = 'clothbrand.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True


# Static & media files
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Auth redirects
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'products:home'
LOGOUT_REDIRECT_URL = 'products:home'

# Email (console backend for dev; swap to SMTP in production)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'orders@clothbrand.example.com'

# -------------------------------------------------------------------
# Razorpay settings
# Get these from https://dashboard.razorpay.com/app/keys
# Set real values as environment variables before going live.
# -------------------------------------------------------------------
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_XXXXXXXXXXXX')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'YOUR_TEST_SECRET_KEY')
RAZORPAY_CURRENCY = 'INR'

MESSAGE_TAGS = {
    10: 'info', 20: 'success', 25: 'success', 30: 'warning', 40: 'danger',
}
