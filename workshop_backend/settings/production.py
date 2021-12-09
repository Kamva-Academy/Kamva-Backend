from workshop_backend.settings.base import *
import redis


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_environment_var('DEBUG', 'False') == 'True'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_environment_var('SECRET_KEY', '*z!3aidedw32xh&1ew(^&5dgd17(ynnmk=s*mo=v2l_(4t_ff(')

ALLOWED_HOSTS = get_environment_var('ALLOWED_HOSTS', '*').split(',')

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DB_NAME = get_environment_var('DB_NAME', 'workshop')
DB_USER = get_environment_var('DB_USER', 'user')
DB_PASS = get_environment_var('DB_PASS', 'p4s$pAsS')
DB_HOST = get_environment_var('DB_HOST', 'localhost')
DB_PORT = get_environment_var('DB_PORT', '5432')

REDIS_HOST = get_environment_var('REDIS_HOST', 'localhost')
REDIS_PORT = get_environment_var('REDIS_PORT', '6379')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}


STATIC_ROOT = get_environment_var('STATIC_ROOT', 'staticfiles')
LOG_LEVEL = get_environment_var('LOG_LEVEL', 'INFO')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)-8s [%(module)s:%(funcName)s:%(lineno)d]: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(BASE_DIR, 'logging/debug.log'),
        },
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': LOG_LEVEL,
            'propagate': True
        },
        'django': {
            'handlers': ['file', 'console'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'workshop_backend': {
            'handlers': ['file', 'console'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
    },
}

TESTING = False

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('JWT',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

ZARINPAL_CONFIG = {
    'ROUTE_START_PAY': 'https://www.zarinpal.com/pg/StartPay/',
    'ROUTE_WEB_GATE': 'https://www.zarinpal.com/pg/services/WebGate/wsdl',
    'TEAM_FEE': int(get_environment_var('TEAM_FEE', '255000')),  # Required
    'PERSON_FEE': int(get_environment_var('PERSON_FEE', '100000')),  # Required
    'MERCHANT': '8b469980-683d-11ea-806a-000c295eb8fc',  # Required
    'DESCRIPTION': 'ثبت‌نام در رویداد «رستاخیز: روز صفر»'  # Required
}

PAYMENT = {
    'FRONT_HOST_SUCCESS': 'https://academy.rastaiha.ir/message/payment/success',
    'FRONT_HOST_FAILURE': 'https://academy.rastaiha.ir/message/payment/failure',
}

REDIS_URL = get_environment_var('REDIS_URL', 'redis://localhost:6379')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    },
}

SWAGGER_URL = 'backend.rastaiha.ir/api/'
