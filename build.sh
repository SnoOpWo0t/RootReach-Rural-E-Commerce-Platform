#!/bin/bash
set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Build successful! Skipping migrations and collectstatic since they are handled locally."

