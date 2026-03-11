from django.contrib.auth.models import User
from django.db import IntegrityError

# Créer ou mettre à jour le compte admin
try:
    admin = User.objects.filter(username='admin').first()
    if admin:
        # Mettre à jour le mot de passe
        admin.set_password('adminpass123')
        admin.save()
        print(f"✓ Admin user updated - Password: adminpass123")
    else:
        # Créer le compte admin
        admin = User.objects.create_superuser('admin', 'admin@auto.com', 'adminpass123')
        print(f"✓ Admin user created - Username: admin, Password: adminpass123")
except Exception as e:
    print(f"✗ Error: {e}")

# Créer un utilisateur test
try:
    test_user = User.objects.filter(username='testuser').first()
    if test_user:
        # Mettre à jour le mot de passe
        test_user.set_password('TestPassword123!')
        test_user.save()
        print(f"✓ Test user updated - Username: testuser, Password: TestPassword123!")
    else:
        # Créer l'utilisateur test
        test_user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123!',
            first_name='Test',
            last_name='User'
        )
        print(f"✓ Test user created - Username: testuser, Password: TestPassword123!")
except Exception as e:
    print(f"✗ Error: {e}")

print("\nDone! Users are ready for testing.")
