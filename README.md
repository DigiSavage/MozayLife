<<<<<<< HEAD
# MozayLife
=======

PhotoMozay Web App

A Django-powered web application for generating photomosaics from user-uploaded images, featuring a high-performance, MongoDB-backed Python/Cython core for fast, high-quality mosaic rendering.

⸻

Table of Contents
	•	Overview
	•	Architecture & Project Structure
	•	How the App Works
	•	Account & Resource Setup
	•	MySQL/MariaDB
	•	MongoDB
	•	AWS S3 (Optional)
	•	Environment Variables & Secrets
	•	EC2 Deployment: Step-by-Step
	•	Production Checklist
	•	Modernization & Maintenance
	•	Troubleshooting
	•	Credits & License

⸻

Overview

PhotoMosaic Web App enables users to:
	•	Upload and manage image pools via a web UI.
	•	Select a main (target) image and generate a high-resolution photomosaic using advanced color-matching algorithms.
	•	View and download results, and optionally store finished mosaics in AWS S3 for scalability.

Tech Stack:
	•	Back End: Django, Cython/Python, MySQL/MariaDB, MongoDB, Celery (optional)
	•	Front End: Bootstrap, jQuery, blueimp file uploader, custom JS/CSS
	•	Storage: Local filesystem or AWS S3 (for uploads/results)


Architecture & Project Structure

photomosaic/                    # Project root
├── manage.py                   # Django manage script
├── photomosaic/                # Django project config: settings, URLs, WSGI
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── mosaic/                     # Main app: views, forms, models, templates
│   ├── static/                 # JS, CSS, images
│   ├── templates/              # HTML templates (base, home, results, etc.)
│   ├── templatetags/           # Custom template tags
│   ├── views.py, models.py, ...# Core Django app logic
├── media/                      # Uploaded images & output mosaics
│   └── results/completed/
├── PhotoMosaic_source/         # Mosaic engine: Cython/Python/C code
│   ├── color_metrics/          # Color math (C/Cython)
│   ├── photomosaic.py, ...     # Image engine modules
│   └── setup.py                # Build script for Cython
├── photomosaic_exec/           # Compiled engine modules (after build)
├── requirements.txt            # Python dependencies
└── README.md                   # This documentation



How the App Works

User Flow:
1. Main Menu: Upload images, remove old images, or start creating a new mosaic.
2. Image Upload: Multi-file upload (drag-and-drop), stored in media/ and indexed in MongoDB.
3. Mosaic Generation: User selects main image and config (tile size, shape, transparency, etc.), triggers engine.
4. Processing: Backend partitions image, analyzes tile colors, finds best match for each tile using MongoDB, and assembles the mosaic in parallel.
5. Results: Mosaic saved to media/results/completed/ (or S3), preview/download link shown.

Admin:
	•	Django admin enabled for advanced image/user management.

⸻

Account & Resource Setup

MySQL/MariaDB

	•	Install MariaDB:

sudo apt update
sudo apt install mariadb-server
sudo mysql_secure_installation

	•	Create DB & user:
CREATE DATABASE mozay CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'mozayuser'@'localhost' IDENTIFIED BY 'YOUR_STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON mozay.* TO 'mozayuser'@'localhost';
FLUSH PRIVILEGES;


	•	Update photomosaic/settings.py:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mozay',
        'USER': 'mozayuser',
        'PASSWORD': 'YOUR_STRONG_PASSWORD',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}



MongoDB
	•	Install MongoDB locally or use MongoDB Atlas:

sudo apt update
sudo apt install -y mongodb
sudo systemctl enable mongodb
sudo systemctl start mongodb


	•	Atlas Example connection URI:
mongodb+srv://<user>:<pass>@mozaylab.c1hgdgz.mongodb.net/?retryWrites=true&w=majority&appName=MozayLab


	•	Update MongoDB connection in your Python code (where MongoClient is called).

AWS S3 (Optional)
	•	Create bucket (e.g., mozaylab) and IAM user with programmatic access.
	•	Note the Access Key ID, Secret Access Key, and region.
	•	Install django-storages:

pip install django-storages[boto3]



	•	Add to settings.py:
