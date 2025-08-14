from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create a default user for testing'

    def handle(self, *args, **options):
        # Check if user already exists
        if User.objects.filter(username='admin').exists():
            self.stdout.write(
                self.style.WARNING('User "admin" already exists')
            )
            return

        # Create superuser
        user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_superuser=True
        )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created user "{user.username}" with password "admin123"')
        )
        self.stdout.write(
            self.style.SUCCESS('You can now log in with username: admin and password: admin123')
        )
