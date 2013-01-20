from django.core.files.storage import FileSystemStorage
from django_scss.settings import SCSS_ROOT


class SCSSFileStorage(FileSystemStorage):
    """
    Standard file system storage for files handled by django-scss.

    The default for ``location`` is ``SCSS_ROOT``
    """
    def __init__(self, location=None, base_url=None, *args, **kwargs):
        if location is None:
            location = SCSS_ROOT
        super(SCSSFileStorage, self).__init__(location, base_url,
                                                *args, **kwargs)
