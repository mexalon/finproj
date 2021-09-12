import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


import smtplib
import ssl

from celery import shared_task
from django.conf import settings




def gmail_it(to, subject, text):
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
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())


@shared_task
def send_email(subject, text, to_list: list):
    [gmail_it(to, subject, text) for to in to_list]
    return f"{to_list}>>{subject}>>{text}"


""" Без этого не хочет работать из под винды """
""" celery -A mymazon  worker -l INFO -P eventlet """