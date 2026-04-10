import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rootreach.settings')
django.setup()

from core.models import CustomUser

# Delete all superusers
superusers = CustomUser.objects.filter(is_superuser=True)
if superusers.exists():
    count = superusers.count()
    superusers.delete()
    print(f"✓ Deleted {count} superuser(s)")
else:
    print("✓ No superusers found to delete")

# Create new superuser
new_super = CustomUser.objects.create_superuser(
    username='akhi',
    email='afrfinsultanaakhi138@gmail.com',
    password='1',
    phone='',
    location='',
    address='',
    gender='other'
)
print(f"\n✓ New superuser created successfully!")
print(f"  Username: {new_super.username}")
print(f"  Email: {new_super.email}")
print(f"  Is Superuser: {new_super.is_superuser}")
