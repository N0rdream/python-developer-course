from .base import *


DEBUG = False

SECRET_KEY = os.getenv('SECRET_KEY')

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('HASKER_DATABASE_NAME'),
        'USER': os.getenv('HASKER_DATABASE_USER'),
        'PASSWORD': os.getenv('HASKER_DATABASE_PASSWORD'),
        'HOST': os.getenv('HASKER_DATABASE_HOST'),
        'PORT': os.getenv('HASKER_DATABASE_PORT')
    }
}

STATIC_ROOT = os.getenv('STATIC_ROOT')
MEDIA_ROOT = os.getenv('MEDIA_ROOT')
