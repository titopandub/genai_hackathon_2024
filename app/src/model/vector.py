from abc import abstractmethod
from annoy import AnnoyIndex
from src.service.embedding import Embedding, embedding
import pandas as pd
from google.cloud import aiplatform_v1
from google.cloud import discoveryengine_v1beta as discoveryengine_v1
from google.protobuf.json_format import MessageToDict
from ddtrace import tracer
import requests
import json
from src.config import config
from src.lib.google_token import google_token
import re
from google.cloud import storage
import markdownify
from src.model.film_metadata import FilmMetadata
from src.db import Session

class VertexSearchAdapter():
    def __init__(self, project_id, location, collection, data_store) -> None:
        self.serving_config = f"projects/{project_id}/locations/{location}/collections/{collection}/dataStores/{data_store}/servingConfigs/default_search:search"

    def search(self, query, limit=10):

        client = discoveryengine_v1.SearchServiceClient()

        # Initialize request argument(s)
        request = discoveryengine_v1.SearchRequest(
            serving_config=self.serving_config,
            query=query,
            page_size=10
        )

        page_result = client.search(request=request)

        result = list(map(lambda x: MessageToDict(x.document._pb)['structData'],page_result))
        result_ids = list(map(lambda x: int(x['id']),result))
        return result_ids

class VertexSearchHttpAdapter():
    def __init__(self, project_id, location, collection, data_store) -> None:
        self.url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_id}/locations/{location}/collections/{collection}/dataStores/{data_store}/servingConfigs/default_search:search"

    # example data = {"query": query, "pageSize": limit}
    def search(self, data):
        token = google_token.get_token()
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(self.url, json=data, headers=headers)
        response_json = json.loads(response.text)

        return response_json

class VidioInfoRepository():
    def __init__(self, project_id, location, collection, data_store) -> None:
        self.adapter = VertexSearchHttpAdapter(project_id=project_id,location=location,collection=collection,data_store=data_store)
        self.storage_client = storage.Client(config["project"])

    def get_file(self, gs_url):
        bucket_name = config["gcs_bucket_name"]
        file_path = re.search(f"{config['gcs_bucket']}\/(.+)",gs_url).group(1)

        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(file_path)

        return blob.download_as_text()

    def to_markdown(self, html):
        md = markdownify.markdownify(str(html), heading_style="ATX")
        return md

    def get_vertex_result(self, query, limit=10):
        data = {"query": query,"pageSize":limit,"queryExpansionSpec":{"condition":"AUTO"},"spellCorrectionSpec":{"mode":"AUTO"},"contentSearchSpec":{"summarySpec":{"summaryResultCount":5,"ignoreAdversarialQuery":True,"includeCitations":True},"snippetSpec":{"returnSnippet":True},"extractiveContentSpec":{"maxExtractiveAnswerCount":1}}}
        response_json = self.adapter.search(data)

        gs_urls = list(map(lambda x: x["document"]["derivedStructData"]["link"], response_json["results"]))
        summary_html = response_json['summary']['summaryText']
        try:
            summary_html = response_json['summary']['summaryWithMetadata']['summary']
        except:
            pass
        summary = self.to_markdown(summary_html)

        return (gs_urls, summary)

    @tracer.wrap(name="repository.search", resource="VidioInfoRepository.search")
    def search(self, query, limit=10):
        gs_urls, summary = self.get_vertex_result(query, limit)
        htmls = list(map(self.get_file, gs_urls))
        mds = list(map(self.to_markdown, htmls))
        information = summary + "\n"

        for md in mds:
            information = information + md

        return information

class FilmRepository:
    def __init__(self, project_id, location, collection, data_store) -> None:
        self.adapter = VertexSearchHttpAdapter(project_id=project_id,location=location,collection=collection,data_store=data_store)
    
    @tracer.wrap(name="repository.search", resource="FilmRepository.search")
    def search(self, query, limit=10):
        data = {"query": query, "pageSize": limit}
        response_json =  self.adapter.search(data)
        result = list(map(lambda x: x["document"]["structData"], response_json["results"]))
        ids = list(map(lambda x: int(x['id']), result))

        return ids
    
    def lookup_film(self, film_ids):
        session = Session()
        film_list = session.query(FilmMetadata).where(FilmMetadata.id.in_(tuple(film_ids))).all()
        data = list(map(lambda x: x.search_text, film_list))
        return "\n\n".join(data)

    def lookup_film_complete_text(self, film_ids):
        session = Session()
        film_list = session.query(FilmMetadata).where(FilmMetadata.id.in_(tuple(film_ids))).all()
        film_search_text = []

        for f in film_list:
            film_search_text.append(f"ID: {str(id)}\n{f.search_text}\nlink: {f.content_url}\nimage: {f.image_url}")
        return "\n\n".join(film_search_text)
    
    def get_image_link(self, id):
        session = Session()
        film = session.query(FilmMetadata).where(FilmMetadata.id == id).first()
        image = film.image_url
        link = film.content_url

        return image, link

    def get_grounding(self, response, history_film_ids):
        vector_search_result = ""

        if len(response) != 0:
            vector_film_ids = self.search(response)
            vector_search_result = self.lookup_film_complete_text(vector_film_ids)
        else:
            if len(history_film_ids) > 0:
                film_ids = []
                vector_search_result
                for film_id in history_film_ids:
                    film_search_query = self.lookup_film([film_id])
                    if film_search_query != "":
                        film_ids += self.search(film_search_query)
                vector_search_result = self.lookup_film_complete_text(set(film_ids))
        return vector_search_result

film_repository = FilmRepository( **config['data_store']['film']['vertex_search'])
vidio_info_repository = VidioInfoRepository(**config['data_store']['vidio_info']['vertex_search'])