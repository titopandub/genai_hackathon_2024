from datetime import datetime
from ddtrace import tracer
from src.model.vector import vidio_info_repository
from src.chain.model import model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from src.service.tracker import Tracker

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import RedisChatMessageHistory

import logging
import os



@tracer.wrap(name="chat.start",resource="vidio-info")
def vidio_info_chain(context, user_query):
    logging.info("masuk vidio info")
    prompt = (
"""You are chatbot for Vidio OTT platform. Your task is to answer to user question. Answer with language same as user question.
You are a chatbot for the Vidio OTT platform. Today's date is {today}. When responding to user questions, provide information, schedules, or match details only if they are scheduled for a future date relative to {today}. If all provided information pertains to past dates, respond with "I don't have the current information." Avoid giving any outdated information about schedules or matches.

Questions can be related to Vidio products, games, films, or other topics.

For queries specifically about games or arcade games available on Vidio, limit your response to three relevant game options and include direct links for users to play these games.

Here are userful information:
{information} 
""")
    information = vidio_info_repository.search(user_query)
    logging.info("masuk vidio info - done search")

    today_date = datetime.now().strftime("%d %B %Y")

    prompt_message = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{user_query}"),
        ]
    )

    chain = prompt_message | model

    redis_uri = os.environ.get("CELERY_BROKER_URL")

    chain_with_history = (RunnableWithMessageHistory(
        chain,
        lambda session_id: RedisChatMessageHistory(
            session_id, url=redis_uri, ttl=600
        ),
        input_messages_key="user_query",
        history_messages_key="history",
    ) | StrOutputParser())

    config = {"configurable": {"session_id":context["visit_id"]}}
    logging.info("masuk vidio info - sebelum invoke")
    resp = chain_with_history.invoke({"user_query": user_query, "information": information, "today": today_date},config=config, track="vidio-info")
    logging.info("masuk vidio info - setelah invoke")

    logging.info("masuk vidio info - sebelum tracker")
    Tracker.track_chat(context["user_id"], context["visit_id"], user_query, resp, information, "vidio-info")
    logging.info("masuk vidio info - setelah tracker")

    return resp