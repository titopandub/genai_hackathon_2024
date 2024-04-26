
from datetime import datetime
import os
import unittest
from tests.base import BaseTest
from unittest.mock import patch
import pandas as pd
from trino.dbapi import connect
from src.etl.reindex_film import ReindexFilm
from src.lib.google_token import GoogleToken
from src.model.film_metadata import FilmMetadata
from src.db import Session, Base
from tests.base import BaseTest
from src.config import config


class ReindexFilmTest(BaseTest):
    def setUp(self) -> None:
        super().setUp()
        self.file_path = "data/film_metadata_plain.json"

    def tearDown(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    @patch('src.etl.reindex_film.connect')
    @patch('pandas.read_sql_query')
    @patch.object(ReindexFilm, 'upload_blob')
    @patch.object(GoogleToken, 'get_token')
    @patch.object(ReindexFilm, 'reindex_from_gcs')
    def test_run(self,
                 reindex_from_gcs_func,
                 get_token_func,
                 upload_blob_func,
                 read_sql_query_func,
                 connect_func):
        read_sql_query_func.return_value = pd.DataFrame([{
            'id': 9372,
            'film_title': 'Ratu Adil',
            'group_name_l1': 'Series',
            'group_name_l2': 'Vidio Original',
            'film_main_genre': 'drama',
            'film_genres': 'action,crime,drama',
            'film_directors': 'ginanti rona,tommy dewo',
            'film_actors': 'dian sastrowardoyo',
            'country_group': 'Indonesia',
            'description': 'This is Ratu Adil description',
            'release_date': datetime.strptime('2024-02-29', '%Y-%m-%d'),
            'total_watchers': 140334,
            'age_rating': '18 or more',
            'image_portrait': 'https://example.com/image.jpg',
            'content_url': 'https://www.vidio.com/premier/9372',
            'image_url': 'https://www.vidio.com/premier/9372',
            'is_premium': True
        }])
        get_token_func.return_value = 'abcdef'

        ReindexFilm().run()

        self.assertTrue(os.path.exists(self.file_path))
        upload_blob_func.assert_called_with("genai_hackathon_2024", self.file_path, self.file_path)
        reindex_from_gcs_func.assert_called_with(
            'abcdef', config["project"], 'global',
            'film-metadata-202403191330_1710829784824',
            f"{config['gcs_bucket']}/data/film_metadata_plain.json"
            )

        session = Session()
        film_metadata = session.query(FilmMetadata).where(FilmMetadata.id == 9372).first()
        self.assertTrue(film_metadata is not None)