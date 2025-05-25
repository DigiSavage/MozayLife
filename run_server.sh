#!/bin/bash
# Runs the Django development server

# Activate the virtual environment (edit path if your venv is elsewhere)
if [ -d "venv/bin" ]; then
    source venv/bin/activate
elif [ -d "venv2/bin" ]; then
    source venv2/bin/activate
else
    echo "❌ Virtual environment not found! Edit this script to point to your venv directory."
    exit 1
fi

# Optional: Export DJANGO_SETTINGS_MODULE if not set (edit as needed)
# export DJANGO_SETTINGS_MODULE=photomosaic.settings

echo "✅ Starting Django development server at http://0.0.0.0:8000/"
python ./manage.py runserver 0.0.0.0:8000