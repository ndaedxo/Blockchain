# Blockchain\DIDBlockchain\DIDBlockchain\settings.py
import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
FIELD_ENCRYPTION_KEY = config('FIELD_ENCRYPTION_KEY', default='y8y1QtWB3iRt9tRfnpvb4cNVIz1fLyey06ntJZMegXk=')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY','django-insecure-)hfae9vwhwq(mx-hytwb=b^*)#_6j0sgqqjq42ckcf=30!(d6*')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['*']

LOGIN_URL = '/auth/login/'  # Ensure this matches your URL pattern


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework.authtoken',
    'corsheaders',
    'coreapi',
    'rest_framework',
    'django_extensions',

    'apps.blockchain',
    'apps.api',
    'apps.users',
    'apps.webapp',
    'apps.docs',
    'apps.utils',
    'apps.tests',
    'apps.wallet',

    
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
# Add CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # Only for development
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8001",
]


ROOT_URLCONF = 'DIDBlockchain.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'webapp/templates')],
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

WSGI_APPLICATION = 'DIDBlockchain.wsgi.application'

RUNNING_IN_DOCKER = config("RUNNING_IN_DOCKER", default=False, cast=bool)

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# Environment variables for database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='DIDBlockchain_db'),
        'USER': config('DB_USER', default='thriftstore_user'),
        'PASSWORD': config('DB_PASSWORD', default='Douvretenser30'),
        'HOST': config('DB_HOST',  'db' if RUNNING_IN_DOCKER else 'localhost'),  # This should be 'db' to match your docker-compose service name
        'PORT': config('DB_PORT', default='5432'),
    }
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': config('DB_NAME', default='DIDBlockchain_db'),
#         'USER': config('DB_USER', default='thriftstore_user'),
#         'PASSWORD': config('DB_PASSWORD', default='Douvretenser30'),
#         'HOST': 'localhost',
#         'PORT': config('DB_PORT', default='5432'),
#     }
# }
# GRANT ALL PRIVILEGES ON DATABASE DIDBlockchain_db TO thriftstore_user;
# GRANT ALL PRIVILEGES ON SCHEMA public TO thriftstore_user;


# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/day',
        'user': '1000/day',
    }
}


# Blockchain settings
BLOCKCHAIN_SETTINGS = {
    'MINIMUM_STAKE': 1000,  # Minimum stake required to become a validator
    'BLOCK_TIME': 30,  # Target time between blocks in seconds
    'MAX_TRANSACTIONS_PER_BLOCK': 100,
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.CustomUser'
