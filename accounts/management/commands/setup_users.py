from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Créer ou mettre à jour les utilisateurs par défaut pour les tests'

    def handle(self, *args, **options):
        # Admin user
        admin = User.objects.filter(username='admin').first()
        if admin:
            admin.set_password('adminpass123')
            admin.save()
            self.stdout.write(
                self.style.SUCCESS('✓ Admin user updated')
            )
        else:
            User.objects.create_superuser('admin', 'admin@auto.com', 'adminpass123')
            self.stdout.write(
                self.style.SUCCESS('✓ Admin user created')
            )

        # Test user
        test_user = User.objects.filter(username='testuser').first()
        if test_user:
            test_user.set_password('TestPassword123!')
            test_user.save()
            self.stdout.write(
                self.style.SUCCESS('✓ Test user updated')
            )
        else:
            User.objects.create_user(
                username='testuser',
                email='testuser@example.com',
                password='TestPassword123!',
                first_name='Test',
                last_name='User'
            )
            self.stdout.write(
                self.style.SUCCESS('✓ Test user created')
            )

        self.stdout.write(self.style.SUCCESS('\nCredentials:'))
        self.stdout.write('Admin: admin / adminpass123')
        self.stdout.write('Test: testuser / TestPassword123!')
