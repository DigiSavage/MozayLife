"""
views.py

PURPOSE:
    Defines all the views/handlers for the Photomosaic Django app.
    Manages image uploads, gallery management, mosaic creation, and async task tracking.

HOW IT WORKS:
    - Handles main mosaic creation form and starts a Celery task.
    - Provides upload gallery via AJAX with JSON responses.
    - Deletes uploaded pictures and local image cleanup.
    - Shows mosaic results including status and generated output.
    - Routes for main menu navigation.

INTERACTIONS:
    - Interacts with `models.py` for Picture ORM objects.
    - Uses `forms.py` for ImageForm for upload validation.
    - Launches Celery task `test_mosaic` from `tasks.py`.
    - Uses Django generic views for AJAX upload handling.
    - Templates used: home.html, main_menu.html, results.html, remove_images.html, error_rm.html
"""

# mosaic/views.py

import os
import re
import glob

from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.generic import CreateView, DeleteView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from celery.result import AsyncResult

from .tasks import test_mosaic
from .models import Picture
from .forms import ImageForm


def orderName(name):
    """Shortens long filenames for display."""
    base = re.sub(r'^.*/', '', name)
    return (base[:10] + '...' + base[-7:]) if len(base) > 20 else base


def home(request):
    """
    GET: show upload/configure form.
    POST: validate inputs, launch Celery mosaic task, store task_id in session, redirect to results.
    """
    if request.method == 'POST':
        # 1) Main image
        main_id = request.POST.get('main_imgfile_id')
        if not main_id:
            return render(request, 'mosaic/home.html', {
                'form': ImageForm(),
                'error': 'Main image is required.'
            })
        try:
            main_pic = Picture.objects.get(id=main_id)
        except Picture.DoesNotExist:
            return render(request, 'mosaic/home.html', {
                'form': ImageForm(),
                'error': 'Invalid main image.'
            })
        main_url = main_pic.file.url

        # 2) Pool images
        raw = request.POST.get('uploaded_image_ids', '')
        pool_ids = [i for i in raw.split(',') if i]
        pool_qs = Picture.objects.filter(id__in=pool_ids)
        pool_urls = [p.file.url for p in pool_qs]
        if not pool_urls:
            return render(request, 'mosaic/home.html', {
                'form': ImageForm(),
                'error': 'Please upload at least one pool image.'
            })

        # 3) Options
        outfile  = request.POST.get('outfile') or 'mosaic.jpg'
        quality  = request.POST.get('quality')
        dimensions = {'low': (15,15), 'med': (35,35), 'high': (55,55)}.get(quality, (35,35))
        shape    = request.POST.get('shape') or 'square'
        artistic = bool(request.POST.get('artistic_effect'))
        fade_val = request.POST.get('fading') or 0
        try:
            fade = float(fade_val) / 100
        except (ValueError, TypeError):
            fade = 0.0

        # 4) Launch Celery task
        task = test_mosaic.delay(
            main_url,
            pool_urls,
            dimensions,
            shape,
            outfile,
            artistic,
            fade
        )
        request.session['task_id'] = task.task_id
        return redirect('mosaic:results')

    # GET
    return render(request, 'mosaic/home.html', {'form': ImageForm()})


@method_decorator(csrf_exempt, name='dispatch')
class PictureCreateView(CreateView):
    """
    AJAX endpoint: accept multiple 'file' uploads at once.
    Returns JSON { files: [ … ] } with each file’s id, url, thumbnailUrl, etc.
    """
    model = Picture
    fields = ['file']

    def post(self, request, *args, **kwargs):
        uploaded = request.FILES.getlist('file')
        files_data = []
        for f in uploaded:
            pic = Picture.objects.create(file=f)
            files_data.append({
                'url': pic.file.url,
                'name': orderName(f.name),
                'type': f.content_type,
                'thumbnailUrl': pic.file.url,
                'size': pic.size,
                'deleteUrl': reverse('mosaic:upload-delete', args=[pic.id]),
                'deleteType': 'DELETE',
                'id': pic.id,
            })
        return JsonResponse({'files': files_data})

    def get(self, request, *args, **kwargs):
        files = []
        for pic in Picture.objects.all():
            files.append({
                'name': orderName(pic.file.name),
                'size': pic.file.size,
                'url': pic.file.url,
                'thumbnailUrl': pic.file.url,
                'deleteUrl': reverse('mosaic:upload-delete', args=[pic.id]),
                'deleteType': 'DELETE',
                'id': pic.id,
            })
        return JsonResponse({'files': files})


@method_decorator(csrf_exempt, name='dispatch')
class PictureDeleteView(DeleteView):
    """
    AJAX endpoint to delete a pool image by its PK.
    """
    model = Picture

    def delete(self, request, *args, **kwargs):
        pic = self.get_object()
        pic.delete()
        return JsonResponse(True, safe=False)


def main_menu(request):
    """Landing page with navigation links."""
    return render(request, 'mosaic/main_menu.html')


def remove(request):
    """
    Wipe out every file under MEDIA_ROOT/pictures/.
    """
    pattern = os.path.join(settings.MEDIA_ROOT, 'pictures', '*')
    for path in glob.glob(pattern):
        try:
            os.remove(path)
        except OSError:
            pass
    return render(request, 'mosaic/remove_images.html')


def results(request):
    """
    Poll Celery task status; if finished, display the mosaic or error.
    Shows spinner and auto-refresh if still running.
    """
    task_id = request.session.get('task_id')
    ready = AsyncResult(task_id).ready() if task_id else False

    s3_url = None
    total_time = None
    error = None

    if ready:
        result = AsyncResult(task_id).result
        if isinstance(result, str) and result.startswith('http'):
            s3_url = result
        elif isinstance(result, (float, int)):
            total_time = result
        else:
            error = str(result)

        # clean up temp uploads at MEDIA_ROOT/upload/
        tmp_pattern = os.path.join(settings.MEDIA_ROOT, 'upload', '*')
        for tmp in glob.glob(tmp_pattern):
            try:
                os.remove(tmp)
            except OSError:
                pass

    return render(request, 'mosaic/results.html', {
        'im': ready,
        's3_url': s3_url,
        'total_time': total_time,
        'error': error,
    })
