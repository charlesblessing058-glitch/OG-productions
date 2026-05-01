from django.db import migrations
from django.contrib.auth import get_user_model

def create_admin(apps, schema_editor):
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@ogproductions.com',
            password='OGAdmin2026!'
        )
        print("🎉 ADMIN CREATED: admin / OGAdmin2026!")

class Migration(migrations.Migration):
    dependencies = [
        ('services', '0008_portfolioitem'),  # Adjust if your last migration has a different name
    ]
    operations = [
        migrations.RunPython(create_admin),
    ]