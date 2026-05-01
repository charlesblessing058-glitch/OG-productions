import requests
import base64
from datetime import datetime
from django.conf import settings
import os
from dotenv import load_dotenv

load_dotenv()

class MpesaAPI:
    def __init__(self):
        self.env = os.getenv('MPESA_ENV', 'sandbox')
        self.consumer_key = os.getenv('MPESA_CONSUMER_KEY')
        self.consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
        self.shortcode = os.getenv('MPESA_SHORTCODE')
        self.passkey = os.getenv('MPESA_PASSKEY')
        self.base_url = 'https://sandbox.safaricom.co.ke' if self.env == 'sandbox' else 'https://api.safaricom.co.ke'
        
    def get_access_token(self):
        """Generate OAuth2 access token"""
        if not self.consumer_key or not self.consumer_secret:
            return None
        api_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(api_url, auth=(self.consumer_key, self.consumer_secret))
        if response.status_code == 200:
            return response.json().get('access_token')
        return None
    
    def generate_password(self):
        """Generate password for STK Push"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_string = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode('utf-8')
        return password, timestamp
    
    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """Initiate STK Push"""
        access_token = self.get_access_token()
        if not access_token:
            return {'error': 'Failed to get access token'}
        
        password, timestamp = self.generate_password()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,  # Customer phone
            "PartyB": self.shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": os.getenv('MPESA_CALLBACK_URL'),
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc
        }
        
        api_url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        response = requests.post(api_url, json=payload, headers=headers)
        
        return response.json()
    
    def check_transaction_status(self, checkout_request_id):
        """Check STK Push transaction status"""
        access_token = self.get_access_token()
        if not access_token:
            return {'error': 'Failed to get access token'}
        
        password, timestamp = self.generate_password()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }
        
        api_url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
        response = requests.post(api_url, json=payload, headers=headers)
        
        return response.json()
