import requests
import base64
import json
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Service, ServiceRequest, SiteSetting, NavigationItem, Notification, PortfolioItem, PortfolioItem, ContactMessage
from .forms import CustomUserCreationForm, CustomAuthenticationForm

# ==========================================
# 🌐 HELPERS
# ==========================================
def get_site_context():
    setting, _ = SiteSetting.objects.get_or_create(id=1)
    nav_items = NavigationItem.objects.filter(is_active=True).order_by('order')
    return {'site_settings': setting, 'nav_items': nav_items}

# ==========================================
# 🔐 AUTHENTICATION
# ==========================================
def user_login(request):
    if request.user.is_authenticated: return redirect('home')
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                login(request, user)
                messages.success(request, f'✅ Welcome, {user.first_name or user.username}!')
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form, **get_site_context()})

def register(request):
    if request.user.is_authenticated: return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        if not username or not email or not password1:
            messages.error(request, '❌ Please fill in all required fields.')
        elif password1 != password2:
            messages.error(request, '❌ Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, '❌ Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, '❌ Email already registered.')
        else:
            try:
                user = User.objects.create_user(username=username, email=email, password=password1, first_name=first_name, last_name=last_name)
                login(request, user)
                messages.success(request, f'✅ Account created successfully!')
                return redirect('home')
            except Exception as e:
                messages.error(request, f'❌ Error: {str(e)}')
    return render(request, 'register.html', {'site_settings': get_site_context()['site_settings']})

def user_logout(request):
    logout(request)
    return redirect('login')

# ==========================================
# 🏠 HOME DASHBOARD
# ==========================================
@login_required(login_url='login')
def home(request):
    ctx = get_site_context()
    ctx['services'] = Service.objects.filter(is_active=True)
    ctx['my_requests'] = ServiceRequest.objects.filter(user=request.user).order_by('-created_at')
    ctx['portfolio'] = PortfolioItem.objects.filter(is_active=True).order_by('order', '-created_at')[:6]
    return render(request, 'home.html', ctx)

# ==========================================
# 📝 REQUEST SUBMISSION
# ==========================================
@login_required
def submit_request(request):
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        client_name = request.POST.get('client_name')
        client_email = request.POST.get('client_email')
        client_phone = request.POST.get('client_phone')
        notes = request.POST.get('notes', '')
        
        is_ajax = request.headers.get('Accept') == 'application/json'
        
        try:
            service = Service.objects.get(id=service_id, is_active=True)
            new_req = ServiceRequest.objects.create(
                user=request.user, service=service,
                client_name=client_name or f"{request.user.first_name} {request.user.last_name}".strip(),
                client_email=client_email or request.user.email,
                client_phone=client_phone, notes=notes,
                status='pending', payment_status='pending'
            )
            
            # ✅ Create Instant Notification
            Notification.objects.create(
                user=request.user,
                title='📩 Request Received',
                message=f'We have received your request for "{service.name}". We will contact you shortly.',
                notification_type='request'
            )
            
            if is_ajax:
                return JsonResponse({'success': True, 'request_id': str(new_req.id)})
            messages.success(request, f'✅ Request for "{service.name}" submitted!')
            return redirect('home')
        except Exception as e:
            if is_ajax:
                return JsonResponse({'success': False, 'message': str(e)}, status=400)
            messages.error(request, f'❌ Error: {str(e)}')
            return redirect('home')
    return redirect('home')

# ==========================================
# 💰 M-PESA INTEGRATION
# ==========================================
MPESA_CONSUMER_KEY = 'IIysoq3NO4gHfjJBYfLTtAylX6aFh9fOObXErsh2ycXbhe2J'
MPESA_CONSUMER_SECRET = 'yv1ZuA3GK18MzcMkwWZzjVOR56g9wtMliNosx4wCgjB2QxZuL0Ys05MlGkaaRU1X'
MPESA_SHORTCODE = '174379'
MPESA_PASSKEY = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
MPESA_TEST_MODE = True

