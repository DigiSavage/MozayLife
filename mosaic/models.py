"""
models.py

PURPOSE:
    Django ORM models for image uploads and picture pool management.

HOW IT WORKS:
    - Picture: for all uploaded images (main + pool). 
    - Auto‐generates a unique slug from the filename.
    - Cleans up the file from storage when its model is deleted.

INTERACTIONS:
    - `PictureCreateView` and AJAX upload endpoints save into this model.
    - Home view and FilePond use its `id` and `file.url`.
"""

import os
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.db.models.signals import post_delete
from django.dispatch import receiver


class Picture(models.Model):
    """
    Represents an uploaded image (main or pool).
    - `file`: stored under MEDIA_ROOT/pictures/
    - `slug`: unique identifier derived from the filename.
    """
    file = models.ImageField(upload_to="pictures/")
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def __str__(self):
        return os.path.basename(self.file.name)

    def get_absolute_url(self):
        # Not strictly used, but handy if you ever need it
        return reverse('mosaic:home')

    def save(self, *args, **kwargs):
        # Auto‐generate a unique slug from the filename if missing
        if not self.slug:
            base = slugify(os.path.basename(self.file.name))
            unique = base
            count = 1
            while Picture.objects.filter(slug=unique).exclude(pk=self.pk).exists():
                unique = f"{base[:240]}-{count}"
                count += 1
            self.slug = unique[:255]
        super().save(*args, **kwargs)


@receiver(post_delete, sender=Picture)
def delete_picture_file(sender, instance, **kwargs):
    """
    Deletes file from storage when Picture object is deleted.
    """
    if instance.file:
        instance.file.delete(save=False)
