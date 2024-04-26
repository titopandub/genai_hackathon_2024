# from sqlalchemy.orm import declarative_base
from sqlalchemy import BigInteger, Column, Integer, String, Time
from src.db import Session, Base
import datetime
import logging

class FlatChat(Base):
    __tablename__ = 'flat_chat'
    id = Column(BigInteger, primary_key=True)
    time = Column(Time)
    user_id = Column(Integer)
    visit_id = Column(String)
    query = Column(String)
    route = Column(String)
    response = Column(String)
    suggestion = Column(String)

class Tracker:
    @staticmethod
    def track_chat(user_id, visit_id, query, response, suggestion, route):
        session = Session()
        flat_chat = FlatChat(time=datetime.datetime.utcnow(), user_id=user_id, visit_id=visit_id, query= query, response=response, suggestion=suggestion, route=route)

        try:
            session.add(flat_chat)
            session.commit()
            session.close()
        except Exception as e:
            logging.error(f"Error when track data: {e}")