def get_mpesa_access_token():
    url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(url, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET))
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print(f"🔍 SAFARICOM AUTH ERROR: {response.status_code} - {response.text}")
        return None

@login_required
def initiate_mpesa_payment(request, request_id):
    """M-Pesa payment with guaranteed simulation fallback"""
    try:
        service_request = ServiceRequest.objects.get(id=request_id, user=request.user)
        
        # 🧪 GUARANTEED SIMULATION MODE (Bypasses Safaricom completely)
        # Set to False later when you have live credentials
        SIMULATION_MODE = True
        
        if SIMULATION_MODE:
            print("🧪 M-PESA SIMULATION: SUCCESS")
            service_request.mpesa_checkout_id = "SIM_" + str(request_id)
            service_request.mpesa_phone = request.POST.get('phone', '254708374149')
            service_request.payment_status = 'paid'
            service_request.mpesa_receipt_number = 'SIM_' + datetime.now().strftime('%Y%m%d%H%M%S')
            service_request.status = 'processing'
            service_request.save()
            
            Notification.objects.create(
                user=request.user,
                title="💰 Payment Received",
                message=f"Test payment of KES {service_request.service.price} for '{service_request.service.name}' confirmed.",
                notification_type='payment'
            )
            return JsonResponse({'success': True, 'message': 'Payment successful (Test Mode)'})
        
        # 🔐 REAL SAFARICOM API (Only runs if SIMULATION_MODE = False)
        raw_phone = request.POST.get('phone') or service_request.client_phone or "254708374149"
        phone = str(raw_phone).replace('+', '').replace(' ', '').replace('-', '')
        if phone.startswith('0'): phone = '254' + phone[1:]
        
        amount = int(float(service_request.service.price))
        if amount <= 0: return JsonResponse({'success': False, 'message': 'Invalid amount'})
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}".encode()).decode('utf-8')
        token = get_mpesa_access_token()
        
        if not token: return JsonResponse({'success': False, 'message': 'Auth failed'})
            
        payload = {
            "BusinessShortCode": MPESA_SHORTCODE, "Password": password, "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline", "Amount": amount, "PartyA": phone,
            "PartyB": MPESA_SHORTCODE, "PhoneNumber": phone,
            "CallBackURL": "https://example.com/callback/", 
            "AccountReference": f"OG{service_request.id}", "TransactionDesc": f"Pay{service_request.id}"
        }
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        response = requests.post('https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest', json=payload, headers=headers, timeout=30)
        
        print(f"🔍 SAFARICOM STATUS: {response.status_code} | BODY: {response.text}")
        
        if response.status_code == 200:
            res = response.json()
            if res.get('ResponseCode') == '0':
                service_request.mpesa_checkout_id = res['CheckoutRequestID']
                service_request.save()
                return JsonResponse({'success': True, 'message': 'M-Pesa prompt sent'})
            return JsonResponse({'success': False, 'message': res.get('errorMessage', 'Unknown Error')})
        return JsonResponse({'success': False, 'message': f'HTTP {response.status_code}'})
        
    except ServiceRequest.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Request not found'})
    except Exception as e:
        print(f"💥 PAYMENT ERROR: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
@csrf_exempt
def mpesa_callback(request):
    try:
        data = json.loads(request.body)
        callback = data['Body']['stkCallback']
        checkout_id = callback['CheckoutRequestID']
        req = ServiceRequest.objects.get(mpesa_checkout_id=checkout_id)
        
        if callback['ResultCode'] == 0:
            req.payment_status = 'paid'; req.status = 'processing'
            for item in callback['CallbackMetadata']['Item']:
                if item['Name'] == 'MpesaReceiptNumber': req.mpesa_receipt_number = item['Value']
            req.save()
            Notification.objects.create(user=req.user, title="💰 Payment Received", message=f"Payment for {req.service.name} confirmed.", notification_type='payment')
            return JsonResponse({'ResultCode': 0})
        else:
            req.payment_status = 'failed'; req.save()
            return JsonResponse({'ResultCode': 1})
    except Exception as e:
        return JsonResponse({'ResultCode': 1, 'ResultDesc': str(e)})

@login_required
def check_payment_status(request, request_id):
    try:
        req = ServiceRequest.objects.get(id=request_id, user=request.user)
        return JsonResponse({'status': req.payment_status, 'receipt': req.mpesa_receipt_number})
    except: return JsonResponse({'status': 'error'})

# ==========================================
# 🛠️ ADMIN DASHBOARD & MANAGEMENT
# ==========================================
@login_required
def admin_panel(request):
    if not request.user.is_superuser: return redirect('home')
    ctx = get_site_context()
    ctx['services'] = Service.objects.all().order_by('-created_at')
    ctx['all_requests'] = ServiceRequest.objects.select_related('user', 'service').order_by('-created_at')
    ctx['users'] = User.objects.filter(is_staff=False).order_by('-date_joined')
    ctx['total_revenue'] = ServiceRequest.objects.filter(payment_status='paid').aggregate(total=Sum('service__price'))['total'] or 0
    ctx['completed_requests'] = ServiceRequest.objects.filter(status='completed').count()
    return render(request, 'admin_panel.html', ctx)

@login_required
def update_site_settings(request):
    if not request.user.is_superuser: return redirect('home')
    if request.method == 'POST':
        setting, _ = SiteSetting.objects.get_or_create(id=1)
        if request.POST.get('site_name'): setting.site_name = request.POST['site_name']
        if request.POST.get('about_title'): setting.about_title = request.POST['about_title']
        if request.POST.get('about_content'): setting.about_content = request.POST['about_content']
        if request.FILES.get('logo'): setting.logo = request.FILES['logo']
        setting.save()
        messages.success(request, '✅ Settings updated!')
    return redirect('admin_panel')

@login_required
def add_nav_item(request):
    if not request.user.is_superuser: return redirect('home')
    if request.method == 'POST':
        NavigationItem.objects.create(label=request.POST.get('label'), url=request.POST.get('url'), is_active=True)
        messages.success(request, '✅ Link added!')
    return redirect('admin_panel')

@login_required
def delete_nav_item(request, item_id):
    if not request.user.is_superuser: return redirect('home')
    NavigationItem.objects.filter(id=item_id).delete()
    messages.success(request, '🗑️ Deleted!')
    return redirect('admin_panel')

# 🆕 NEW: Clear All Requests
@login_required
def clear_all_requests(request):
    if not request.user.is_superuser: return redirect('home')
    ServiceRequest.objects.all().delete()
    messages.success(request, '🗑️ All requests cleared successfully!')
    return redirect('admin_panel')

# 🆕 NEW: Complete Request & Notify Client
@login_required
def complete_request(request, request_id):
    if not request.user.is_superuser: return redirect('home')
    try:
        req = ServiceRequest.objects.get(id=request_id)
        req.status = 'completed'
        req.completed_at = datetime.now()
        req.admin_notes = request.POST.get('admin_notes', '')
        req.delivery_link = request.POST.get('delivery_link', '')
        req.save()
        
        Notification.objects.create(
            user=req.user,
            title='✅ Work Completed!',
            message=f'Your request for "{req.service.name}" is ready. {req.admin_notes or ""} {req.delivery_link or ""}',
            notification_type='completion'
        )
        messages.success(request, f'✅ Marked as completed! Client notified.')
    except Exception as e:
        messages.error(request, f'❌ Error: {str(e)}')
    return redirect('admin_panel')

# 🆕 NEW: Notification API
@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
    return JsonResponse({
        'count': Notification.objects.filter(user=request.user, is_read=False).count(),
        'items': [{'id': n.id, 'title': n.title, 'message': n.message, 'time': n.created_at.strftime('%I:%M %p')} for n in notifications]
    })

@login_required
def mark_notification_read(request, notif_id):
    Notification.objects.filter(id=notif_id, user=request.user).update(is_read=True)
    return JsonResponse({'success': True})

# ==========================================
# 📋 SERVICE MANAGEMENT
# ==========================================
@login_required
def create_service(request):
    if not request.user.is_superuser: return redirect('home')
    if request.method == 'POST':
        Service.objects.create(name=request.POST['name'], description=request.POST.get('description',''), price=request.POST['price'], is_active=True)
        messages.success(request, '✅ Service created!')
    return redirect('admin_panel')

@login_required
def update_service(request, service_id):
    if not request.user.is_superuser: return redirect('home')
    try:
        s = Service.objects.get(id=service_id)
        s.name = request.POST.get('name', s.name)
        s.description = request.POST.get('description', s.description)
        s.price = request.POST.get('price', s.price)
        s.save()
        messages.success(request, '✅ Service updated!')
    except: messages.error(request, '❌ Error updating')
    return redirect('admin_panel')

@login_required
def delete_service(request, service_id):
    if not request.user.is_superuser: return redirect('home')
    Service.objects.filter(id=service_id).delete()
    messages.success(request, '🗑️ Deleted!')
    return redirect('admin_panel')

# ==========================================
# 📱 STUB VIEWS
# ==========================================
def request_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    ServiceRequest.objects.create(user=request.user, service=service)
    messages.success(request, f'✅ Requested "{service.name}"!')
    return redirect('home')
def payment_success(r, id): return redirect('home')
def payment_cancel(r): return redirect('home')
def mpesa_wait(r, id): return redirect('home')
def check_status(r, id): return redirect('home')
def stripe_webhook(r): return JsonResponse({'status': 'ok'})
def api_request_status(r, id): return JsonResponse({'status': 'pending'})
def contact_submit(request):
    if request.method == 'POST':
        ContactMessage.objects.create(name=request.POST.get('name'), email=request.POST.get('email'), message=request.POST.get('message'))
        messages.success(request, '✅ Message sent!')
    return redirect('home')




# ==========================================
# 🖼️ PORTFOLIO MANAGEMENT
# ==========================================
@login_required
def admin_portfolio(request):
    if not request.user.is_superuser: return redirect('home')
    ctx = get_site_context()
    ctx['portfolio_items'] = PortfolioItem.objects.all().order_by('order', '-created_at')
    return render(request, 'admin_portfolio.html', ctx)

@login_required
def add_portfolio_item(request):
    if not request.user.is_superuser: return redirect('home')
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        category = request.POST.get('category', 'General')
        order = request.POST.get('order', 0)
        image = request.FILES.get('image')
        PortfolioItem.objects.create(
            title=title, description=description, category=category,
            order=int(order), image=image, is_active=True
        )
        messages.success(request, f'✅ "{title}" added to portfolio!')
    return redirect('admin_portfolio')

@login_required
def edit_portfolio_item(request, item_id):
    if not request.user.is_superuser: return redirect('home')
    try:
        item = PortfolioItem.objects.get(id=item_id)
        if request.method == 'POST':
            item.title = request.POST.get('title', item.title)
            item.description = request.POST.get('description', item.description)
            item.category = request.POST.get('category', item.category)
            item.order = int(request.POST.get('order', item.order))
            if request.FILES.get('image'):
                item.image = request.FILES['image']
            item.save()
            messages.success(request, f'✅ "{item.title}" updated!')
        return redirect('admin_portfolio')
    except PortfolioItem.DoesNotExist:
        messages.error(request, '❌ Item not found.')
        return redirect('admin_portfolio')

@login_required
def delete_portfolio_item(request, item_id):
    if not request.user.is_superuser: return redirect('home')
    try:
        item = PortfolioItem.objects.get(id=item_id)
        item.delete()
        messages.success(request, f'🗑️ "{item.title}" deleted.')
    except:
        messages.error(request, '❌ Error deleting.')
    return redirect('admin_portfolio')







