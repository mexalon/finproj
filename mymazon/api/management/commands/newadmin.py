import os

from django.conf import settings
from django.core.management.base import BaseCommand

from api.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        email = os.getenv('SUPERUSER_EMAIL', 'admin@admin.com')
        password = os.getenv('SUPERUSER_PASSWORD', 'admin')
        if email and password:
            try:
                admin = User.objects.filter(email=email)
            except Exception:
                print(f'No valid email')
                return
            else:
                if admin:
                    print(f'user {email} already exist')
                    return
            try:
                admin = User.objects.create_superuser(email=email, username='admin', password=password)
            except Exception:
                print(f'No valid email or user already exists')
                return
            else:
                admin.is_active = True
                admin.is_admin = True
                admin.save()
                print(f'Superuser {email} created')
        else:
            print(f'There is No superuser email and pass env!')
