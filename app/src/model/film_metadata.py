
# from sqlalchemy.orm import declarative_base
from sqlalchemy import BigInteger, Column, Integer, String, Time, text
from src.db import Session, Base
from src.config import config
import pandas as pd
import datetime
import logging

class FilmMetadata(Base):
    __tablename__ = 'film_metadata'
    id = Column(BigInteger, primary_key=True)
    title = Column(String)
    group_l1 = Column(String)
    group_l2 = Column(String)
    genres = Column(String)
    actors = Column(String)
    directors = Column(String)
    country = Column(String)
    release_date = Column(String)
    release_year = Column(Integer)
    age_rating = Column(String)
    content_url = Column(String)
    description = Column(String)
    image_portrait = Column(String)
    image_url = Column(String)
    popularity = Column(String)
    total_watchers = Column(Integer)
    # search_text = row["content"],
    search_text = Column(String)

