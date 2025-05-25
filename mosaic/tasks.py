# mosaic/tasks.py

from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

# Ensure Django settings are loaded for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photomosaic.settings')

# --- Import photomosaic engine ---
try:
    from photomosaic_exec import photomosaic as pm
except ImportError as e:
    pm = None
    print("ERROR: Could not import photomosaic_exec.photomosaic. Make sure it is installed and importable.", e)

app = Celery('mosaic_task')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def test_mosaic(self, main_img_path, pool_image_paths, dimensions, shape, fileout, artistic, bending):
    """
    Asynchronously generates a photomosaic and uploads the result to AWS S3.
    Returns the S3 URL.
    """
    if pm is None:
        self.update_state(state='FAILURE', meta={'exc': 'photomosaic_exec not installed'})
        return 'photomosaic_exec not installed'
    try:
        # 1. Create PhotoMosaic instance (no tile_images arg)
        mypm = pm.PhotoMosaic(
            main_img_path,
            dimensions,
            shape
        )

        # 2. (Optional) If your API allows, load your pool images here:
        # mypm.load_tiles_from_list(pool_image_paths)
        # — consult photomosaic_exec docs for the correct method.

        # 3. Partition
        if artistic and shape == 'square':
            mypm.partition(depth=2)
        else:
            mypm.partition()

        # 4. Analyze & build
        mypm.analyze()
        mypm.choose_match()
        mypm.mosaic()

        # 5. Fading
        if bending:
            mypm.fading(bending)

        # 6. Save locally
        results_path = os.path.join(settings.MEDIA_ROOT, 'results')
        os.makedirs(results_path, exist_ok=True)
        local_result_path = os.path.join(results_path, fileout or 'mosaic.jpg')
        mypm.imsave(local_result_path)

        # 7. Upload to S3
        s3_bucket = os.environ.get('AWS_BUCKET', settings.AWS_STORAGE_BUCKET_NAME)
        s3_key    = 'results/' + os.path.basename(local_result_path)
        pm.upload_to_s3(
            local_path=local_result_path,
            s3_bucket=s3_bucket,
            s3_key=s3_key,
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region=os.environ.get('AWS_REGION', settings.AWS_REGION)
        )

        return f"https://{s3_bucket}.s3.{os.environ.get('AWS_REGION', settings.AWS_REGION)}.amazonaws.com/{s3_key}"

    except Exception as e:
        self.update_state(state='FAILURE', meta={'exc': str(e)})
        return str(e)
