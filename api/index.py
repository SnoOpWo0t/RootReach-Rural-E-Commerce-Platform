import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rootreach.settings')

from rootreach.wsgi import application

app = application