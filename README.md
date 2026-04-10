# RoorReach Django E-commerce Project Setup Guide

## 📋 Prerequisites
Before you start, make sure you have:
- Python 3.8 or higher installed on your computer
- Git (optional, for version control)

## 🚀 Quick Start Guide for Beginners

### Step 1: Download/Clone the Project
If you have Git:
```bash
git clone <repository-url>
cd RoorReach_1
```

If you downloaded as ZIP:
- Extract the ZIP file
- Open terminal/command prompt in the project folder

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv .venv

# macOS/Linux
python3 -m venv .venv
```

### Step 3: Activate Virtual Environment
```bash
# Windows (Command Prompt)
.venv\Scripts\activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Set Up Database
```bash
python manage.py migrate
```

### Step 6: Create Admin User (Optional)
```bash
python manage.py createsuperuser
```

### Step 7: Run the Development Server
```bash
python manage.py runserver
```

### Step 8: Open Your Browser
Visit: http://127.0.0.1:8000/

## 🛠️ Alternative Installation (One-Line Command)
If you want to install specific versions manually:
```bash
pip install Django==5.2.6 django-crispy-forms==2.4 crispy-bootstrap4==2025.6 Pillow==11.3.0
```

## 📦 What Each Package Does
- **Django**: The main web framework
- **django-crispy-forms**: Makes forms look better with Bootstrap styling
- **crispy-bootstrap4**: Bootstrap 4 templates for crispy forms
- **Pillow**: Handles image processing (profile pictures, product images)

## 🔧 Troubleshooting

### If you get "python is not recognized":
- Make sure Python is installed and added to PATH
- Try using `py` instead of `python` on Windows

### If virtual environment activation fails:
- On Windows PowerShell, you might need to run:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### If pip install fails:
- Update pip first: `python -m pip install --upgrade pip`
- Try: `python -m pip install -r requirements.txt`

## 🌐 Production Deployment
For production, you'll also need:
- A production database (PostgreSQL recommended)
- A web server (Nginx + Gunicorn)
- Environment variables for secrets

## 📞 Support
If you encounter any issues, check:
1. Python version: `python --version`
2. Virtual environment is activated (you should see `.venv` in terminal prompt)
3. All packages installed: `pip list`

## 🎯 Project Structure
```
RoorReach_1/
├── manage.py              # Django management script
├── requirements.txt       # This file - lists all dependencies
├── db.sqlite3            # Database file
├── rootreach/            # Main project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                 # Main application
│   ├── models.py         # Database models
│   ├── views.py          # Business logic
│   ├── templates/        # HTML templates
│   └── static/           # CSS, JS, images
└── media/                # User uploaded files
```

Happy coding! 🎉

## AI Shopping Assistant (New)

RootReach now includes an AI assistant page at `/ai-assistant/`.

### What it does
- Accepts natural language shopping requests (example: product type, budget, location).
- Recommends matching products from your catalog.
- Works in two modes:
  - Catalog intelligence mode (built-in ranking, no API key needed)
  - LLM-assisted mode (if OpenAI API key is configured)

### Optional OpenAI setup
Set these environment variables before running the server:

```powershell
$env:OPENAI_API_KEY="your_openai_api_key"
$env:OPENAI_MODEL="gpt-4o-mini"
```

If `OPENAI_API_KEY` is not set, the assistant will still work using local ranking logic.