from celery import Celery
from celery.schedules import crontab


def init_celery():
    celery = Celery(
                    'app',
                     broker='redis://localhost:6379',
                     backend='redis://localhost:6379',
                     include=['app.tasks'],
                     result_expires=3600,
                     timezone = 'Europe/Moscow',
                     )

    return celery


celery_app = init_celery()

# # Optional configuration, see the application user guide.
# celery_app.conf.update(
#     result_expires=3600,
#     timezone = 'Europe/Moscow',
# )
# Default visibility_timeout 3600
celery_app.conf.broker_transport_options = {'visibility_timeout': 86400}  # 1 day

celery_app.conf.beat_schedule = {
    # Executes dayly at 0:00
    'add-dayly-at-0': {
        'task': 'app.tasks.create_mail_task',
        'schedule': crontab(hour=0, minute=0),
    },
}
