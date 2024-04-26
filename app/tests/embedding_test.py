import unittest
from tests.base import BaseTest
import tests.bootstrap as _
import dotenv
dotenv.load_dotenv()
from src.service.embedding import embedding, google_model, GoogleEmbedding

class TestEmbedding(BaseTest):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        pass

    def test_google_model(self):
        response = GoogleEmbedding(google_model).embedding_text("bagaimana mendaftar paket mahasiswa")

        self.assertEqual(len(response), 768)
        self.assertTrue(response[0] > 0.029 and response[0] < 0.030)