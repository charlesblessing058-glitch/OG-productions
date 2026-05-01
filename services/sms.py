import africastalking
from django.conf import settings
import os
from dotenv import load_dotenv

load_dotenv()

class SMSNotifier:
    def __init__(self):
        self.username = os.getenv('AFRICASTALKING_USERNAME', 'sandbox')
        self.api_key = os.getenv('AFRICASTALKING_API_KEY', '')
        self.sender_id = os.getenv('SENDER_ID', 'OGProds')
        self.sms = None
        
        # Initialize Africa's Talking
        if self.api_key:
            try:
                africastalking.initialize(self.username, self.api_key)
                self.sms = africastalking.SMS
            except Exception as e:
                print(f"⚠️ Failed to initialize SMS service: {e}")
                self.sms = None
    
    def send_sms(self, phone_number, message):
        """Send SMS to client"""
        if not self.api_key or not self.sms:
            print(f"📱 SMS Mock: Would send to {phone_number}: {message}")
            return {'status': 'mock', 'message': 'SMS sent (mock mode)'}
        
        try:
            # Format phone number
            phone = phone_number.replace(' ', '').replace('-', '')
            if phone.startswith('0'):
                phone = '+254' + phone[1:]
            elif phone.startswith('254') and not phone.startswith('+'):
                phone = '+' + phone
            
            # Send SMS
            response = self.sms.send(
                message=message,
                to=[phone],
                from_=self.sender_id
            )
            
            print(f"✅ SMS sent to {phone}: {response['SMSMessageData']['Recipients'][0]['statusCode']}")
            return response
            
        except Exception as e:
            print(f"❌ SMS error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def send_payment_confirmation(self, phone, request_id, service_name, amount):
        """Send payment confirmation SMS"""
        message = (
            f"OG Productions: Payment of KES {amount} received for {service_name}. "
            f"Request ID: {str(request_id)[:8]}... Status: Processing. "
            f"Track: ogproductions.com/track/{request_id}"
        )
        return self.send_sms(phone, message)
    
    def send_status_update(self, phone, request_id, new_status, service_name):
        """Send status update SMS"""
        status_messages = {
            'processing': 'We have started working on your project!',
            'completed': 'Your project is ready! Check your email for delivery.',
            'cancelled': 'Your request was cancelled. Contact us for assistance.'
        }
        message = (
            f"OG Productions: {service_name} - {status_messages.get(new_status, f'Status: {new_status}')} "
            f"Request ID: {str(request_id)[:8]}..."
        )
        return self.send_sms(phone, message)
    
    def send_admin_alert(self, admin_phone, message):
        """Send alert to admin"""
        full_message = f"🚨 OG Admin Alert: {message}"
        return self.send_sms(admin_phone, full_message)