INSTALLED_APPS += ['storages']
AWS_ACCESS_KEY_ID = '...'
AWS_SECRET_ACCESS_KEY = '...'
AWS_STORAGE_BUCKET_NAME = 'mozaylab'
AWS_S3_REGION_NAME = 'us-east-1'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'


	•	Sync media/ to S3 (optional):
aws s3 sync media/ s3://mozaylab/media/



***************

Environment Variables & Secrets

Store all credentials outside of settings.py using environment variables or a .env file:
	•	DJANGO_SECRET_KEY
	•	DJANGO_DEBUG
	•	DJANGO_ALLOWED_HOSTS
	•	MYSQL_USER, MYSQL_PASSWORD
	•	MONGO_URI
	•	AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

Never commit passwords or keys to Git!

⸻
***************

EC2 Deployment: Step-by-Step

Assuming an Ubuntu EC2 instance with SSH access.

	1.	System Setup
sudo apt update && sudo apt upgrade -y
sudo apt install python2.7 python2.7-dev python-pip build-essential cython \
    mariadb-server libmysqlclient-dev mongodb nodejs npm git

	2.	Clone Repo & Setup
git clone https://github.com/youruser/photomosaic.git
cd photomosaic

	3.	Virtual Environment
pip install virtualenv
virtualenv venv
source venv/bin/activate


	4.	Install Requirements
pip install -r requirements.txt
pip install mysqlclient

	5.	Build Cython Modules
cd PhotoMosaic_source
python setup.py build_ext --inplace
cd ..

	6.	Django Migrations
python manage.py migrate
python manage.py collectstatic


	7.	Create Superuser
python manage.py createsuperuser


	8.	Prepare Directories
mkdir -p media/results/completed
mkdir -p static

	9.	Run Dev Server
python manage.py runserver


	10.	Production: Gunicorn & nginx
	•	Install Gunicorn:
pip install gunicorn
gunicorn photomosaic.wsgi:application --bind 0.0.0.0:8000



	•	Configure nginx to proxy to Gunicorn and serve /media/ and /static/.

⸻

Production Checklist
	•	All secrets/keys secured via environment variables.
	•	DEBUG = False, ALLOWED_HOSTS set to your domain.
	•	MariaDB and MongoDB running and accessible.
	•	Media and static paths are correct and writable.
	•	(Optional) S3 is syncing correctly.
	•	Python 3 upgrade highly recommended for long-term maintenance.
	•	HTTPS enabled (Let’s Encrypt).

⸻

Modernization & Maintenance
	•	Python 3:
Refactor all code for Python 3 compatibility (e.g., xrange → range, print function, exception syntax, imports, etc.).
	•	Cython Modules:
Rebuild using Python 3 and Cython; test all dependencies.
	•	Frontend:
Use modern JS bundlers (Webpack, Parcel) to consolidate and minify JS/CSS.
	•	Security:
Never store secrets in code or repo. Rotate keys regularly.
	•	Backups:
Backup MongoDB and media (or use S3 versioning).

⸻

Troubleshooting
	•	Static/media not served: Check nginx config, STATIC_URL, MEDIA_URL, and permissions.
	•	Database errors: Confirm MariaDB and MongoDB are running and credentials are correct.
	•	Cython build errors: Ensure all dependencies and Python/C headers are installed.
	•	Permission issues: Ensure media/static dirs are writable by the web process.
	•	Missing modules: Rebuild engine with python setup.py build_ext --inplace.

⸻

Credits & License
	•	Photomosaic core: Adapted from open source projects (see code attributions).
	•	Frontend: blueimp, jQuery, Bootstrap, and other OSS libraries.
	•	License: See LICENSE file for open-source license details.

⸻

How Everything Relates
	•	Django Layer (photomosaic/, mosaic/): Handles UI, file uploads, triggers mosaic engine.
	•	PhotoMosaic Engine (PhotoMosaic_source/): Performs all color analysis and image assembly.
	•	Databases:
	•	MariaDB: Django’s default ORM DB (users, sessions, admin).
	•	MongoDB: Used by engine for fast tile/pool image matching.
	•	Static/Media: Served locally or via S3, required for user uploads/results.
	•	Template Tags: Custom UI widgets (drag-and-drop, previews) for user convenience.
	•	Structure: Separation of web, engine, and compiled code ensures maintainability and scalability.

















