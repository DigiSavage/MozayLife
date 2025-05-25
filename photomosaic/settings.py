# settings.py

"""
settings.py

PURPOSE:
    Core Django settings for the Photomosaic Project.
    Configures database, static/media files, installed apps, middleware,
    Celery with Redis as broker/backend, and essential security and localization settings.

HOW IT WORKS:
    - Defines BASE_DIR for file paths.
    - Loads environment variables from .env via python-dotenv.
    - Configures MariaDB using environment variables.
    - Sets up static and media file handling.
    - Integrates Celery for asynchronous task processing using Redis.
    - Configures S3 storage for media uploads via django-storages.
    - Registers installed Django and third-party apps.
    - Configures templates, middleware, and logging.

INTERACTIONS:
    - DATABASES connects to MariaDB for application data.
    - CELERY uses Redis for task queue and result backend.
    - STATIC and MEDIA settings govern asset serving.
    - DEFAULT_FILE_STORAGE points to S3Boto3Storage for uploaded media.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ── Build paths inside the project: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ── Load environment variables from .env at project root
env_path = BASE_DIR / '.env'
if env_path.exists():
    load_dotenv(env_path)

# ── SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY environment variable not set")

# ── SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() in ('1', 'true', 'yes')

# ── Hosts/domain names that this Django site can serve
ALLOWED_HOSTS = [
    host.strip() for host in os.getenv('ALLOWED_HOSTS', '').split(',')
    if host.strip()
] or ['localhost', '127.0.0.1']

# ── Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mosaic',
    'storages',           # Required for S3 storage
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'photomosaic.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'mosaic' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'photomosaic.wsgi.application'

# ── Database configuration (MariaDB)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DATABASE_NAME', ''),
        'USER': os.getenv('DATABASE_USER', ''),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', ''),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', '3306'),
        'OPTIONS': {
            'init_command': 'SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED',
        },
    }
}

# ── Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_L10N = True
USE_TZ = True
SITE_ID = 1

# ── Static files (CSS, JavaScript, Images)
STATIC_URL = os.getenv('STATIC_URL', '/static/')
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# ── Media files (user uploads)
MEDIA_URL = os.getenv('MEDIA_URL', '/media/')
MEDIA_ROOT = BASE_DIR / 'media'

# ── AWS S3 settings for media storage
AWS_ACCESS_KEY_ID       = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY   = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_BUCKET')
AWS_S3_REGION_NAME      = os.getenv('AWS_REGION', 'us-east-1')
AWS_QUERYSTRING_AUTH    = False  # Publicly readable
DEFAULT_FILE_STORAGE    = 'storages.backends.s3boto3.S3Boto3Storage'

# ── Celery configuration (using Redis)
CELERY_BROKER_URL        = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND    = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT    = ['json']
CELERY_TASK_SERIALIZER   = 'json'
CELERY_RESULT_SERIALIZER = 'json'

print("Celery will use broker:", CELERY_BROKER_URL)

# ── File upload permissions
FILE_UPLOAD_PERMISSIONS = 0o664

# ── Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
