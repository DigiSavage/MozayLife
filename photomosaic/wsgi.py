"""
wsgi.py

PURPOSE:
    WSGI entrypoint for the Photomosaic Django project.

HOW IT WORKS:
    - Exposes the WSGI application object that Django uses for the development server and that production WSGI servers (Gunicorn, uWSGI, etc.) will use.
    - Sets up the DJANGO_SETTINGS_MODULE environment variable if not already set.

USAGE:
    - Required by any WSGI server hosting this Django project.
    - Do not rename or remove from the root Django project folder.

MODERNIZATION NOTES:
    - No changes needed for Django 3.2+.
    - WSGI middleware can be added after the `get_wsgi_application()` line if desired.
"""

import os

# Set the default Django settings module for the 'photomosaic' project.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "photomosaic.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

# Optional: Apply custom WSGI middleware here
# Example:
# from my_middleware import SomeWSGIMiddleware
# application = SomeWSGIMiddleware(application)