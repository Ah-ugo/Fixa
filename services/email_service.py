import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import random
import string
from db import users_collection
from dotenv import load_dotenv
import os
load_dotenv()

SMTP_PASSWORD=os.getenv('SMTP_PASSWORD')
EMAIL_FROM=os.getenv('EMAIL_FROM')
SMTP_USERNAME=os.getenv('EMAIL_FROM')
SMTP_SERVER=os.getenv('SMTP_SERVER')


class EmailService:
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = 465  # SSL port
        self.smtp_username = SMTP_USERNAME
        self.smtp_password = SMTP_PASSWORD
        self.sender_email = EMAIL_FROM
        self.otp_expiry_minutes = 15  # OTP validity period

    def send_email(self, recipient_email: str, subject: str, body: str, is_html=False):
        """
        Generic email sending function
        """
        try:
            # Create message container
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject

            # Attach the body
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            # Connect to server and send email
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.sender_email, recipient_email, msg.as_string())

            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def generate_otp(self, length=6):
        """Generate a numeric OTP of given length"""
        return ''.join(random.choices(string.digits, k=length))

    def store_otp(self, email: str, otp: str):
        """Store OTP in database with expiry time"""
        expiry_time = datetime.now() + timedelta(minutes=self.otp_expiry_minutes)
        users_collection.update_one(
            {"email": email},
            {"$set": {
                "otp": otp,
                "otp_expiry": expiry_time,
                "otp_attempts": 0  # Reset attempts
            }},
            upsert=True
        )

    def send_otp_email(self, email: str):
        """Send OTP email for account verification"""
        otp = self.generate_otp()
        self.store_otp(email, otp)

        subject = "Your Verification OTP"
        body = f"""
        <html>
            <body>
                <h2>Account Verification</h2>
                <p>Your OTP code is: <strong>{otp}</strong></p>
                <p>This code will expire in {self.otp_expiry_minutes} minutes.</p>
                <p>If you didn't request this, please ignore this email.</p>
            </body>
        </html>
        """

        return self.send_email(email, subject, body, is_html=True)

    def send_password_reset_email(self, email: str, reset_token: str):
        """Send password reset email with token"""
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

        subject = "Password Reset Request"
        body = f"""
        <html>
            <body>
                <h2>Password Reset</h2>
                <p>We received a request to reset your password. Click the link below to proceed:</p>
                <p><a href="{reset_link}">Reset Password</a></p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this, please ignore this email.</p>
            </body>
        </html>
        """

        return self.send_email(email, subject, body, is_html=True)

    def send_welcome_email(self, email: str, name: str):
        """Send welcome email after successful registration"""
        subject = "Welcome to Our Platform!"
        body = f"""
        <html>
            <body>
                <h2>Welcome, {name}!</h2>
                <p>Thank you for registering with us. Your account has been successfully created.</p>
                <p>Start exploring our platform and enjoy our services.</p>
                <p>If you have any questions, feel free to contact our support team.</p>
            </body>
        </html>
        """

        return self.send_email(email, subject, body, is_html=True)

    def verify_otp(self, email: str, otp: str):
        """Verify if the provided OTP is valid"""
        user = users_collection.find_one({"email": email})
        if not user:
            return {"error": "User not found"}

        # Check if OTP exists and hasn't expired
        if "otp" not in user or "otp_expiry" not in user:
            return {"error": "OTP not generated or expired"}

        if datetime.now() > user["otp_expiry"]:
            return {"error": "OTP expired"}

        # Check attempt limit (optional security measure)
        if user.get("otp_attempts", 0) >= 3:
            return {"error": "Too many attempts. Please request a new OTP."}

        # Increment attempt counter
        users_collection.update_one(
            {"email": email},
            {"$inc": {"otp_attempts": 1}}
        )

        if user["otp"] == otp:
            # Clear OTP after successful verification
            users_collection.update_one(
                {"email": email},
                {"$unset": {"otp": "", "otp_expiry": "", "otp_attempts": ""}}
            )
            return {"message": "OTP verified successfully"}
        else:
            return {"error": "Invalid OTP"}

    def generate_reset_token(self, email: str):
        """Generate and store a password reset token"""
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        expiry_time = datetime.now() + timedelta(hours=1)  # Token valid for 1 hour

        users_collection.update_one(
            {"email": email},
            {"$set": {
                "reset_token": token,
                "reset_token_expiry": expiry_time
            }}
        )

        return token