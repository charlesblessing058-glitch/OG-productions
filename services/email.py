from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import os
from dotenv import load_dotenv

load_dotenv()

class EmailNotifier:
    def __init__(self):
        self.from_email = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@ogproductions.com')
        self.admin_email = os.getenv('ADMIN_EMAIL', 'admin@ogproductions.com')
        
    def send_email(self, to_email, subject, text_message, html_message=None):
        """Send email with optional HTML version"""
        if not to_email:
            print("⚠️ No email address provided")
            return False
            
        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_message,
                from_email=self.from_email,
                to=[to_email]
            )
            if html_message:
                msg.attach_alternative(html_message, "text/html")
            msg.send(fail_silently=False)
            print(f"✅ Email sent to {to_email}: {subject}")
            return True
        except Exception as e:
            print(f"❌ Email error: {e}")
            return False
            
    def send_payment_confirmation(self, email, name, request_id, service_name, amount):
        """Send payment receipt email"""
        short_id = str(request_id)[:8]
        subject = f"✅ Payment Confirmed - {service_name} (OG Productions)"
        
        text = f"""Hello {name},

Thank you for your payment of KES {amount} for {service_name}.

Request ID: {request_id}
Status: Processing

We'll notify you via SMS and email as your project progresses.

Best regards,
OG Productions Team
        """.strip()
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #28a745;">✅ Payment Confirmed!</h2>
            <p>Hello <strong>{name}</strong>,</p>
            <p>Thank you for your payment of <strong>KES {amount}</strong> for <strong>{service_name}</strong>.</p>
            <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                <tr style="background: #f8f9fa;"><td style="padding: 10px; border: 1px solid #ddd;"><strong>Request ID</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{request_id}</td></tr>
                <tr><td style="padding: 10px; border: 1px solid #ddd;"><strong>Status</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;"><span style="background: #ffc107; color: #000; padding: 3px 8px; border-radius: 4px;">PROCESSING</span></td></tr>
            </table>
            <p>We'll notify you via SMS and email as your project progresses.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="color: #666; font-size: 14px;">Best regards,<br><strong>OG Productions Team</strong></p>
        </div>
        """
        return self.send_email(email, subject, text, html)
        
    def send_status_update(self, email, name, request_id, service_name, status):
        """Send status change notification"""
        status_config = {
            'processing': {'emoji': '', 'color': '#ffc107', 'msg': 'We have started working on your project!'},
            'completed': {'emoji': '✅', 'color': '#28a745', 'msg': 'Your project is ready for delivery!'},
            'cancelled': {'emoji': '❌', 'color': '#dc3545', 'msg': 'Your request has been cancelled.'}
        }
        config = status_config.get(status, {'emoji': '📢', 'color': '#6c757d', 'msg': f'Status updated to {status}'})
        
        subject = f"{config['emoji']} Status Update: {service_name} - {status.upper()}"
        
        text = f"""Hello {name},

Your request for {service_name} (ID: {request_id}) status has been updated to: {status.upper()}

{config['msg']}

Best regards,
OG Productions Team
        """.strip()
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: {config['color']};">{config['emoji']} Status Update</h2>
            <p>Hello <strong>{name}</strong>,</p>
            <p>Your request for <strong>{service_name}</strong> has been updated:</p>
            <h3 style="background: {config['color']}; color: #000; padding: 10px; border-radius: 5px; text-align: center;">{status.upper()}</h3>
            <p><strong>Request ID:</strong> {request_id}</p>
            <p>{config['msg']}</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="color: #666; font-size: 14px;">Best regards,<br><strong>OG Productions Team</strong></p>
        </div>
        """
        return self.send_email(email, subject, text, html)
