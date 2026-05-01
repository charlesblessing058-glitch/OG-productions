from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model

@receiver(post_migrate)
def create_production_admin(sender, **kwargs):
    """Auto-create admin user on first deploy"""
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@ogproductions.com',
            password='OGAdmin2026!'
        )
        print("🎉 PRODUCTION ADMIN CREATED!")
        print("Username: admin")
        print("Password: OGAdmin2026!")
        print("⚠️ Change password after first login!")
