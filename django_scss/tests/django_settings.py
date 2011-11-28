from django.conf.global_settings import *
import os


STATIC_ROOT = MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')
STATIC_URL = MEDIA_URL = "/media/"
INSTALLED_APPS = (
    "django_scss",
)
SCSS_MTIME_DELAY = 2
SCSS_OUTPUT_DIR = "SCSS_CACHE"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
        },
    },
    'loggers': {
        'django_scss': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}
