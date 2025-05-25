# photomosaic/mosaic/admin.py

"""
PURPOSE:
    Registers and customizes Django admin views for pool images management.

DETAILS:
    - Picture: Manages all pool images (with slug for easy lookup).
"""

from django.contrib import admin
from .models import Picture

@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    list_display = ('file', 'slug')
    search_fields = ('file', 'slug')
