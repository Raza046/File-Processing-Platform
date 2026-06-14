import os
from celery import Celery
from kombu import Queue

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.update(
    broker_url=os.getenv("CELERY_BROKER_URL"),
)

app.autodiscover_tasks()

app.conf.task_queues = (
    Queue('image_queue', routing_key='image.#'),
    Queue('pdf_queue', routing_key='pdf.#'),
    Queue('csv_queue', routing_key='csv.#'),
)


app.conf.task_routes = {
    'files.tasks.process_pdf': {
        'queue': 'pdf_queue',
    },
    'files.tasks.process_image': {
        'queue': 'image_queue',
    },
    'files.tasks.process_csv': {
        'queue': 'csv_queue',
    },
}
