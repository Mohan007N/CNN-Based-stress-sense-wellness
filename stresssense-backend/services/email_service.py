"""
services/email_service.py — Email Service using Resend API
===========================================================
Handles all email communications using Resend API.
"""

import logging
import requests
from flask import current_app

logger = logging.getLogger(__name__)


class EmailService:
    """Email service using Resend API"""
    
    @staticmethod
    def send_email(to: str, subject: str, html: str, text: str = None):
        """
        Send email using Resend API
        
        Args:
            to: Recipient email address
            subject: Email subject
            html: HTML content
            text: Plain text content (optional)
        
        Returns:
            dict: Response from Resend API
        """
        try:
            api_key = current_app.config.get('RESEND_API_KEY')
            from_email = current_app.config.get('EMAIL_FROM')
            
            if not api_key:
                logger.error("RESEND_API_KEY not configured")
                return {"success": False, "error": "Email service not configured"}
            
            url = "https://api.resend.com/emails"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "from": from_email,
                "to": [to],
                "subject": subject,
                "html": html
            }
            
            if text:
                payload["text"] = text
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"Email sent successfully to {to}")
                return {"success": True, "data": response.json()}
            else:
                logger.error(f"Failed to send email: {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Email service error: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def send_welcome_email(user_email: str, user_name: str):
        """Send welcome email to new user"""
        subject = "Welcome to StressSense! 🎉"
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to StressSense!</h1>
                </div>
                <div class="content">
                    <h2>Hi {user_name},</h2>
                    <p>Thank you for joining StressSense! We're excited to help you monitor and improve your workplace wellness.</p>
                    
                    <h3>What's Next?</h3>
                    <ul>
                        <li>Complete your wellness baseline assessment</li>
                        <li>Enable camera access for emotion detection</li>
                        <li>Explore your personalized dashboard</li>
                        <li>Track your stress levels over time</li>
                    </ul>
                    
                    <a href="http://localhost:8080/dashboard" class="button">Go to Dashboard</a>
                    
                    <p>If you have any questions, feel free to reach out to our support team.</p>
                    
                    <p>Best regards,<br>The StressSense Team</p>
                </div>
                <div class="footer">
                    <p>StressSense | 410 Market St, San Francisco, CA</p>
                    <p>hello@stresssense.app | +1 (555) 010-2025</p>
                    <p>Developed by Mohana Krishnan</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(user_email, subject, html)
    
    @staticmethod
    def send_stress_alert_email(user_email: str, user_name: str, stress_level: str):
        """Send stress alert email"""
        subject = f"⚠️ Stress Alert: {stress_level} Level Detected"
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #ef4444; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .alert {{ background: #fee2e2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; }}
                .tips {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ Stress Alert</h1>
                </div>
                <div class="content">
                    <h2>Hi {user_name},</h2>
                    
                    <div class="alert">
                        <strong>We've detected {stress_level} stress levels in your recent activity.</strong>
                    </div>
                    
                    <p>Your wellbeing is important. Here are some immediate actions you can take:</p>
                    
                    <div class="tips">
                        <h3>Quick Stress Relief Tips:</h3>
                        <ul>
                            <li>Take a 5-minute break and practice deep breathing</li>
                            <li>Step away from your desk and stretch</li>
                            <li>Drink a glass of water</li>
                            <li>Talk to a colleague or friend</li>
                            <li>Consider rescheduling non-urgent tasks</li>
                        </ul>
                    </div>
                    
                    <p>If stress persists, please consider speaking with your manager or HR representative.</p>
                    
                    <p>Take care,<br>The StressSense Team</p>
                </div>
                <div class="footer">
                    <p>StressSense | 410 Market St, San Francisco, CA</p>
                    <p>hello@stresssense.app | +1 (555) 010-2025</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(user_email, subject, html)