PhotoMosaic Web App
A Django-powered web application for generating photomosaics from user-uploaded images, featuring a highly parallel, MongoDB-backed Python/Cython core for fast, high-quality mosaic rendering.

Table of Contents
Project Overview

Architecture & File Structure

How the App Works

Account & Resource Setup

MySQL User/DB

MongoDB Database

AWS S3 Bucket

Environment Variables & Secrets

EC2 Deployment: Step-by-Step

Production Checklist

Modernization & Maintenance

Troubleshooting

License

Project Overview
This project enables users to:

Upload and manage image pools via a web UI

Select a source image and generate a high-resolution photomosaic using advanced color-matching algorithms

View and download results

Back End: Django, Cython, Python, MySQL, MongoDB
Front End: Bootstrap, jQuery, blueimp file uploader, custom JS/CSS
Storage: Local filesystem for uploads and mosaics; (optionally) AWS S3 for scalable storage

Architecture & File Structure

photomosaic/
├── manage.py
├── photomosaic/            # Django project settings, URLs, WSGI
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── mosaic/                 # Main Django app (views, forms, models)
│   ├── static/             # All static assets (js, css, images)
│   ├── templates/          # HTML templates (extends base.html)
│   ├── templatetags/       # Custom template tags (e.g., upload_tags)
│   └── ...                 # Other Django app files
├── media/                  # Uploaded and result images (auto-created)
│   └── results/completed/  # Output mosaics
├── PhotoMosaic_source/     # Core mosaic engine (Python/Cython)
│   ├── color_metrics/      # Color distance C/Cython code
│   ├── ...                 # Jigsaw, memo, directory_walker, etc.
│   └── setup.py
├── photomosaic_exec/       # Compiled Cython modules (after build)
├── requirements.txt
└── README.md


How the App Works
Users visit the web app:

Main menu lets users upload images, remove images, and create mosaics.

Image upload:

Images are stored in media/, indexed in MongoDB for fast access.

Mosaic generation:

The user selects an image, chooses shape and settings, and launches the process.

The mosaic engine tiles the image, analyzes colors, matches each tile with the closest pool image, and generates the mosaic (using parallelism for speed).

Results:

The mosaic is saved to media/results/completed/ and shown to the user.

Optional S3 Storage:

For scalable deployments, you can sync media/ to AWS S3 using tools like django-storages.

Account & Resource Setup
MySQL User/DB
Install MySQL:
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation


Create database and user:
mysql -u root -p

CREATE DATABASE mozay CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'mozayuser'@'localhost' IDENTIFIED BY 'YOUR_STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON mozay.* TO 'mozayuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;


Update photomosaic/settings.py:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mozay',
        'USER': 'mozayuser',
        'PASSWORD': 'YOUR_STRONG_PASSWORD',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            "init_command": "SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED"
        },
    }
}




MongoDB Database
Install MongoDB:
sudo apt update
sudo apt install -y mongodb
sudo systemctl enable mongodb
sudo systemctl start mongodb


(Optional) Secure MongoDB & create user:

By default, this app uses the jobs database and doesn't require authentication. For production, add a user:
mongo
use jobs
db.createUser({ user: "mosaicuser", pwd: "YOUR_MONGO_PASS", roles: [ { role: "readWrite", db: "jobs" } ] })


Update connection URI in Python if needed:
MONGO_URI = "mongodb://mosaicuser:YOUR_MONGO_PASS@localhost:27017/jobs"




AWS S3 Bucket (Optional, for production media storage)
Create a bucket:

Log in to AWS Console > S3 > Create bucket (e.g., mozaylab).

Set up bucket policy for public or authenticated access as appropriate.

Create an IAM user for Django:

AWS IAM > Users > Add user (programmatic access).

Attach policy for S3 full access (or limited to your bucket).

Note the Access Key ID and Secret Access Key.



Install and configure django-storages:
pip install django-storages[boto3]


Add to settings.py:
INSTALLED_APPS += ['storages']

AWS_ACCESS_KEY_ID = '...'
AWS_SECRET_ACCESS_KEY = '...'
AWS_STORAGE_BUCKET_NAME = 'mozaylab'
AWS_S3_REGION_NAME = 'us-east-1'  # adjust as needed
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'



