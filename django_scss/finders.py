from django_scss.storage import SCSSFileStorage
from django.contrib.staticfiles.finders import BaseStorageFinder


class SCSSFinder(BaseStorageFinder):
    """
    A staticfiles finder that looks in SCSS_ROOT
    for compiled files, to be used during development
    with staticfiles development file server or during
    deployment.
    """
    storage = SCSSFileStorage

    def list(self, ignore_patterns):
        return []
