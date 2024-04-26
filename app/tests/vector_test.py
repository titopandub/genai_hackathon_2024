import unittest
from tests.base import BaseTest
import tests.bootstrap as _
from src.model.vector import FilmRepository, VertexSearchHttpAdapter, VidioInfoRepository
from src.service.embedding import embedding
import vertexai
import dotenv
from src.config import config

class TestVector(BaseTest):
    def setUp(self):
        super().setUp()
        dotenv.load_dotenv()
        vertexai.init(project=config['vertexai']['project'], location=config['vertexai']['location'])

    def tearDown(self):
        pass

    def test_vertex_search(self):
        if 'vertex_search' not in config['data_store']['film']:
            return
        # film_repository = FilmRepository(**config['data_store']['film']['vertex_search'])
        film_repository = FilmRepository(**config['data_store']['film']['vertex_search'])

        res = film_repository.search("action")
        res_lookup = film_repository.lookup_film(res)

        self.assertIn("action", res_lookup)

    def test_vidio_info_repository(self):
        vidio_info_repository = VidioInfoRepository(**config['data_store']['vidio_info']['vertex_search'])
        result = vidio_info_repository.search("berapa harga paket mahasiswa")

        self.assertIn("19", result)

    def test_vidio_info_repository_no_summary(self):
        vidio_info_repository = VidioInfoRepository(**config['data_store']['vidio_info']['vertex_search'])
        result = vidio_info_repository.search("ibukota indonesia")

        self.assertIn("jakarta", result.lower())
