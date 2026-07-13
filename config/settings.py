"""
Django settings for config project.
"""

from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================================
# SECURITY
# ==========================================

SECRET_KEY = 'django-insecure-thf2mg%e2%kq*-y^##l3p-%h3eiinb%ldgmxv3#wjc8#tlxh0k'

DEBUG = True

ALLOWED_HOSTS = []


# ==========================================
# APPLICATIONS
# ==========================================

INSTALLED_APPS = [

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'accounts',
]


# ==========================================
# MIDDLEWARE
# ==========================================

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'config.urls'


# ==========================================
# TEMPLATES
# ==========================================

TEMPLATES = [

    {
        'BACKEND':
        'django.template.backends.django.DjangoTemplates',

        'DIRS':
        [BASE_DIR / 'templates'],

        'APP_DIRS':
        True,

        'OPTIONS':
        {

            'context_processors':
            [

                'django.template.context_processors.request',

                'django.contrib.auth.context_processors.auth',

                'django.contrib.messages.context_processors.messages',

            ],

        },
    },
]


WSGI_APPLICATION = 'config.wsgi.application'


# ==========================================
# DATABASE
# ==========================================

DATABASES = {

    'default':
    {

        'ENGINE':
        'django.db.backends.sqlite3',

        'NAME':
        BASE_DIR / 'db.sqlite3',

    }

}



# ==========================================
# PASSWORD VALIDATION
# ==========================================

AUTH_PASSWORD_VALIDATORS = [

    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },

    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
    },

    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },

    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },

]



# ==========================================
# AUTHENTICATION SETTINGS
# ==========================================

# IMPORTANT:
# Your login page is accounts/urls.py -> path("")

LOGIN_URL = "/"

LOGIN_REDIRECT_URL = "/dashboard/"

LOGOUT_REDIRECT_URL = "/"



# ==========================================
# INTERNATIONALIZATION
# ==========================================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Manila'

USE_I18N = True

USE_TZ = True



# ==========================================
# STATIC FILES
# ==========================================

STATIC_URL = 'static/'


STATICFILES_DIRS = [

    BASE_DIR / "static",

]



# ==========================================
# EMAIL SMTP
# ==========================================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"


EMAIL_HOST = "smtp.gmail.com"


EMAIL_PORT = 587


EMAIL_USE_TLS = True


EMAIL_HOST_USER = os.getenv(
    "EMAIL_HOST_USER"
)


EMAIL_HOST_PASSWORD = os.getenv(
    "EMAIL_HOST_PASSWORD"
)


DEFAULT_FROM_EMAIL = EMAIL_HOST_USER



# ==========================================
# SECURITY HARDENING
# ==========================================

# Prevent clickjacking attacks

X_FRAME_OPTIONS = "DENY"


# Cookie security
# Keep False during local testing

SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_HTTPONLY = True



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# Gmail SMTP Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')      # Your sender email
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  # Your App Password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
