from http import HTTPStatus
import json
import os
import unittest
from tests.base import BaseTest
from unittest.mock import patch

import requests_mock
from src.app import app
from src.chain import chain_router
from tests.user_test import internal_token

class AppTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.headers = {'Content-Type': 'application/json'}
        self.app = app.test_client()

    @patch("src.chain.chain_router.run")
    def test_chat_route_success(self, run_fn):
        run_fn.return_value = "mock bot return value"
        
        endpoint = "/async-chat-route"
        request_data = {
            "user_id": 123,
            "visit_id": "random",
            "message": "Hi, how are you?",
            "channel": "dummy",
            "token": internal_token
        }
        # self.assertEqual(chain_router.run(request_data, "Hi, how are you?"), "mock bot return value")
        with requests_mock.Mocker() as mock:
            vidio_chat_host = os.environ.get("VIDIO_CHAT_HOST","http://live.vidio.test:8080")
            mock.post(f'{vidio_chat_host}/v1/channels/publish')
            resp = self.app.post(endpoint, headers=self.headers, data=json.dumps(request_data))

            self.assertEqual(resp.status_code, HTTPStatus.OK.value)
