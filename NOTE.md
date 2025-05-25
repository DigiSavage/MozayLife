# Project Setup & Development Guide

## Quick Start (EC2/Linux)

1. **Create and activate a Python virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Compile PhotoMosaic modules:**
    ```bash
    cd PhotoMosaic_source
    ./run
    # (Adjust this step if you migrate from legacy build scripts)
    ```

4. **Go to project root (where `manage.py` is):**
    ```bash
    cd ..
    ```

5. **Run Celery worker:**
    ```bash
    celery -A mosaic.tasks worker -l info
    ```

6. **Run Django server (in a new terminal):**
    ```bash
    python manage.py runserver 0.0.0.0:8000
    # (or use Gunicorn/Uvicorn for production)
    ```

---

**For production deployment:**  
- Use Gunicorn or Uvicorn, and a process manager like `systemd` or `pm2`.
- Use Nginx as a reverse proxy.
- Set environment variables for secrets/configs—do NOT hardcode in settings.

**See `requirements.txt` for dependencies.**
