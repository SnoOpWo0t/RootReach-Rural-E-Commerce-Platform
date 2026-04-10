import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rootreach.settings')
django.setup()

from core.models import CustomUser

# Update the akhi superuser to have user_type='admin'
try:
    user = CustomUser.objects.get(username='akhi')
    user.user_type = 'admin'
    user.save()
    print(f"✓ Updated superuser 'akhi'")
    print(f"  Username: {user.username}")
    print(f"  User Type: {user.user_type} → {user.get_user_type_display()}")
    print(f"  Is Superuser: {user.is_superuser}")
except CustomUser.DoesNotExist:
    print("✗ User 'akhi' not found")