Sync old media:
aws s3 sync media/ s3://mozaylab/media/



Environment Variables & Secrets
Set the following as ENV variables or in a .env file (with django-environ):

DJANGO_SECRET_KEY

DJANGO_DEBUG

DJANGO_ALLOWED_HOSTS

MYSQL_USER, MYSQL_PASSWORD

MONGO_URI

AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY (if using S3)

Never commit passwords or secret keys to version control!




EC2 Deployment: Step-by-Step

Assumes a clean Ubuntu EC2 instance with SSH access.

1. Update and install system dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install python2.7 python2.7-dev python-pip build-essential cython \
    mysql-server libmysqlclient-dev mongodb nodejs npm git


2. Clone your repo and setup project directory
git clone https://github.com/youruser/photomosaic.git
cd photomosaic



3. Set up and activate virtualenv
pip install virtualenv
virtualenv venv
source venv/bin/activate



4. Install Python requirements
pip install -r requirements.txt
# Also install mysqlclient for Django MySQL integration
pip install mysqlclient



5. Build Cython extensions
cd PhotoMosaic_source
python setup.py build_ext --inplace
cd ..



6. Run Django migrations
python manage.py migrate
python manage.py collectstatic  # if using staticfiles in production



7. Create superuser
python manage.py createsuperuser



8. Setup media and static directories
mkdir -p media/results/completed
mkdir -p static

# If using S3, skip this and configure settings.py as above



9. Configure Gunicorn for production
pip install gunicorn
gunicorn photomosaic.wsgi:application --bind 0.0.0.0:8000



10. (Optional) Setup nginx as a reverse proxy

Add an nginx config for your domain, proxying to 127.0.0.1:8000

Serve /media/ and /static/ directly from the filesystem

11. (Optional) Enable as a systemd service for Gunicorn/nginx

12. (Optional) Install and configure Celery for async tasks

Production Checklist
 All secrets and credentials are secured (not in version control).

 All paths in settings.py are correct.

 MySQL and MongoDB are running and populated.

 EC2 security group allows HTTP/HTTPS (and SSH for admin).

 HTTPS enabled (Let’s Encrypt/Certbot recommended).

 If using S3, all media is syncing as expected.

 Python 3 upgrade recommended (see below).

Modernization & Maintenance
Upgrade for Python 3

Change all code to be Python 3 compatible (print, imports, exception syntax, xrange → range, etc).

Use pip install pillow and updated package versions.

For Cython modules, ensure setup.py is Python 3 compatible.

Test thoroughly!

JS/CSS Modernization

Use npm install to add modern build tools (Webpack, Parcel).

Bundle and minify all JS into one custom.js, and CSS into custom.css.

Remove any unused JS/CSS from static/js/.

Other Recommendations

Set DEBUG = False and configure ALLOWED_HOSTS in production.

Use AWS S3 for scalable storage if needed.

Add monitoring (CloudWatch, Sentry, etc).

Troubleshooting
Static/media not served: Check nginx config and Django settings.py.

Database errors: Ensure MySQL and MongoDB are running, users/passwords correct.

Build issues: Make sure all C/Cython dependencies are present.

Permissions: Ensure media/ and static/ are writable by the Django user.

License
See LICENSE file for full open-source licensing.

Credits
Core photomosaic code adapted from open-source academic projects (see in-code attributions)

Frontend: blueimp, jQuery, Bootstrap

******

full breakdown of every folder and file in your project, what each one is for, what it relates to, and why the structure is important. This level of detail is intended both for onboarding developers and for long-term maintainability, modernization, and debugging.

📦 Top-Level Structure
1. photomosaic/ (Project Root)
Purpose: The root directory for the entire Django project and supporting code. Contains app modules, compiled code, static/media folders, and all setup scripts/configs.

Relates To: All other files and folders are structured under this root for clarity and Python import resolution.

⚙️ Core Django Project
2. photomosaic/
Purpose: Main Django project folder (not to be confused with the root). Holds core config: settings, URLs, and the WSGI entrypoint.

Contains:

__init__.py: Marks the folder as a Python package.

