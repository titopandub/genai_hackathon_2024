
import unittest
from tests.base import BaseTest
import logging
import tests.bootstrap as _
from unittest.mock import patch, MagicMock
from src.service.larva import Larva
from src.chain.chain_router import run, guard
from guardrails.errors import ValidationError

context = {
    "user_id": 54936340,
    "visit_id": "ffffff",
    "user_gender": "",
    "user_age": -1
}

class TestPrompt(BaseTest):
    def setUp(self):
        super().setUp()
        Larva.get_play_history_film = MagicMock(return_value=[8222, 7640, 9150, 3917])

    def tearDown(self):
        pass

    def test_prompt_end_to_end_vidio_info_chain(self):
        response = run(context, "bagaimana mendaftar paket mahasiswa")
        # print(response)

        self.assertIn("kampus", response)

    def test_prompt_end_to_end_reco_chain(self):
        response = run(context, "gw lagi pengen nonton film science fiction, apa ya yang cocok?")
        # print(response)

        self.assertIn("Kenapa kamu suka", response)

    # def test_prompt_end_to_end_vidio_info_chain_general(self):
    #     response = run(context, "1 + 1 = ")
    #     # print(response)

    #     found = False
    #     if any(search_word in response.lower() for search_word in ["dua", "two", "2"]):
    #         found = True
    #     else:
    #         logging.error(f"=== response: {response}")

    #     self.assertTrue(found, response)

    def test_prompt_mention_competitor(self):
        with self.assertRaises(ValidationError):
            guard.validate(llm_output="Film squid game tersedia di Netflix. Kompetitor vidio adalah Mola TV, WeTV dan Disney+ Hotstar")

        response = run(context, "OTT apa yang merupakan saingan Vidio.com?")

        self.assertContainAny([
                "Maaf, kami terbatas dalam memberikan informasi spesifik tentang produk atau layanan Vidio.com. Untuk detail lebih lanjut, silakan merujuk langsung ke sumber resmi mereka.".lower(),
                "competitors", "sorry", "cannot", "ott", "answer"
            ],
            response
        )
        self.assertNotContainAny(
            ["Vision+", "Mola TV", "WeTV", "iQiyi", "Netflix", "Disney+ Hotstar", "Amazon Prime Video", "MAXStream", "Hulu", "HBO GO", "Apple TV+"],
            response
        )