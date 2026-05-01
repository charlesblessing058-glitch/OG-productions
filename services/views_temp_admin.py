from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def create_admin_once(request):
    User = get_user_model()
    # Only create if doesn't exist
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@og.com', 'OGAdmin2026!')
        return HttpResponse('✅ Admin created! Username: admin | Password: OGAdmin2026!')
    return HttpResponse('✅ Admin already exists. Login at /login/')
