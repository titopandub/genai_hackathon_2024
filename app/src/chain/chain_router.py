import logging
from ddtrace import tracer

from src.chain.chain_vidio_info import vidio_info_chain
from src.chain.chain_reco import ask_recommendation
from src.chain.chain_general import ask_general_question

from src.chain.model import model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableBranch

from guardrails import Guard
from guardrails.hub import (
    CompetitorCheck
)

import logging


logging.getLogger()
guard = Guard().use(CompetitorCheck(competitors=["Vision+", "Mola TV", "WeTV", "iQiyi", "Netflix", "Disney+ Hotstar", "Amazon Prime Video", "MAXStream", "Hulu", "HBO GO", "Apple TV+"], on_fail="exception"))


route_chain = (
    PromptTemplate.from_template(
        """You are chatbot for Vidio OTT platform        
Given the user question below, classify it as either being about
`recommendation` if question related to user want film recommendation
`other` otherwise

Do not respond with more than one word.

<user_query>
{user_query}
</user_query>

Classification:
"""
    ) | model | StrOutputParser() 
) 

@tracer.wrap(name="chat.ask",resource="router")
def run(context, user_query):
    logging.info("masuk run method")
    branch = RunnableBranch(
        (lambda x: "recommendation" in x["topic"], lambda x: ask_recommendation(context, user_query)),
        lambda x: vidio_info_chain(context, user_query)
    )
    full_chain = {"topic": route_chain, "user_query": lambda x: x["user_query"], "user_id": lambda x: x["user_id"]} | branch | StrOutputParser()

    response = full_chain.invoke({"user_query": user_query, "user_id": context["user_id"]}) 

    try:
        validation_outcome = guard.validate(llm_output=response)
        response = validation_outcome.validated_output
    except Exception as e:
        logging.error(e)
        response = "Maaf, kami terbatas dalam memberikan informasi spesifik tentang produk atau layanan Vidio.com. Untuk detail lebih lanjut, silakan merujuk langsung ke sumber resmi mereka."

    return response
