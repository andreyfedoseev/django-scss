from django.conf.global_settings import *
import os


DEBUG = True

STATIC_ROOT = MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'static')
STATIC_URL = MEDIA_URL = "/static/"

STATICFILES_DIRS = (
    os.path.join(os.path.dirname(__file__), 'staticfiles_dir'),
    ("prefix", os.path.join(os.path.dirname(__file__), 'staticfiles_dir_with_prefix')),
)

SECRET_KEY = "SECRET_KEY"

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
