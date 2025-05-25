#!/usr/bin/env python
"""
manage.py

PURPOSE:
    Django's command-line utility for administrative tasks.
    Used to run the development server, migrate the database, create superusers, collect static files, and more.

HOW IT COMMUNICATES:
    - Sets the DJANGO_SETTINGS_MODULE environment variable to use your project's settings.
    - Delegates all management commands to Django's command-line interface.

PATHS TO CHECK:
    - No custom paths; uses the current directory context.
    - Relies on 'photomosaic.settings' as the settings module (update if your project folder changes).

MODERNIZATION NOTES:
    - Compatible with both Python 2 and 3.
    - For Python 2, the 'from exc' part in exception chaining can be omitted (safe to leave as-is if using Python 3).

USAGE:
    python manage.py runserver         # Start development server
    python manage.py migrate           # Apply migrations
    python manage.py createsuperuser   # Create admin user
    python manage.py collectstatic     # Collect static files
    # ...and more (see 'python manage.py help')

Author: MozayLab Project
"""

import os
from dotenv import load_dotenv

# Loads .env from the same directory as manage.py
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

import sys

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "photomosaic.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
