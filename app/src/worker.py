from datetime import timedelta
import src.bootstrap as _
from src.chain.chain_router import run
from src.service.vidio_chat import VidioChat
from src.etl.reindex_schedule import ReindexSchedule
from src.etl.reindex_film import ReindexFilm
from src.celery import celery
import uuid

@celery.task(name="process_chat")
def process_chat(context, prompt):
    request_id = str(uuid.uuid4())
    VidioChat.send_user_chat(request_id, context['token'], context['channel'], prompt)

    response = run(context, prompt)

    VidioChat.send_bot_chat(request_id, context['token'], context['channel'], response)

    return response


@celery.task(name="reindex_schedule")
def reindex_schedule():
    ReindexSchedule().run()


@celery.task(name="reindex_film")
def reindex_film():
    ReindexFilm().run()
