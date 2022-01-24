from django.core.mail import send_mail

from bookstore.celery import app


@app.task
def send_email(to, subject, body):
    send_mail(
        subject,
        body,
        'from-default@gmail.com',
        [to]
    )
