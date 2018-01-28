from __future__ import absolute_import
from celery import Celery
from kombu import Queue
from TripY.cluster_managment import default_config as CONFIG

app = Celery('TripY', broker=CONFIG.CELERY_BROKER_URL, backend=CONFIG.CELERY_RESULT_BACKEND,
             include=['TripY.worker'])
app.conf.task_create_missing_queues = True
