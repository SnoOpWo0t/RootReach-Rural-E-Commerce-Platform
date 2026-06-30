#!/bin/bash

# Build script for Vercel deployment

echo "Building project..."
python3 -m pip install -r requirements.txt

echo "Make migrations..."
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput

echo "Collect static..."
python3 manage.py collectstatic --noinput --clear
