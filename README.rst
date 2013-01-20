Django SCSS
===================

Django SCSS provides template tags to compile SCSS into CSS from templates.
It works with both inline code and extenal files.

Installation
************

1. Add "django_scss" to INSTALLED_APPS setting.
2. Make sure that you have sass executable installed. See SASS official site for details.
3. Optionally, you can specify the full path to sass executable with SCSS_EXECUTABLE setting. By default it's set to sass.
4. In case you use Django’s staticfiles contrib app you have to add django-scss’s file finder to the ``STATICFILES_FINDERS`` setting, for example :

::

    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        # other finders..
        'django_scss.finders.SCSSFinder',
    )


Example Usage
*************

Inline
------

::

    {% load scss %}

    <style>
      {% inlinescss %}
        #header {
          h1 {
            font-size: 26px;
            font-weight: bold;
          }
          p { font-size: 12px;
            a { text-decoration: none;
              &:hover { border-width: 1px }
            }
          }
        }
      {% endinlinescss %}
    </style>

renders to

::

      <style>
        #header h1 {
          font-size: 26px;
          font-weight: bold; }
        #header p {
          font-size: 12px; }
          #header p a {
            text-decoration: none; }
            #header p a:hover {
              border-width: 1px; }
      </style>


External file
-------------

::

    {% load scss %}

    <link rel="stylesheet" href="{{ STATIC_URL}}{% scss "path/to/styles.scss" %}" />

renders to

::

    <link rel="stylesheet" href="/media/SCSS_CACHE/path/to/styles-91ce1f66f583.css" />

Note that by default compiled files are saved into ``SCSS_CACHE`` folder under your ``STATIC_ROOT`` (or ``MEDIA_ROOT`` if you have no ``STATIC_ROOT`` in your settings).
You can change this folder with ``SCSS_ROOT`` and ``SCSS_OUTPUT_DIR`` settings.

Note that all relative URLs in your stylesheet are converted to absolute URLs using your ``STATIC_URL`` setting.


Settings
********

``SCSS_EXECUTABLE``
    Path to SASS compiler executable. Default: "sass".

``SCSS_ROOT``
    Controls the absolute file path that compiled files will be written to. Default: ``STATIC_ROOT``.

``SCSS_OUTPUT_DIR``
    Controls the directory inside ``SCSS_ROOT`` that compiled files will be written to. Default: ``"SCSS_CACHE"``.

``SCSS_USE_CACHE``
    Whether to use cache for inline styles. Default: ``True``.

``SCSS_CACHE_TIMEOUT``
    Cache timeout for inline styles (in seconds). Default: 30 days.

``SCSS_MTIME_DELAY``
    Cache timeout for reading the modification time of external stylesheets (in seconds). Default: 10 seconds.

``SCSS_USE_COMPASS``
    Boolean. Wheter to use compass or not. Compass must be installed in your system. Run "sass --compass" and if no error is shown it means that compass is installed.
