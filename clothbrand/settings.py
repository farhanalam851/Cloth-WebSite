"""
Django settings for clothbrand project.
"""

from decimal import Decimal
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------------------------
# SECURITY
# These are read from a `.env` file in the project root (same folder
# as manage.py) if one exists, otherwise from real environment
# variables, otherwise the defaults below are used.
# -------------------------------------------------------------------
SECRET_KEY = config(
    'DJANGO_SECRET_KEY',
    default='django-insecure-CHANGE-THIS-BEFORE-GOING-LIVE-a7szzkmps3'
)

DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=Csv())


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
# Get these from https://dashboard.razorpay.com/app/keys and put them
# in a `.env` file in the project root (see .env.example).
# -------------------------------------------------------------------
RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID', default='rzp_test_XXXXXXXXXXXX')
RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET', default='YOUR_TEST_SECRET_KEY')
RAZORPAY_CURRENCY = 'INR'

# -------------------------------------------------------------------
# Shipping & tax
# Flat shipping rate applied to every order, and a GST percentage applied
# to the order subtotal. Change these to match your client's actual
# rates, or wire them up to be editable from the admin later if needed.
# -------------------------------------------------------------------
SHIPPING_FLAT_RATE = Decimal(config('SHIPPING_FLAT_RATE', default='99.00'))
TAX_RATE_PERCENT = Decimal(config('TAX_RATE_PERCENT', default='18.00'))  # standard GST slab

MESSAGE_TAGS = {
    10: 'info', 20: 'success', 25: 'success', 30: 'warning', 40: 'danger',
}
