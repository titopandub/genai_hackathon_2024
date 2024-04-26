
import os
from celery import Celery
import ssl
from datetime import timedelta

celery = None

if "rediss" in os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379"):
    celery = Celery(__name__,
        broker_use_ssl = {
            'ssl_cert_reqs': ssl.CERT_NONE
        },
        redis_backend_use_ssl = {
            'ssl_cert_reqs': ssl.CERT_NONE
        }
    )
else:
    celery = Celery(__name__)

celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

celery.conf.beat_schedule = {
    'execute-reindex-schedule': {
        'task': 'reindex_schedule',  # Use the full name of the task if it's in a different file
        'schedule': timedelta(hours=1),  # sets the interval (every minute in this case)
    },
    'execute-reindex-film': {
        'task': 'reindex_film',
        'schedule': timedelta(hours=1)
    }
}