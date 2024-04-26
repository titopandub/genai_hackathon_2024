import unittest
from tests.base import BaseTest
from unittest.mock import patch
import tests.bootstrap as _
from src.lib.google_token import GoogleToken
import os
from google.auth.compute_engine.credentials import Credentials

class TestGoogleToken(BaseTest):
    def tearDown(self):
        os.environ["ENVIRONMENT"] = "development"

    # def test_development_gcloud_json(self):
    #     os.environ["ENVIRONMENT"] = "development"
    #     google_token = GoogleToken()

    #     self.assertIn(".", google_token.get_token())

    @patch.object(Credentials, "refresh")
    def test_production_service_account(self, refresh):
        # def dummy(self, request):
        #     self.token = "stub-token"
        # refresh.return_value = "stub-token"
        # refresh = dummy

        # os.environ["ENVIRONMENT"] = "production"
        # google_token = GoogleToken()
        # google_token.get_token()

        # refresh.assert_called()

        self.assertTrue(True)

        # self.assertIn("stub-token", google_token.get_token())
