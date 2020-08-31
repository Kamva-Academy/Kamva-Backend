from workshop_backend.settings.base import *
import sys
####import django_heroku
from datetime import timedelta

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*z!3aidedw32xh&1ew(^&5dgd17(ynnmk=s*mo=v2l_(4t_ff('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

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
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'workshop_backend': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

TESTING = sys.argv[1] == 'test'
# TESTING = True

# Activate Django-Heroku.
####django_heroku.settings(locals(), test_runner=False)
####DOMAIN = get_environment_var('DOMAIN', 'http://kabaraamadalapeste.herokuapp.com')

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    },
}

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

ZARINPAL_CONFIG = {
    'ROUTE_START_PAY': 'https://sandbox.zarinpal.com/pg/StartPay/',
    'ROUTE_WEB_GATE': 'https://sandbox.zarinpal.com/pg/services/WebGate/wsdl',
    'TEAM_FEE': int(get_environment_var('TEAM_FEE', '255000')),  # Required
    'PERSON_FEE': int(get_environment_var('PERSON_FEE', '100000')),  # Required
    'MERCHANT': 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX',  # Required
    'DESCRIPTION': 'ثبت‌نام در رویداد «مدرسه تابستانه رستا» به صورت آزمایشی'  # Required
}
PAYMENT = {
    'FRONT_HOST_SUCCESS': 'https://rastaiha.ir/payment/success/',
    'FRONT_HOST_FAILURE': 'https://rastaiha.ir/payment/failure/'
}
