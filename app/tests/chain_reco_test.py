import unittest
from tests.base import BaseTest
from unittest.mock import patch, MagicMock
import tests.bootstrap as _
import dotenv
from src.service.larva import Larva
from src.service.tracker import FlatChat
from src.db import Session

session = Session()

dotenv.load_dotenv()
from src.chain.chain_reco import ask_recommendation, parse_final_response, Recommendation

context = {
    "user_id": 54936340,
    "visit_id": "ffffff",
    "user_gender": "",
    "user_age": -1
}

class TestPrompt(BaseTest):
    @patch.object(Larva, "get_play_history_film")
    def test_prompt_end_to_end(self, get_play_history_film ):
        get_play_history_film.return_value = [8222, 7640, 9150, 3917]

        response = ask_recommendation(context, "gw lagi pengen nonton film science fiction, apa ya yang cocok?")

        self.assertContainAny(
            ['sci-fi', 'fiksi', 'sains', 'science', 'petualang', 'fiction', 'scifi','angkasa', 'space', 'teknologi'],
            response
        )
        self.assertIn("kenapa kamu suka", response.lower())
        self.assertIn("judul", response.lower())
        self.assertIn("https://thumbor", response)

        history = session.query(FlatChat).order_by(FlatChat.id.desc()).first()
        self.assertEqual("recommendation", history.route)

    def test_film_metadata_not_exist_in_alloy(self):
        final_response = [
            Recommendation(id=-1, title="Not exist", explanation="Not exist").__dict__,
            Recommendation(id=824, title="Ganteng Ganteng Serigala", explanation="GGS").__dict__
        ]
        response = parse_final_response({"items": final_response})
        self.assertIn("ganteng", response.lower())
