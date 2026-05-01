from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Authentication
    path('login/', views.client_login, name='login'),
    path('register/', views.client_register, name='register'),
    path('logout/', views.client_logout, name='logout'),
    
    # Service requests
    path('request/<int:service_id>/', views.request_service, name='request_service'),
    path('request/submit/', views.submit_request, name='submit_request'),
    
    # Contact
    path('contact/submit/', views.contact_submit, name='contact_submit'),
    
    # M-Pesa payment
    path('payment/mpesa/<int:request_id>/', views.initiate_mpesa_payment, name='initiate_mpesa_payment'),
    path('payment/status/<int:request_id>/', views.check_payment_status, name='check_payment_status'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    
    # Admin panel routes
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/settings/', views.update_site_settings, name='update_site_settings'),
    path('admin-panel/nav/add/', views.add_nav_item, name='add_nav_item'),
    path('admin-panel/nav/<int:item_id>/delete/', views.delete_nav_item, name='delete_nav_item'),
    path('admin-panel/service/add/', views.create_service, name='create_service'),
    path('admin-panel/service/<int:service_id>/edit/', views.update_service, name='update_service'),
    path('admin-panel/service/<int:service_id>/delete/', views.delete_service, name='delete_service'),
    path('admin-panel/requests/clear/', views.clear_all_requests, name='clear_all_requests'),
    path('admin-panel/portfolio/', views.admin_portfolio, name='admin_portfolio'),
    path('admin-panel/portfolio/add/', views.add_portfolio_item, name='add_portfolio_item'),
    path('admin-panel/portfolio/<int:item_id>/edit/', views.edit_portfolio_item, name='edit_portfolio_item'),
    path('admin-panel/portfolio/<int:item_id>/delete/', views.delete_portfolio_item, name='delete_portfolio_item'),
    path('admin-panel/request/<int:request_id>/complete/', views.complete_request, name='complete_request'),
    
    # API endpoints
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('api/notifications/<int:notif_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # User dashboard
    path('my-dashboard/', views.my_dashboard, name='my_dashboard'),
    
    # Payment success/cancel
    path('payment/success/<int:request_id>/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    
    # M-Pesa wait page
    path('mpesa/wait/<int:request_id>/', views.mpesa_wait, name='mpesa_wait'),
    
    # Status check API
    path('api/status/<int:request_id>/', views.check_status, name='check_status'),
    
    # Stripe webhook (if used)
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    
    # Request status API
    path('api/request/<int:request_id>/status/', views.api_request_status, name='api_request_status'),
]
