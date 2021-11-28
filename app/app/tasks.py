from __future__ import absolute_import, unicode_literals
from core.models import Task
from datetime import datetime
from celery import shared_task
from celery import Celery
from celery.schedules import crontab
from celery import current_app
app = current_app._get_current_object()

nowutc = datetime.utcnow()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # # Calls test('hello') every 10 seconds.
    # sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')

    # # Calls test('world') every 30 seconds
    # sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # # Executes every Monday morning at 7:30 a.m.
    # sender.add_periodic_task(
    #     crontab(hour=7, minute=30, day_of_week=1),
    #     test.s('Happy Mondays!'),
    # )

    
    # sender.add_periodic_task(2.0, change_task_status(), name='change status task')
    # Calls task every 10 seconds.
    sender.add_periodic_task(10.0, change_task_status(), name='change status task')


# Task
def try_parsing_date(text: str):
    for fmt in ["%Y-%m-%d %H:%M:%S.%f+00:00", "%Y-%m-%d %H:%M:%S+00:00", 
                    "%Y-%m-%d%H:%M:%S.%f+00:00", "%Y-%m-%dT%H:%M:%S.%fZ", "Y-%m-%d %H:%M:%S.%f",
                    "%Y-%m-%d%H:%M:%S.%f"]:
        return datetime.strptime(str(text), fmt)


@app.task
def change_task_status():
    pending_task = Task.objects.filter(status="pending")
    for row in pending_task:
        rows = Task.objects.filter(status="pending").update(status="expired") if \
        try_parsing_date(str(row.deadline)) < nowutc else None
    return dict()
