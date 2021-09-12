import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from celery import shared_task
from django.conf import settings
import json


def gmail_it(to, subject, text, content):
    port = settings.EMAIL_HOST_PORT
    smtp_server = "smtp.gmail.com"
    sender_email = settings.EMAIL_HOST_USER
    receiver_email = to
    password = settings.EMAIL_HOST_PASSWORD

    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = to

    message.attach(MIMEText(text, "plain"))
    if content:
        attachment = MIMEText(content)
        attachment.add_header('Content-Disposition', 'attachment',
                              filename="content.json")
        message.attach(attachment)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())


@shared_task
def send_email(subject, text, to_list: list, content=None):
    [gmail_it(to, subject, text, content) for to in to_list]
    return f"{to_list}>>{subject}>>{text}"


""" Без этого не хочет работать из под винды """
""" celery -A mymazon  worker -l INFO -P eventlet """
