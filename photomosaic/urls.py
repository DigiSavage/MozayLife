"""
urls.py

PURPOSE:
    Main URL routing for the Photomosaic Django project.

HOW IT WORKS:
    - Defines all root-level URL routes for the project.
    - Connects URLs to views in the mosaic app and admin interface.
    - Handles media file serving in development mode (when DEBUG=True).

MODERNIZATION NOTES:
    - For Django 3+, uses `path` and `re_path` with direct function references (no string view references).
    - Replaces older patterns() and string app references with modern includes and namespaces.
    - Uses Django’s automatic admin site discovery.
"""

# photomosaic/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect
from mosaic import views as mosaic_views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Main menu landing page
    path('', mosaic_views.main_menu, name='main_menu'),

    # Mosaic creation form & handler
    path('home/', mosaic_views.home, name='home'),

    # Remove all uploaded pool images
    path('remove/', mosaic_views.remove, name='remove'),

    # Mosaic results/status page
    path('results/', mosaic_views.results, name='results'),

    # Legacy “/new/” → upload endpoint
    path('new/', lambda r: HttpResponseRedirect('/upload/')),

    # AJAX upload/list/delete namespace
    path('upload/', include(('mosaic.urls', 'mosaic'), namespace='mosaic')),
]

# Serve static & media during development only
if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
