# photomosaic/__init__.py

"""
PURPOSE:
    This file ensures that the Celery application instance is imported
    whenever Django starts. This is critical so that Celery tasks are
    registered and ready for use throughout your project.

HOW IT WORKS:
    - Imports the Celery app object from celery.py (or celery_app.py if renamed).
    - Makes sure Celery integration is initialized on Django startup.

INTERACTIONS:
    - Imports Celery app from photomosaic/celery.py (or photomosaic/celery_app.py).
    - Called implicitly by Django when starting server or running management commands.
"""

from .celery import app as celery_app
__all__ = ('celery_app',)
