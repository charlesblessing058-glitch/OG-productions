from django.db import models
from django.contrib.auth.models import User

# Choices
STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]

PAYMENT_CHOICES = [
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('failed', 'Failed'),
]

class SiteSetting(models.Model):
    site_name = models.CharField(max_length=100, default='Original Grand Productions')
    contact_email = models.EmailField(default='hello@originalgrand.com')
    contact_phone = models.CharField(max_length=20, default='+254 700 000 000')
    location = models.CharField(max_length=100, default='Nairobi, Kenya')
    about_title = models.CharField(max_length=200, default='About Original Grand Productions')
    about_content = models.TextField(default='We are a creative agency dedicated to bringing your vision to life.')
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    about_document = models.FileField(upload_to='about_docs/', null=True, blank=True)

    def __str__(self):
        return self.site_name

class NavigationItem(models.Model):
    label = models.CharField(max_length=50)
    custom_text = models.CharField(max_length=100, blank=True)
    url = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def get_display_text(self):
        return self.custom_text if self.custom_text else self.label.title()

    def __str__(self):
        return self.get_display_text()

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ServiceRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_requests')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=20)
    notes = models.TextField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='pending')
    
    # M-Pesa Fields
    mpesa_checkout_id = models.CharField(max_length=100, blank=True, null=True)
    mpesa_receipt_number = models.CharField(max_length=100, blank=True, null=True)
    mpesa_phone = models.CharField(max_length=20, blank=True, null=True)
    mpesa_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Admin Delivery Fields
    admin_notes = models.TextField(blank=True, null=True, help_text='Admin delivery notes')
    delivery_link = models.URLField(blank=True, null=True, help_text='Link to completed work')
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service.name} - {self.user.username}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=20, default='info')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.user.username})"


class PortfolioItem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='portfolio/', null=True, blank=True)
    category = models.CharField(max_length=50, default='General')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title
