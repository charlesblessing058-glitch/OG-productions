from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create temporary admin user'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.SUCCESS('Admin already exists!'))
        else:
            User.objects.create_superuser('admin', 'admin@og.com', 'Admin123!')
            self.stdout.write(self.style.SUCCESS('✅ Admin created! Username: admin | Password: Admin123!'))
