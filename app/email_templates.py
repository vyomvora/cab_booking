"""This module defines the email templates for the application."""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


#Email configuration
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME', 'cabbook66@gmail.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'ybxq sheq rjjh lwgv')
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'Cab Booking Service <noreply@cabbooking.com>')

def send_booking_confirmation(current_user,booking, car, fare):
    """ 
    This function is used for sending cab booking confirmation email to user 
    """
    try:
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Your Cab Booking Confirmation'
        msg['From'] = EMAIL_FROM
        msg['To'] = current_user.email
        #HTML Email Template
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }}
                .header {{
                    background-color: #4a90e2;
                    color: white;
                    padding: 15px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    padding: 20px;
                }}
                .booking-details {{
                    background-color: #f9f9f9;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .detail-row {{
                    margin-bottom: 10px;
                }}
                .label {{
                    font-weight: bold;
                }}
                .footer {{
                    text-align: center;
                    padding: 15px;
                    font-size: 12px;
                    color: #777;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Booking Confirmation</h1>
                </div>
                <div class="content">
                    <p>Dear {current_user.name if hasattr(current_user, 'name') else 'Customer'},</p>
    
                    <p>Thank you for booking with our cab service. Your booking has been confirmed!</p>
                    
                    <div class="booking-details">
                        <div class="detail-row">
                            <span class="label">Booking ID:</span> {booking.id}
                        </div>
                        <div class="detail-row">
                            <span class="label">Date & Time:</span> {booking.booking_time.strftime('%d %B %Y, %I:%M %p')}
                        </div>
                        <div class="detail-row">
                            <span class="label">Car Type:</span> {car.model}
                        </div>
                        <div class="detail-row">
                            <span class="label">Pickup Location:</span> {booking.pickup_address}
                        </div>
                        <div class="detail-row">
                            <span class="label">Drop-off Location:</span> {booking.dropoff_address}
                        </div>
                        <div class="detail-row">
                            <span class="label">Estimated Fare:</span> €{fare:.2f}
                        </div>
                    </div>
                    <p>To view your booking details or make changes, please log in to your account.</p>                    
                </div>
            </div>
        </body>
        </html>
        """

        #Attach HTML content
        part = MIMEText(html, 'html')
        msg.attach(part)

        #Connect to mail server and send email
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, current_user.email, msg.as_string())
        server.quit()

        return True
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {str(e)}")
        return False

def send_booking_modification_email(user, booking, car, fare, original_data):
    """
    This function is used for sending cab modified booking email to user
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Your Cab Booking Has Been Modified'
        msg['From'] = EMAIL_FROM
        msg['To'] = user.email

        # Format old and new times
        old_time = original_data['journey_date'].strftime('%d %B %Y, %I:%M %p')
        new_time = booking.journey_date.strftime('%d %B %Y, %I:%M %p')

        # Identify changes
        changes = []
        if original_data['pickup_address'] != booking.pickup_address:
            changes.append(f"<strong>Pickup Location:</strong> {original_data['pickup_address']} → {booking.pickup_address}")
        if original_data['dropoff_address'] != booking.dropoff_address:
            changes.append(f"<strong>Dropoff Location:</strong> {original_data['dropoff_address']} → {booking.dropoff_address}")
        if old_time != new_time:
            changes.append(f"<strong>Date & Time:</strong> {old_time} → {new_time}")
        if original_data['car_model'] != car.model:
            changes.append(f"<strong>Car Type:</strong> {original_data['car_model']} → {car.model}")
        if original_data['estimated_fare'] != fare:
            changes.append(f"<strong>Fare:</strong> €{original_data['estimated_fare']:.2f} → €{fare:.2f}")

        changes_html = "<br>".join(changes) if changes else "No changes detected."

        # HTML Email Template
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                .header {{ background-color: #f39c12; color: white; padding: 15px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ padding: 20px; }}
                .booking-details, .changes {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .detail-row {{ margin-bottom: 10px; }}
                .label {{ font-weight: bold; }}
                .footer {{ text-align: center; padding: 15px; font-size: 12px; color: #777; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Booking Modification Confirmation</h1>
                </div>
                <div class="content">
                    <p>Dear {user.name},</p>
                    <p>Your cab booking has been successfully modified. Below are the updated details:</p>
                    
                    <div class="changes">
                        <h3>Changes Summary:</h3>
                        {changes_html}
                    </div>
                    
                    <div class="booking-details">
                        <h3>Updated Booking Details:</h3>
                        <div class="detail-row">
                            <span class="label">Booking ID:</span> {booking.id}
                        </div>
                        <div class="detail-row">
                            <span class="label">Pickup Location:</span> {booking.pickup_address}
                        </div>
                        <div class="detail-row">
                            <span class="label">Drop-off Location:</span> {booking.dropoff_address}
                        </div>
                        <div class="detail-row">
                            <span class="label">Date & Time:</span> {new_time}
                        </div>
                        <div class="detail-row">
                            <span class="label">Car Type:</span> {car.model}
                        </div>
                        <div class="detail-row">
                            <span class="label">Estimated Fare:</span> €{fare:.2f}
                        </div>
                    </div>                    
                </div>
            </div>
        </body>
        </html>
        """
        part = MIMEText(html, 'html')
        msg.attach(part)

        #Connect to mail server and send email
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, user.email, msg.as_string())
        server.quit()

        return True
    except smtplib.SMTPException as e:
        print(f"Error sending email: {str(e)}")
        return False



def send_booking_cancellation_email(user, booking):
    """
    This function is used for sending cab cancellation booking email to user
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Your Cab Booking Has Been Cancelled'
        msg['From'] = EMAIL_FROM
        msg['To'] = user.email

        booking_time = booking.journey_date.strftime('%d %B %Y, %I:%M %p')

        # HTML Email Template
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                .header {{ background-color: #e74c3c; color: white; padding: 15px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ padding: 20px; }}
                .booking-details {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .detail-row {{ margin-bottom: 10px; }}
                .label {{ font-weight: bold; }}
                .footer {{ text-align: center; padding: 15px; font-size: 12px; color: #777; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Booking Cancellation Confirmation</h1>
                </div>
                <div class="content">
                    <p>Dear {user.name},</p>
                    <p>Your cab booking has been successfully cancelled as per your request.</p>                    
                    <div class="booking-details">
                        <h3>Cancelled Booking Details:</h3>
                        <div class="detail-row">
                            <span class="label">Booking ID:</span> {booking.id}
                        </div>
                        <div class="detail-row">
                            <span class="label">Pickup Location:</span> {booking.pickup_address}
                        </div>
                        <div class="detail-row">
                            <span class="label">Drop-off Location:</span> {booking.dropoff_address}
                        </div>
                        <div class="detail-row">
                            <span class="label">Scheduled Date & Time:</span> {booking_time}
                        </div>
                    </div>
                    
                </div>
            </div>
        </body>
        </html> 
        """

        # Attach HTML content
        part = MIMEText(html, 'html')
        msg.attach(part)

        # Connect to mail server and send email
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, user.email, msg.as_string())
        server.quit()

        return True
    except smtplib.SMTPException as e:
        print(f"Error sending email: {str(e)}")
        return False
