from datetime import datetime
import logging
import os
import pandas as pd
import requests
from src.config import config
from trino.dbapi import connect
from google.cloud import storage
from src.lib.google_token import GoogleToken
from src.db import Session
from src.model.film_metadata import FilmMetadata
from sqlalchemy import text


class ReindexFilm():
    def run(self):
        conn = connect(
            host=os.environ.get("TRINO_HOST", ""),
            port=os.environ.get("TRINO_PORT", ""),
            user=os.environ.get("TRINO_USER", ""),
            catalog="hive",
        )
        _ = conn.cursor()
        film_df = pd.read_sql_query(self.generate_sql_query(), conn)
        film_df = self.preprocess_film_metadata(film_df)
        film_df.to_json('data/film_metadata_plain.json', orient='records', lines=True)
        self.upload_blob('genai_hackathon_2024', 'data/film_metadata_plain.json', 'data/film_metadata_plain.json')
        self.reindex_film()
        self.update_film_metadata_db(film_df)
    
    def generate_sql_query(self):
        return f"""
SELECT 
    DISTINCT(dayshift.vod_metadata.film_id) as id, 
    dayshift.vod_metadata.film_title, 
    group_name_l1, 
    group_name_l2, 
    film_main_genre, 
    film_genres, 
    film_directors, 
    film_actors, 
    country_group, 
    films.description, 
    films.release_date, 
    film_rating as age_rating,
    image_portrait,
    concat('https://www.vidio.com/premier/', cast(films.id as varchar)) as content_url,
    concat('https://thumbor.prod.vidiocdn.com/', to_base64url(hmac_sha1(cast(concat('223x332/filters:quality(75)/vidio-web-prod-film/uploads/film/image_portrait/', cast(films.id as varchar), '/', films.image_portrait) as varbinary), cast('cheeky rando' as varbinary))), '/', concat('223x332/filters:quality(75)/vidio-web-prod-film/uploads/film/image_portrait/', cast(films.id as varchar), '/', films.image_portrait)) as image_url
    -- CASE WHEN premium_contents.premiumable_id IS NULL THEN FALSE ELSE TRUE END as is_premium
FROM dayshift.vod_metadata
LEFT JOIN vidio_production.films as films ON dayshift.vod_metadata.film_id = films.id
-- LEFT JOIN vidio_web.public.premium_contents as premium_contents ON dayshift.vod_metadata.film_id = premium_contents.premiumable_id AND premium_contents.premiumable_type = 'Film'
WHERE
dayshift.vod_metadata.film_id IS NOT NULL
AND film_published = true
AND film_deleted = false
AND video_published = true
"""

    def preprocess_film_metadata(self, df):
        df.fillna('', inplace=True)
        df['id'] = df['id'].astype(str)
        df['title'] = df['film_title'].str.lower()
        df['group_l1'] = df['group_name_l1'].str.lower()
        df['group_l2'] = df['group_name_l2'].str.lower()
        df['genres'] = df['film_genres'].apply(lambda x: x.split(','))
        df['actors'] = df['film_actors'].apply(lambda x: x.split(','))
        df['directors'] = df['film_directors'].apply(lambda x: x.split(','))
        # df.loc[df['actors'] == "various", 'actors'] = ""
        df['country'] = df['country_group'].str.lower()
        # df['total_watchers'] = df['total_watchers'].astype('int')
        df['release_date'] = df['release_date'].astype(str)
        df['release_date'] = df['release_date'].str.replace(" 00:00:00", "")
        df['release_year'] = df['release_date'].apply(lambda x: str(datetime.strptime(str(x), "%Y-%m-%d").year) if x != '' else '')

        def popularity(total_watchers):
            if total_watchers >= 50000:
                return "trending"
            elif total_watchers < 50000 and total_watchers >= 500:
                return "average"
            else:
                return "below average"

        # df['popularity'] = df['total_watchers'].apply(lambda x: popularity(x))
        search_text_columns = ['title', 'description', 'group_l1', 'group_l2', 'film_main_genre', 'genres', 'directors', 'actors', 'country', 'release_year', 'age_rating']
        df['search_text'] = df[search_text_columns].apply(lambda row: self.search_text(*row), axis=1)
        df.rename(columns={'search_text': 'content', "content_uri": "uri"}, inplace=True)
        df = df.loc[:,~df.columns.duplicated()]
        df.drop(columns=['film_title', 'group_name_l1', 'group_name_l2', 'film_main_genre', 'film_genres', 'film_directors', 'film_actors', 'country_group'], inplace=True)
        return df

    def search_text(self, title, description, group_l1, group_l2, main_genre, genres, directors, actors, country, release_year, age_rating):
        genres = ', '.join(genres)
        actors = ', '.join(actors)
        directors = ', '.join(directors)
        return f"""title: {title}
actors: {actors}
group: {group_l1} > {group_l2}
genres: {main_genre}, {genres}
directors: {directors}
description: {description}
country: {country}
release year: {release_year}
age rating: {age_rating}"""

    def upload_blob(self, bucket_name, source_file_name, destination_blob_name):
        storage.blob._DEFAULT_CHUNKSIZE = 35 * 1024 * 1024  # 35 MB
        storage.blob._MAX_MULTIPART_SIZE = 35 * 1024 * 1024  # 35 MB

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)

    def reindex_film(self):
        token = GoogleToken().get_token()
        project_id = config["project"]
        location = "global"
        data_store_id = config['data_store']['reindex_film_datastore']
        gcs_url = f"{config['gcs_bucket']}/data/film_metadata_plain.json"
        self.reindex_from_gcs(token, project_id, location, data_store_id, gcs_url)
        logging.info("success reindex from Vidio Schedule")

    def reindex_from_gcs(self, token, project_id, location, data_store_id, gcs_url):
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data={
            "reconciliationMode": "FULL",
            "autoGenerateIds": True,
            "gcsSource":{
                "inputUris": [
                gcs_url
                ],
                "dataSchema": "custom"
            }
        }
        response = requests.post(
            f"https://discoveryengine.googleapis.com/v1beta/projects/{project_id}/locations/{location}/collections/default_collection/dataStores/{data_store_id}/branches/0/documents:import",
            headers=headers,
            json=data
        )
        return response
    
    def update_film_metadata_db(self, df):
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
                search_text = row["content"],
                # popularity = row["popularity"],
                # total_watchers = row["total_watchers"],
                popularity = "",
                total_watchers = 0
            ))

        session.commit()

