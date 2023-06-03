from datetime import timedelta
from kamva_backend.settings.base import *

DEBUG = get_environment_var('DEBUG', 'False') == 'True'

SECRET_KEY = get_environment_var(
    'SECRET_KEY', '*z!3aidedw32xh&1ew(^&5dgd17(ynnmk=s*mo=v2l_(4t_ff(')

ALLOWED_HOSTS = get_environment_var('ALLOWED_HOSTS', '*').split(',')

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

STATIC_ROOT = os.path.join(BASE_DIR, get_environment_var(
    'STATIC_ROOT_FILE_NAME', 'staticfiles'))
# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, 'media'),
# )

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
        'kamva_backend': {
            'handlers': ['file', 'console'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
    },
}

TESTING = False


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
    'MERCHANT': '817461df-e332-4657-85d1-76e7e0a06f0e',  # Required
    'DESCRIPTION': ''  # Required
}

PAYMENT = {
    'FRONT_HOST_SUCCESS': 'https://kamva.academy/message/payment/success',
    'FRONT_HOST_FAILURE': 'https://kamva.academy/message/payment/failure',
}

SWAGGER_URL = 'https://backend.rastaiha.ir/api/'

CSRF_TRUSTED_ORIGINS = get_environment_var('CSRF_TRUSTED_ORIGINS', '*').split(',')

DEFAULT_FILE_STORAGE = "minio_storage.storage.MinioMediaStorage"
# STATICFILES_STORAGE = "minio_storage.storage.MinioStaticStorage"
MINIO_STORAGE_ENDPOINT = get_environment_var('MINIO_STORAGE_ENDPOINT', None)
MINIO_STORAGE_ACCESS_KEY = get_environment_var(
    'MINIO_STORAGE_ACCESS_KEY', None)
MINIO_STORAGE_SECRET_KEY = get_environment_var(
    'MINIO_STORAGE_SECRET_KEY', None)
MINIO_STORAGE_USE_HTTPS = True
MINIO_STORAGE_MEDIA_BUCKET_NAME = 'media'
MINIO_STORAGE_STATIC_BUCKET_NAME = 'static'
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True
MINIO_STORAGE_AUTO_CREATE_STATIC_BUCKET = True
