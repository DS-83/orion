from __future__ import absolute_import, unicode_literals

from celery import Celery

# celery_app = Celery('app',
#              broker='redis://localhost:6379',
#              backend='redis://localhost:6379',
#              include=['app.tasks'])
#
# # Optional configuration, see the application user guide.
# celery_app.conf.update(
#     result_expires=3600,
#     timezone = 'Europe/Moscow',
# )
#
# class ContextTask(celery_app.Task):
#     def __call__(self, *args, **kwargs):
#         with current_app.app_context():
#             return self.run(*args, **kwargs)
#
# celery_app.Task = ContextTask


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

if __name__ == '__main__':
    celery_app.start()


# def init_celery():
#     celery_app = Celery('app',
#          broker='redis://localhost:6379',
#          backend='redis://localhost:6379',
#          include=['app.tasks']
#     )
#     celery_app.conf.update(
#         result_expires=3600,
#         timezone = 'Europe/Moscow',
#     )
#
#     class ContextTask(celery_app.Task):
#         def __call__(self, *args, **kwargs):
#             with current_app.app_context():
#                 return self.run(*args, **kwargs)
#
#     celery_app.Task = ContextTask
#     return celery_app
