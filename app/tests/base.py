import os
os.environ["testing"] = "1"
import tests.bootstrap
from datetime import datetime
import unittest
from unittest.mock import patch
import pandas as pd
from trino.dbapi import connect
from src.etl.reindex_film import ReindexFilm
from src.lib.google_token import GoogleToken
from src.model.film_metadata import FilmMetadata
from typing import List

from src.db import Session, truncate_db
from src.config import config
from sqlalchemy import text

import redis

import src.monkey_patch
def fixture_film_metadata():
    df = pd.read_json("./data/film_metadata.json", lines=True)

    session = Session()
    session.execute(text("DELETE FROM film_metadata"))

    for index, row in df.iterrows():
        session.add(FilmMetadata(
            id = row["id"],
            title = row["title"],
            group_l1 = row["group_l1"],
            group_l2 = row["group_l2"],
            genres = row["genres"],
            actors = row["actors"],
            directors = row["directors"],
            country = row["country"],
            release_date = row["release_date"],
            release_year = row["release_year"] if row["release_year"] != "" else None,
            age_rating = row["age_rating"],
            content_url = row["content_url"],
            description = row["description"],
            image_portrait = row["image_portrait"],
            image_url = row["image_url"],
            # popularity = row["popularity"],
            # total_watchers = row["total_watchers"],
            search_text = row["search_text"],
            popularity = "",
            total_watchers = 0
        ))

    session.commit()

def truncate_redis():
    redis_uri = os.environ.get("CELERY_BROKER_URL")
    r = redis.from_url(redis_uri)
    r.flushdb()

class BaseTest(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        truncate_db()
        truncate_redis()
        fixture_film_metadata()
    
    def assertContainAny(self, member: List[str], container: str, msg: str=None):
        contain_keyword = False
        for k in member:
            if k in container.lower():
                contain_keyword = True

        if msg is None:
            msg = container

        self.assertTrue(contain_keyword, msg=msg)

    def assertNotContainAny(self, member: List[str], container: str, msg: str=None):
        contain_keyword = False
        for k in member:
            if k in container.lower():
                contain_keyword = True

        if msg is None:
            msg = container

        self.assertFalse(contain_keyword, msg=msg)
           
    # @classmethod
    # def setUpClass(cls):
    #     fixture_film_metadata()