settings.py: All Django project settings—databases, static/media config, installed apps, etc.

Relates To: Controls configuration for all Django apps, static/media, DBs.

urls.py: Routes URLs to views across apps (mostly mosaic/).

Relates To: Directs traffic to admin panel and mosaic app endpoints.

wsgi.py: The entrypoint for production web servers (Gunicorn, uWSGI, etc.).

Relates To: Required by most deployment systems.

(optional) asgi.py if you add async support (not shown here).

3. manage.py
Purpose: Command-line utility for all Django project management (runserver, migrate, collectstatic, etc.).

Relates To: Wraps all Django settings and management tasks, always run from project root.

🧩 Main Django App
4. mosaic/
Purpose: The main Django app for handling photomosaic logic, views, templates, static assets, etc.

Contains:

static/: All JavaScript, CSS, and static image assets.

Relates To: Used for file upload UI, gallery, and custom interactivity.

templates/: App-level HTML templates.

Relates To: Rendered by Django views. Uses {% extends %} for inheritance.

templatetags/: Custom Django template tags, e.g., for injecting upload widgets.

Relates To: Loaded into templates for extra template functionality.

media/: (Created at runtime) Where user-uploaded and output files are stored. Not part of version control.

Relates To: Django MEDIA_ROOT/MEDIA_URL; served to users or via S3.

results/ & results/completed/: Output directory for generated mosaics.

Relates To: Shown to user after mosaic generation.

Usual Django files (views.py, forms.py, models.py, admin.py, etc.).

Relates To: Handle routing, forms, admin, etc.

4.1. static/js/, static/css/, etc.
Purpose: All frontend JavaScript/CSS for uploads, gallery, file handling.

Relates To: Referenced in templates for a working user interface.

4.2. templates/
Purpose: Holds all HTML templates for different pages and error handlers.

base.html: Base template for all pages; includes common header, loads static files, provides {% block %} sections.

404.html, 500.html: Custom error pages for not found/server error.

main_menu.html, home.html, results.html, picture_form.html, remove_images.html, error_rm.html: All user-facing interface pages for upload, gallery, removal, results, etc.

Relates To: Each template is loaded by a view function in Django and typically extends base.html.

4.3. templatetags/upload_tags.py
Purpose: Custom Django tag to inject dynamic file upload JS templates.

Relates To: Used in HTML with {% load upload_tags %} and {% upload_js %} to render uploader widget templates.

🏗️ Photomosaic Engine (Core Processing)
5. PhotoMosaic_source/
Purpose: The heart of the image processing engine, implemented in Python and Cython (some C for speed).

Why Separate? This keeps the computationally intensive logic modular and distinct from the web layer, allowing easy future upgrades or replacement (e.g., swap Cython for Rust or pure Python if needed).

Contains:

directory_walker.py: Walks directories recursively to find all image files for the pool.

jigsaw.py: Contains logic for generating puzzle-shaped mosaic tiles (jigsaw shapes).

memo.py: Implements function memoization for performance (caching results of expensive function calls).

photomosaic.py: Core orchestration: partitions source images, analyzes colors, matches with pool, assembles the final mosaic.

progress_bar.py: Utility for logging progress during long operations.

color_metrics/: Submodule for fast color math (deltaE2000, rgb2lab, etc.).

setup.py: Compiles Cython modules (important for performance).

requirements.txt, README, etc.: Setup and dependency info.

5.1. color_metrics/
Purpose: High-performance C/Cython routines for color distance calculations.

color_metrics.pyx: Cython implementation glue.

deltaE2000.c/.h: Implements CIEDE2000 color difference in C.

rgb2lab.c/.h: Fast RGB to Lab color conversion.

__init__.py: Makes the directory a Python module.

Relates To: Used by photomosaic.py for matching tile images by perceived color, which is a core quality metric of the mosaic.

5.2. setup.py
Purpose: Build script for compiling all Cython extensions. This is required for the engine’s performance. Run python setup.py build_ext --inplace.

Relates To: Outputs compiled modules in the current directory, often to photomosaic_exec/.

5.3. README, requirements.txt
Purpose: Explain compilation steps, Python requirements, and advanced usage of the photomosaic engine.

