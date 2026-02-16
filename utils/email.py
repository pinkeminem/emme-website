import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config


def send_contact_email(name, email, subject, message):
    if not Config.SMTP_HOST or not Config.SMTP_USER:
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = Config.SMTP_FROM or Config.SMTP_USER
        msg['To'] = Config.CONTACT_EMAIL
        msg['Subject'] = f'[emme-em.me] {subject}'
        msg['Reply-To'] = email

        body = f"From: {name} <{email}>\nSubject: {subject}\n\n{message}"
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
            server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASS)
            server.send_message(msg)

        return True
    except Exception as e:
        print(f'Email send failed: {e}')
        return False
