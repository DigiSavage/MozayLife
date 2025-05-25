"""
celery.py

PURPOSE:
    Configure and initialize Celery for the Photomosaic Django project.
    Sets up the Celery application to enable asynchronous task processing.

HOW IT WORKS:
    - Defines a Celery app named 'photomosaic' representing the Django project.
    - Loads Django settings module for Celery configuration using the 'CELERY_' prefix.
    - Auto-discovers task modules from all installed Django apps (e.g., mosaic/tasks.py).
    - Ensures Celery uses Django's timezone settings for correct time-related operations.
    - Exposes the Celery app instance for use in worker startup commands.
"""

# photomosaic/celery.py

import os
from celery import Celery
from django.conf import settings

# 1. Tell Celery which settings module to use
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photomosaic.settings')

# 2. Create the Celery app instance
app = Celery('photomosaic')

# 3. Pull in any Celery-related settings defined in Django settings.py,
#    e.g. CELERY_BROKER_URL, CELERY_RESULT_BACKEND, etc.
app.config_from_object('django.conf:settings', namespace='CELERY')

# 4. Auto-discover tasks from all INSTALLED_APPS
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# 5. Use your Django project's TIME_ZONE (instead of UTC)
app.conf.enable_utc = False
app.conf.timezone = settings.TIME_ZONE

# 6. A small debug task you can call with `app.send_task('ping')`
@app.task(name='ping')
def ping():
    return 'pong'