Relates To: Reference for anyone maintaining or deploying the engine.

📁 Build/Compiled Modules
6. photomosaic_exec/
Purpose: Where all the Cython/C-compiled modules are placed after running setup.py.

Relates To: Importable by the Django app for use in image processing; keeps compiled code organized and out of the source folder.

🗂️ Misc/Runtime
7. media/
Purpose: Runtime directory for all user-uploaded images and output mosaics.

Relates To: Used in Django settings as MEDIA_ROOT, served by Django (in dev) or Nginx/S3 (in production). Results are written here by processing jobs.

8. static/
Purpose: Where all collected static files (JS, CSS, images) go for serving to clients.

Relates To: Managed by collectstatic in Django; can be served by Nginx, S3, or Django’s dev server.

🔒 Settings/Config
9. .env (recommended, not always present)
Purpose: Store secret config, DB passwords, and environment variables.

Relates To: Loaded by Django on startup (with django-environ or similar), keeps secrets out of source code.

🧑‍💻 Developer/Build Files
10. requirements.txt
Purpose: Lists all Python dependencies for easy install with pip install -r requirements.txt.

Relates To: All code that depends on these modules (Django, Pillow, pymongo, etc.).

11. README.md
Purpose: Documentation for new users/devs. Contains usage, setup, deployment, and troubleshooting info.

Relates To: Every aspect of setup, deployment, and app usage.

How Everything Relates
Django Layer (photomosaic/, mosaic/): Handles web requests, forms, file uploads, and triggers photomosaic generation.

PhotoMosaic Engine (PhotoMosaic_source/): Receives the file paths from Django, does the heavy lifting of generating the mosaic, and writes outputs to media/results/completed/.

Databases (MySQL/MongoDB): MySQL stores Django app data (users, sessions, admin); MongoDB indexes uploaded images for fast color matching.

Static/Media Folders: Serve user-uploaded content and static assets to clients. Optional S3 integration for scale.

Custom Template Tags: Make complex UI widgets possible and reusable in templates (e.g., file uploaders).

Why This Structure?
Separation of Concerns: Web logic, image processing, and frontend assets are separated, making each layer easy to test, maintain, and swap/modernize independently.

Performance: Heavy computation in Cython/C; web layer stays responsive.

Scalability: Use S3 for media; MongoDB and MySQL for large image sets; stateless web app can scale horizontally.

Maintainability: Clear, documented folder and file layout, with everything in predictable places for quick onboarding.
































README section (ready to copy-paste at the top of your repo) that covers:

What the project is and how it works

How the major folders and files relate

Step-by-step deployment instructions (for dev/prod)

Modernization tips (Python 3, JS, build process)

Notes on further maintenance and best practices

PhotoMosaic Web App – README
Overview
This project is a full-stack Django application that generates photomosaics from user-uploaded images.

The backend is built with Django, with a modular photomosaic engine (Python + Cython/C code).

Image pool and mosaic generation use MongoDB for fast access and parallel processing.

The frontend uses modern (but classic) JavaScript libraries for multi-file image uploads, progress bars, drag-and-drop support, and a clean, Bootstrap-based interface.

Project Structure & How It All Fits Together
1. Django App: mosaic/
Handles all web requests: routing, forms, session management, serving static files, and templates.

views.py: Orchestrates user flows (uploading, removing images, creating mosaics, displaying results).

templates/: HTML files for all UI pages.

static/js/: JS/CSS for the frontend (file upload, gallery, etc).

media/: Where user-uploaded and mosaic-generated images are stored.

2. Photomosaic Engine: PhotoMosaic_source/
High-performance Python + Cython code for:

Traversing image directories

Color analysis (color_metrics/)

Image splitting/tiling

Parallelized image matching using MongoDB

Image assembly and processing

3. Project Settings: photomosaic/
settings.py: All Django config—paths, database (MySQL), static/media locations, Celery, Cloudinary (optional), etc.

urls.py: Connects project URLs to app (mosaic/) URLs.

wsgi.py: Entry point for production servers (e.g., Gunicorn, uWSGI).

4. Compiled Extensions: photomosaic_exec/
After building, Cython/C modules for speed.

How It Works: Full Flow
User accesses the site (main_menu.html):

