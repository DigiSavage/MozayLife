"""
__init__.py

PURPOSE:
    - Ensures that the Celery app is loaded when Django starts,
      so all tasks use the correct app context.

DETAILS:
    - Imports the `app` object from your tasks.py, which registers your Celery configuration.
    - Exposes `celery_app` as the public API for use with Django and Celery integrations.

USAGE:
    - Keep this at the root of your Django app (e.g., `mosaic/`) to ensure
      Celery tasks work across your whole project.

MODERNIZATION NOTES:
    - This is compatible with Django 3+ and Celery 5+.
    - No further changes needed unless you change your tasks app/module structure.
"""

