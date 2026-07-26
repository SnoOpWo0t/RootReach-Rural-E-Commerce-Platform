<div align="center">
  <img src="https://via.placeholder.com/200x200.png?text=RootReach+Logo" alt="RootReach Logo" width="150" height="150"/>

  # RootReach
  
  **A Modern Rural E-Commerce Platform Empowering Local Businesses**
  
  [![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
  [![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com/)
  
  [Features](#✨-features) • [Quick Start](#🚀-quick-start) • [Deployment](#🌐-deployment) • [AI Assistant](#🤖-ai-assistant) • [Structure](#🎯-project-structure)
</div>

---

## 📖 About RootReach

**RootReach** is a comprehensive, rural-focused e-commerce platform built on the robust Django framework. Our mission is to connect rural artisans, farmers, and local sellers with a wider market, providing them with an intuitive and powerful platform to manage and grow their businesses.

## 📸 Gallery

> **Note:** Add your project screenshots and GIFs to a `docs/images/` directory in your repository and update the paths below.

### Platform Demo
<div align="center">
  <img src="https://via.placeholder.com/800x450.gif?text=Platform+Demo+GIF" alt="RootReach Demo GIF" width="800"/>
</div>

### Screenshots
<p align="center">
  <img src="https://via.placeholder.com/400x250.png?text=Home+Page" alt="Home Page" width="400"/>
  <img src="https://via.placeholder.com/400x250.png?text=Seller+Dashboard" alt="Dashboard" width="400"/>
</p>

---

## ✨ Features

- **Multi-Role User Ecosystem:** Seamless experiences tailored for Buyers, Sellers, and Administrators.
- **Smart Product Management:** Robust tools for rural sellers to manage inventory and orders.
- **AI-Powered Discovery:** A built-in AI shopping assistant that recommends products based on natural language requests.
- **Modern UI/UX:** Clean, responsive design powered by Bootstrap 4 and Django Crispy Forms.
- **Ready for the Cloud:** Serverless deployment configuration pre-setup for Vercel.

---

## 🚀 Quick Start

Follow these steps to get a local development environment up and running.

### 1. Prerequisites
Ensure you have the following installed:
- **Python 3.8+**
- **Git** (optional, but recommended)

### 2. Installation Steps

**Clone the repository:**
```bash
git clone <repository-url>
cd RootReach-Rural-E-Commerce-Platform
```

**Set up your virtual environment:**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Prepare the database:**
```bash
python manage.py migrate
```

*(Optional) Create a superuser for the admin dashboard:*
```bash
python manage.py createsuperuser
```

**Launch the development server:**
```bash
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000/` in your browser to view the application!

---

## 🔑 Test Accounts
For local testing, the following accounts are pre-configured:

| Role | Username | Password |
|------|----------|----------|
| **Admin** | `akhi` | `1` |
| **Seller** | `Seller` | `Test@1234` |
| **Buyer** | `Buyer` | `Test@1234` |

---

## 🤖 AI Shopping Assistant

RootReach features a cutting-edge AI shopping assistant available at `/ai-assistant/`.

**Capabilities:**
- Understands natural language shopping requests (e.g., budget, product type, location).
- Smartly recommends matching products from the platform's catalog.
- **Dual Modes:** Runs entirely on catalog intelligence (no API key required), or optionally via LLM assistance for advanced reasoning.

**Optional LLM Setup:**
To enable OpenAI integration, set the following environment variables before starting your server:

```powershell
$env:OPENAI_API_KEY="your_openai_api_key"
$env:OPENAI_MODEL="gpt-4o-mini"
```

---

## 🎯 Project Structure

```text
RootReach/
├── manage.py              # Django management script
├── requirements.txt       # Project dependencies
├── db.sqlite3             # Local SQLite database
├── rootreach/             # Main project settings & configurations
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                  # Core application (business logic)
│   ├── models.py          # Database models
│   ├── views.py           # View controllers
│   ├── templates/         # HTML templates
│   └── static/            # CSS, JS, and image assets
├── api/                   # Serverless entrypoints (Vercel)
└── media/                 # User-uploaded files (images, documents)
```

---

## 📦 Tech Stack & Packages

- **Django 5.2:** The core web framework.
- **django-crispy-forms & crispy-bootstrap4:** For beautiful, responsive form rendering.
- **Pillow 11.3:** For robust image processing (profile pictures, product images).
- **SQLite:** Default local database (PostgreSQL recommended for production).

---

## 🌐 Deployment

### Vercel Integration
This project is configured for serverless deployment on Vercel out of the box using `api/index.py` and `vercel.json`.

> [!WARNING]
> **Vercel Size Limits:** Vercel enforces a 250MB limit on serverless functions. To avoid deployment failures, large files like `venv/` or the SQLite database are automatically excluded via `.vercelignore`.

**Required Vercel Environment Variables:**
- `SECRET_KEY`
- `DEBUG=false`
- `ALLOWED_HOSTS=your-project.vercel.app`

> [!NOTE]
> Vercel is ideal for demonstration purposes. For full production, migrate your database to a managed service (e.g., Neon, AWS RDS) and use external storage (e.g., AWS S3, Cloudinary) for media files, as local storage on Vercel is ephemeral.

### Traditional Production Stack
For a standard VPS or dedicated server deployment, the recommended stack is:
- **Database:** PostgreSQL
- **Web Server:** Nginx + Gunicorn
- **Secrets Management:** Environment variables (`.env`)

---

## 🔧 Troubleshooting

- **"python is not recognized"**: Ensure Python is added to your system's `PATH`. On Windows, try using the `py` command.
- **Virtual environment activation fails**: If you are using PowerShell on Windows, you may need to update your execution policy:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- **Pip install fails**: Try upgrading pip first:
  ```bash
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
  ```

---

<div align="center">
  <i>Developed with ❤️ for rural empowerment. Happy Coding! 🎉</i>
</div>