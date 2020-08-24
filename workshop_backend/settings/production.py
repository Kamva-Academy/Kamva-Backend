from workshop_backend.settings.base import *


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
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logging/debug.log'),
        },
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': LOG_LEVEL,
            'propagate': True
        },
        'django': {
            'handlers': ['file'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'workshop_backend': {
            'handlers': ['file'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
    },
}

TESTING = False

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
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