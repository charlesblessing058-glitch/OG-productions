from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create admin user for production'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'admin'
        email = 'admin@ogproductions.com'
        password = 'OGAdmin2026!'
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(f'✅ Admin "{username}" already exists!'))
        else:
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS(f'🎉 Admin created!'))
            self.stdout.write(self.style.WARNING(f'Username: {username}'))
            self.stdout.write(self.style.WARNING(f'Password: {password}'))
            self.stdout.write(self.style.WARNING('⚠️ Change password after first login!'))