Upload images for the mosaic pool.

Remove or add images at any time.

Start a new mosaic generation.

Upload Process (picture_form.html):

Users select/upload multiple images via a drag-and-drop interface.

Frontend JS (from static/js/) handles chunked uploads, previews, progress bars.

Backend Image Pool:

Uploaded images are saved to media/ and indexed in MongoDB (as per settings.py).

The PhotoMosaic_source/ code analyses and stores color metrics for fast matching.

Mosaic Generation:

User chooses a base image and mosaic shape.

Mosaic engine divides the base image into tiles, analyzes colors, and selects the best-matching pool image for each tile.

Mosaic is assembled, saved to media/results/completed/, and displayed in results.html.

Admin/Management:

Django Admin is enabled for advanced management of users and images.

Static and media files are served via Django (dev) or your web server (prod).

Deployment Instructions
Prerequisites
Python 2.7 (project is legacy; modernization for Python 3 recommended)

pip, virtualenv

MySQL (or compatible) for Django database

MongoDB for image/color data (used by mosaic engine)

C build tools (gcc, python-dev, cython) for Cython extensions

Node.js/npm (if you wish to modernize/minimize frontend assets)

1. Clone and Set Up Virtual Environment
sh
Copy
Edit
git clone <repo-url>
cd <repo-dir>
virtualenv venv
source venv/bin/activate
2. Install Python Requirements
sh
Copy
Edit
pip install -r PhotoMosaic_source/requirments.txt
# or if requirements.txt is at root, adjust path as needed
Install MySQL and MongoDB server if not already running.

(Optional) Install any missing system dependencies (ImageMagick, Python headers).

3. Configure Your Paths
Edit photomosaic/settings.py:

PROJ_DIR: Set to your actual project path (absolute is safest).

DATABASES: Set MySQL credentials.

MEDIA_ROOT, STATIC_ROOT: Make sure these directories exist.

ALLOWED_HOSTS: Add your server IP/domain.

Remove/disable CLOUDINARY if not in use.

4. Build Cython Modules
From within PhotoMosaic_source/:

sh
Copy
Edit
cd PhotoMosaic_source
python setup.py build_ext --inplace
# Or use the provided ./run script if available and executable
./run
This generates the compiled photomosaic_exec/ directory.

5. Run Database Migrations
sh
Copy
Edit
cd <repo-dir>
python manage.py migrate
6. Create a Superuser (for admin access)
sh
Copy
Edit
python manage.py createsuperuser
7. Run Development Server
sh
Copy
Edit
python manage.py runserver
Visit http://127.0.0.1:8000/ to test.

8. For Production:
Use Gunicorn/uWSGI and a reverse proxy (nginx/Apache) pointing to photomosaic.wsgi.

Serve media/ and static/ via web server.

Secure your secrets, set DEBUG=False, configure ALLOWED_HOSTS.

(Optional) Use Celery and a message broker for heavy/async tasks.

Modernization & Maintenance Tips
Python 3: The code is written for Python 2.x; upgrade to Python 3 for long-term security and package compatibility (update all print statements, integer division, exception syntax, xrange to range, and all imports).

Cython/Dependencies: Ensure your build environment matches the versions in requirments.txt. Update for new versions as needed.

JavaScript: Consider combining/minifying JS using webpack or similar for production. Remove unused files and consolidate logic into custom.js for maintainability.

Security: Don’t store secrets in version control. Change all sample passwords/secrets in settings.py.

Static/media paths: Ensure all paths in settings.py match your actual deployment.

Cloudinary/3rd Party: Remove configs/services you aren’t using.

Backups: Regularly backup your MongoDB and media directories.

Troubleshooting
Static files not loading?

Check STATIC_ROOT, STATIC_URL, and your web server config.

Media upload/permission errors?

Make sure the user running Django has write permission to media/.

Cython modules not found?

Rebuild with python setup.py build_ext --inplace and check PYTHONPATH.

Contributors & Credits
Photomosaic core adapted from open source projects (see in-code attributions)

JS libraries: jQuery, blueimp file upload, Bootstrap, etc.

License
See LICENSE file for open-source license details.

>>>>>>> 5607720 (Clean push of photomosaic project with no secrets or venv)
