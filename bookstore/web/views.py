import json
from uuid import uuid4
import datetime
from pytz import timezone

from django.contrib import messages
from django.shortcuts import render, HttpResponse, redirect
from django_celery_beat.models import PeriodicTask, CrontabSchedule

from web.forms import EmailForm
from web.tasks import send_email


def index(request):
    return render(request, 'index.html')

def send_instant_email(request):
    form = EmailForm()
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['body']
            send_email.delay(email, subject, body)
            messages.add_message(request, messages.INFO, 'Sent instant email')
        return redirect('/send_instant_email')

    context = {'form': form}
    return render(request, 'send_instant_email.html', context=context)

def send_scheduled_email(request):
    form = EmailForm()
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['body']
            schedule = request.POST['schedule']
            schedule_dt_obj = datetime.datetime.strptime(
                schedule, "%Y-%m-%dT%H:%M"
            )
            schedule_dt_obj = schedule_dt_obj.astimezone(timezone("UTC"))

            crontab_schedule, _ = CrontabSchedule.objects.get_or_create(
                minute=schedule_dt_obj.minute,
                hour=schedule_dt_obj.hour,
                day_of_week="*",
                day_of_month=schedule_dt_obj.day,
                month_of_year=schedule_dt_obj.month
            )

            randomstr = uuid4().hex
            PeriodicTask.objects.create(
                crontab=crontab_schedule,
                name=f"Send scheduled email - {randomstr}",
                task="web.tasks.send_email",
                args=json.dumps([email, subject, body])
            )

            messages.add_message(request, messages.INFO, 'Scheduled email')
        return redirect('/send_scheduled_email')

    context = {'form': form}
    return render(request, 'send_scheduled_email.html', context=context)
