from django.http import HttpResponse
from django.contrib.auth import get_user_model

def temp_create_admin(request):
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@og.com', 'OGAdmin2026!')
        return HttpResponse('✅ Admin created! Username: admin | Password: OGAdmin2026!')
    return HttpResponse('✅ Admin already exists.')
