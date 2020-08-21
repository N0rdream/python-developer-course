from .base import *


DEBUG = True

SECRET_KEY = 'secret'

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, 'static_cdn')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_cdn')

INTERNAL_IPS = ['10.0.2.2', '10.0.2.15']
INSTALLED_APPS += ['debug_toolbar',]
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware',]

DEBUG_TOOLBAR_CONFIG = {
    'JQUERY_URL': '/static/jquery-3.3.1.min.js'
}