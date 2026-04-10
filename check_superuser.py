import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rootreach.settings')
django.setup()

from core.models import CustomUser

# Check if akhi exists
try:
    user = CustomUser.objects.get(username='akhi')
    print(f"✓ Found user: {user.username}")
    print(f"  Is superuser: {user.is_superuser}")
    print(f"  Is staff: {user.is_staff}")
    print(f"  Is active: {user.is_active}")
    print(f"  Email: {user.email}")
except CustomUser.DoesNotExist:
    print("✗ User 'akhi' does not exist - creating now...")
    
    # Delete all superusers first
    CustomUser.objects.filter(is_superuser=True).delete()
    
    # Create new superuser with proper settings
    user = CustomUser.objects.create_superuser(
        username='akhi',
        email='afrfinsultanaakhi138@gmail.com',
        password='1',
        phone='',
        location='',
        address='',
        gender='other'
    )
    user.is_active = True
    user.is_staff = True
    user.save()
    
    print(f"\n✓ New superuser created!")
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Is active: {user.is_active}")
    print(f"  Is staff: {user.is_staff}")
    print(f"  Is superuser: {user.is_superuser}")
