import unittest
from tests.base import BaseTest
import logging
import tests.bootstrap as _
from src.chain.chain_general import ask_general_question
from src.service.tracker import FlatChat
from src.db import Session

session = Session()

context = {
    "user_id": 54936340,
    "visit_id": "ffffff"
}

class TestGeneralPrompt(BaseTest):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        pass

    def test_prompt_end_to_end(self):
        user_id = 54936340

        response = ask_general_question(context, "1 + 1 = ")

        found = False
        if any(search_word in response.lower() for search_word in ["dua", "two", "2"]):
            found = True
        else:
            logging.error(f"=== response: {response}")

        self.assertTrue(found)
        history = session.query(FlatChat).order_by(FlatChat.id.desc()).first()
        self.assertEqual("other", history.route)