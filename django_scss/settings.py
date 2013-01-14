from django.conf import settings


SCSS_EXECUTABLE = getattr(settings, "SCSS_EXECUTABLE", "sass")
SCSS_USE_CACHE = getattr(settings, "SCSS_USE_CACHE", True)
SCSS_CACHE_TIMEOUT = getattr(settings, "SCSS_CACHE_TIMEOUT", 60 * 60 * 24 * 30) # 30 days
SCSS_MTIME_DELAY = getattr(settings, "SCSS_MTIME_DELAY", 10) # 10 seconds
SCSS_ROOT = getattr(settings, "SCSS_ROOT", getattr(settings, "STATIC_ROOT", getattr(settings, "MEDIA_ROOT")))
SCSS_OUTPUT_DIR = getattr(settings, "SCSS_OUTPUT_DIR", "SCSS_CACHE")
SCSS_DEVMODE = getattr(settings, "SCSS_DEVMODE", False)
SCSS_DEVMODE_WATCH_DIRS = getattr(settings, "SCSS_DEVMODE_WATCH_DIRS", [settings.STATIC_ROOT])
SCSS_DEVMODE_EXCLUDE = getattr(settings, "SCSS_DEVMODE_EXCLUDE", ())
SCSS_USE_COMPASS = getattr(settings, "SCSS_USE_COMPASS", False)
