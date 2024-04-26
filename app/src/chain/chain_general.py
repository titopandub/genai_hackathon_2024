from typing import List
from ddtrace import tracer
import logging

from src.model.vector import film_repository as vector_search
from src.service.larva import Larva
from src.service.tracker import Tracker

from src.chain.model import model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


output_parser = StrOutputParser()

template_general = """Given a user's query on any topic, use your extensive database and understanding of various subjects to provide a clear, accurate, and helpful answer.
Prioritize directness and relevance in your response, ensuring it is informative and accessible to the user. If the question falls outside your expertise, offer guidance on where or how they might find the desired information.
Always communicate in a friendly and professional tone, fostering a positive user experience. Please answer according to user's query.

User Query: {user_query}
Answer: """
prompt_general = ChatPromptTemplate.from_template(template_general)
chain_general = prompt_general | model | output_parser

@tracer.wrap(name="chat.start",resource="general")
def ask_general_question(context, user_query):
    final_response = chain_general.invoke({"user_query": user_query}, track="general")

    Tracker.track_chat(context["user_id"], context["visit_id"], user_query, final_response, "", "other")

    return final_response