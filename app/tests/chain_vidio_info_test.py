from datetime import datetime
import unittest
from tests.base import BaseTest
from unittest.mock import patch
import tests.bootstrap as _
import time_machine
import dotenv
dotenv.load_dotenv()
from src.chain.chain_vidio_info import vidio_info_chain
from src.service.tracker import FlatChat
from src.db import Session
from src.model.vector import vidio_info_repository
import time

session = Session()

context = {
    "user_id": 54936340,
    "visit_id": "ffffff"
}

class TestVidioInfoPrompt(BaseTest):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        pass

    def test_prompt_end_to_end(self):
        response = vidio_info_chain(context, "bagaimana mendaftar paket mahasiswa")

        self.assertIn("kampus", response)
        self.assertIn("email", response)
        history = session.query(FlatChat).order_by(FlatChat.id.desc()).first()
        self.assertEqual("vidio-info", history.route)

    def test_prompt_with_history_context(self):
        response = vidio_info_chain(context, "bagaimana hubungan lasja dengan ayahnya")
        self.assertContainAny(
            ['harmonis', 'konflik', 'dekat', 'rahasia', 'wibowo', 'soeryo', 'renggang', 'curiga', 'jauh', 'mati'],
            response
        )

        response = vidio_info_chain(context, "siapa suaminya")
        self.assertIn("oka", response.lower())

        response = vidio_info_chain(context, "bagaimana mendaftar paket mahasiswa")
        self.assertIn("mahasiswa", response.lower())

    def test_prompt_games(self):
        response = vidio_info_chain(context, "game apa yang seru dimainkan saat menunggu antrian?")

        self.assertContainAny(
            ['arcade', 'antri', 'game', 'candy', 'tower', 'fruit', 'skor', 'seru', 'level', 'waktu', 'potong', 'combo'],
            response
        )