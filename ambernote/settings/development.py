from .common import *  # noqa

DEBUG = True

# django-debug-toolbar
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#explicit-setup

INTERNAL_IPS = ['127.0.0.1']

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# whitenoise
# https://whitenoise.evans.io/en/stable/django.html

INSTALLED_APPS.insert(
    # insert whitenoise before staticfiles
    INSTALLED_APPS.index('django.contrib.staticfiles'),
    'whitenoise.runserver_nostatic',
)

# Fake email backend for development
# https://docs.djangoproject.com/en/4.1/topics/email/#console-backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
