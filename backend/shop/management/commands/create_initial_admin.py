from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates an initial admin user if none exists'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@betapack.co.rs',
                password='admin123'  # PROMENI OVO POSLE!
            )
            self.stdout.write(self.style.SUCCESS('Admin user created successfully!'))
            self.stdout.write(self.style.WARNING('Username: admin, Password: admin123'))
            self.stdout.write(self.style.WARNING('PLEASE CHANGE PASSWORD AFTER FIRST LOGIN!'))
        else:
            self.stdout.write(self.style.SUCCESS('Admin user already exists'))
