from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def add(x, y):
    """Simple test task to verify Celery is working."""
    return x + y


@shared_task
def send_test_email(to_email):
    """Send a test email asynchronously."""
    subject = 'Test Email from Celery'
    message = 'This is a test email sent via Celery task.'
    from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[to_email],
        fail_silently=False,
    )

    return f"Email sent to {to_email}"