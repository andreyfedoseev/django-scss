from django_scss.settings import SCSS_DEVMODE


if SCSS_DEVMODE:
    # Run the devmode daemon if it's enabled.
    # We start it here because this file is auto imported by Django when
    # devserver is started.
    from django_scss.devmode import start_daemon
    start_daemon()
