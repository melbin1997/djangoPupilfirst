import time

from celery.decorators import periodic_task
from datetime import datetime, timedelta
from tasks.models import ReportConfig
from tasks.models import Task, Notification
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Count

from task_manager.celery import app

import redis

REDIS_CLIENT = redis.Redis()

def only_one(function=None, key="", timeout=None):
    """Enforce only one celery task at a time."""

    def _dec(run_func):
        """Decorator."""

        def _caller(*args, **kwargs):
            """Caller."""
            ret_value = None
            have_lock = False
            lock = REDIS_CLIENT.lock(key, timeout=timeout)
            try:
                have_lock = lock.acquire(blocking=False)
                if have_lock:
                    ret_value = run_func(*args, **kwargs)
            finally:
                if have_lock:
                    lock.release()

            return ret_value

        return _caller

    return _dec(function) if function is not None else _dec

# @periodic_task(run_every=timedelta(seconds=10))
def send_email_reminder():
    print("Starting to process emails")
    for user in User.objects.all():
        pending_qs = Task.objects.filter(user=user, deleted=False, completed=False)
        email_content = f"You have {pending_qs.count()} pending tasks."
        send_mail("Pending Tasks from Task Manager", email_content, "tasks@taskmanager.com", [user.email])
        print(f'Completed email processing for user : {user.id}')


@app.task
def test_background_job():
    for i in range(10):
        time.sleep(1)
        print(i)


@periodic_task(run_every=timedelta(seconds=1))
# @only_one(key="SingleTask", timeout=60 * 5)
def send_task_summary():
    currentTime = datetime.now()
    # print(currentTime)
    

    for email_config in ReportConfig.objects.all():
        # print("Count",Notification.objects.filter(timestamp__gte=datetime.now().date(), user=email_config.user).count())
        if Notification.objects.filter(timestamp__gte=datetime.now().date(), user=email_config.user).count() == 0 and currentTime.time() > email_config.time:
            qs = Task.objects.filter(user = email_config.user, deleted = False).values('status').annotate(total=Count('id')).order_by('status')
            email_content = f'Hi {email_config.user.username}\nPlease find the below task summary :\n'
            for task_summary in qs:
                email_content += f"{task_summary.get('status')} : {task_summary.get('total')}\n"
            # print(email_content)
            send_mail("Task Summary", email_content, "tasks@taskmanager.com", [email_config.user.email])
            Notification(user=email_config.user, content = email_content).save()
            print(f'Completed task summary email for user : {email_config.user.username} for today with content : {email_content}')
