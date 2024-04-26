from typing import List
from ddtrace import tracer
import logging

from src.model.vector import film_repository as vector_search
from src.service.larva import Larva
from src.service.tracker import Tracker

from src.chain.model import model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser




class Recommendation(BaseModel):
    id: int = Field(description="ID of the content")
    title: str = Field(description="title of the content, use title case for this")
    explanation: str = Field(description="why you recommend this content")

class RecommendationList(BaseModel):
    __root__: List[Recommendation]

def parse_final_response(final_response):
    items = []
    for item in final_response['items']:
        try:
            image, link = vector_search.get_image_link(item['id'])
            items.append(f"* Judul: **{item['title']}**\n\n  Kenapa kamu suka: {item['explanation']}\n\n  [![{item['title']}]({image})]({link})")
        except:
            logging.warning(f"[chain_reco] film {item['id']} not exist in alloy")
    return "\n\n\n".join(items)

def need_recommendation(text):
    return text.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']

def get_user_profile(user_gender, user_age):
    return f"User Profile: {user_gender} {user_age}" if user_gender != "" and user_age != -1 else ""

output_parser = StrOutputParser()
json_parser = JsonOutputParser(pydantic_object=RecommendationList)

template_need_vector_search = """You are Chat Recommendation Engine, your job is to decide if we need to summarize User Query and look up to Vector Search or not.
User Query: {user_query}
Summarize the User Query as context to look up to Vector Search. If there is no context need to look up, you can answer with empty."""
prompt_need_vector_search = ChatPromptTemplate.from_template(template_need_vector_search)

template_recommendation = """You are content expert from OTT company.
Your task is to give recommendation based on User Query, Movie Data retrieved from Vector Search and User History.
The answer in **Bahasa Indonesia**, give **5 (five)** recommendation, re-rank the recommendation based on User Query and User History relevancy.
{format_instructions}
Always use title case for title field.
Do not recommend content from User History unless it really relevant for them based on their query.
Give the explanation for each content why it relevant for the user based on the User Query, User Profile, Vector Search Result and User History. The explanation should show only if it is relevant to be shown to user and summarize it based on User Query and User History.

Here is the context.
{user_profile}

User Query: {user_query}

Vector Search Result:
{vector_search_result}

User History:
{user_history}"""
prompt_recommendation = PromptTemplate(
    template=template_recommendation,
    input_variables=["user_query", "vector_search_result", "user_history"],
    partial_variables={"format_instructions": json_parser.get_format_instructions()},
)

chain_need_vector_search = prompt_need_vector_search | model | output_parser
chain_recommendation = prompt_recommendation | model | json_parser

@tracer.wrap(name="chat.ask",resource="reco_ask_recommendation")
def ask_recommendation(context, user_query):
    logging.info("masuk reco")
    user_id = context['user_id']
    user_profile = get_user_profile(context["user_gender"], context["user_age"])

    span = tracer.trace(name="llm.query", resource="chain_need_vector_search")
    chain_need_vector_search_response = chain_need_vector_search.invoke({"user_query": user_query})
    span.finish()

    history_film_ids = Larva.get_play_history_film(user_id)
    user_history = vector_search.lookup_film(history_film_ids)
    vector_search_result = vector_search.get_grounding(chain_need_vector_search_response, history_film_ids)

    final_response = chain_recommendation.invoke({
        "user_query": user_query, 
        "user_profile": user_profile,
        "vector_search_result": vector_search_result, 
        "user_history": user_history
    }, track="chain_recommendation")
    span.finish()

    final_response = parse_final_response(final_response)


    Tracker.track_chat(context["user_id"], context["visit_id"], user_query, final_response, vector_search_result, "recommendation")

    return final_response