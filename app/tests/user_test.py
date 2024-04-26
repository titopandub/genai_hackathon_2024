import unittest
from tests.base import BaseTest
import tests.bootstrap as _
from src.lib.user import User
from unittest.mock import MagicMock, Mock
import streamlit as st
from streamlit.runtime.state.query_params_proxy import QueryParamsProxy
import os


non_internal_token = "eyJhbGciOiJIUzUxMiJ9.eyJpZCI6MSwibmFtZSI6IlVzZXIgMSIsImF2YXRhciI6Imh0dHBzOi8vdGh1bWJvci5wcm9kLnZpZGlvY2RuLmNvbS9TN1dJbmtfaExYcjNaY0EycmhlRE9pSzNZdTg9LzMyeDMyL2ZpbHRlcnM6cXVhbGl0eSg3MCkvdmlkaW8td2ViLXByb2QtdXNlci91cGxvYWRzL3VzZXIvYXZhdGFyLzgyOTc2ODM4L2I4MmMzNWY1LWE3Y2QtNDZjOC1hZmYxLTUyYjhkN2E2N2NkYzQwMHg0MDAtMTI2NTM5ZDRjZTcyYjRlZi5wbmciLCJ2ZXJpZmllZF9waG9uZSI6IjYyODk3ODg4MjkzIiwiaGFzX2RhbmEiOnRydWUsImlzX3ByZW1pZXIiOnRydWUsImlzX2ludGVybmFsIjpmYWxzZSwicGFja2FnZV9pZHMiOiIyMiIsImV4cCI6MTcwOTI4MjAzNSwiZ2VuZGVyIjoibWFsZSIsImFnZSI6MjV9.lMMoIBPijX1pvJHIYTfXbUeuPnhZ1omwcJLBFCAVk0IBrp1flEGcdj5sVkooxe5qOqwdQLQTnn7dK40kYcM7KA" 
internal_token = "eyJhbGciOiJIUzUxMiJ9.eyJpZCI6MSwibmFtZSI6IlVzZXIgMSIsImF2YXRhciI6Imh0dHBzOi8vdGh1bWJvci5wcm9kLnZpZGlvY2RuLmNvbS9TN1dJbmtfaExYcjNaY0EycmhlRE9pSzNZdTg9LzMyeDMyL2ZpbHRlcnM6cXVhbGl0eSg3MCkvdmlkaW8td2ViLXByb2QtdXNlci91cGxvYWRzL3VzZXIvYXZhdGFyLzgyOTc2ODM4L2I4MmMzNWY1LWE3Y2QtNDZjOC1hZmYxLTUyYjhkN2E2N2NkYzQwMHg0MDAtMTI2NTM5ZDRjZTcyYjRlZi5wbmciLCJ2ZXJpZmllZF9waG9uZSI6IjYyODk3ODg4MjkzIiwiaGFzX2RhbmEiOnRydWUsImlzX3ByZW1pZXIiOnRydWUsImlzX2ludGVybmFsIjp0cnVlLCJwYWNrYWdlX2lkcyI6IjIyIiwiZXhwIjoxNzA5MjgyMDM1fQ.U8rLonUIS1GGwINfLZmfTzG9N4V0qg9qZSxe3jzWzWZJ-jHjhBPNVhUvLrcmPWfhVQgHkhp117pl7jcNw-1xUA"
internal_token_staging = "eyJhbGciOiJIUzUxMiJ9.eyJpZCI6MSwibmFtZSI6IlVzZXIgMSIsImF2YXRhciI6Imh0dHBzOi8vdGh1bWJvci5wcm9kLnZpZGlvY2RuLmNvbS9TN1dJbmtfaExYcjNaY0EycmhlRE9pSzNZdTg9LzMyeDMyL2ZpbHRlcnM6cXVhbGl0eSg3MCkvdmlkaW8td2ViLXByb2QtdXNlci91cGxvYWRzL3VzZXIvYXZhdGFyLzgyOTc2ODM4L2I4MmMzNWY1LWE3Y2QtNDZjOC1hZmYxLTUyYjhkN2E2N2NkYzQwMHg0MDAtMTI2NTM5ZDRjZTcyYjRlZi5wbmciLCJ2ZXJpZmllZF9waG9uZSI6IjYyODk3ODg4MjkzIiwiaGFzX2RhbmEiOnRydWUsImlzX3ByZW1pZXIiOnRydWUsImlzX2ludGVybmFsIjp0cnVlLCJwYWNrYWdlX2lkcyI6IjIyIiwiZXhwIjoxNzA5MjgyMDM1LCJnZW5kZXIiOiJtYWxlIiwiYWdlIjoyNX0.KGb5Zt6hsRI39RxZF3xur8jQLjnnzuBpzCMn2tdVVsLNHYjyebXcO3_dxsIkx0SbaoCRaVHiOtjurNraCR5KKA"


class Dummy:
    def get(self, key):
        pass


class TestUser(BaseTest):
    def setUp(self):
        super().setUp()
        os.environ["QUIZ_JWT_SECRET"] = "salam_gembira"
        os.environ["QUIZ_JWT_SECRET_STAGING"] = "salam_gembira_2"
        self.mock = Dummy()

    def tearDown(self):
        pass

    def test_get_user_from_token(self):
        self.mock.get = MagicMock(return_value=internal_token)
        st.query_params = self.mock

        self.assertEqual(User().id(), 1)
        self.assertEqual(User().is_login(), True)

    def test_get_user_from_token_staging(self):
        self.mock.get = MagicMock(return_value=internal_token_staging)
        st.query_params = self.mock

        self.assertEqual(User().id(), 1)
        self.assertEqual(User().is_login(), True)

    def test_get_user_from_token_invalid_return_none(self):
        self.mock.get = MagicMock(return_value="")
        st.query_params = self.mock

        self.assertEqual(User().id(), None)
        self.assertEqual(User().is_login(), False)

    def test_only_internal(self):
        self.mock.get = MagicMock(return_value=non_internal_token)
        st.query_params = self.mock

        os.environ["ONLY_INTERNAL"] = "false"
        self.assertEqual(User().is_login(), True)

        os.environ["ONLY_INTERNAL"] = "true"
        self.assertEqual(User().is_login(), False)

        self.mock.get = MagicMock(return_value=internal_token)
        st.query_params = self.mock

        os.environ["ONLY_INTERNAL"] = "false"
        self.assertEqual(User().is_login(), True)

        os.environ["ONLY_INTERNAL"] = "true"
        self.assertEqual(User().is_login(), True)

    def test_gender(self):
        self.mock.get = MagicMock(return_value=non_internal_token)
        st.query_params = self.mock
        self.assertEqual(User().gender(), "male")

    def test_gender_no_property(self):
        self.mock.get = MagicMock(return_value=internal_token)
        st.query_params = self.mock
        self.assertEqual(User().gender(), "")

    def test_age(self):
        self.mock.get = MagicMock(return_value=non_internal_token)
        st.query_params = self.mock
        self.assertEqual(User().age(), 25)

    def test_age_no_property(self):
        self.mock.get = MagicMock(return_value=internal_token)
        st.query_params = self.mock
        self.assertEqual(User().age(), -1)