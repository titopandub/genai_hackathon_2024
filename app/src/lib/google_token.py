import dotenv
dotenv.load_dotenv()
import google.auth
import google.auth.transport.requests
from google.auth import compute_engine
from google.oauth2 import service_account

import os

GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
class GoogleToken:
    def __init__(self) -> None:
        self.auth_req = google.auth.transport.requests.Request()

        if os.environ.get("ENVIRONMENT", "development") in ["production", "staging"]:
            self.creds = service_account.Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS, scopes=['https://www.googleapis.com/auth/cloud-platform'])
        else:
            try:
                self.creds, self.project = google.auth.default()
                self.creds.refresh(self.auth_req)
            except:
                self.creds = service_account.Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS, scopes=['https://www.googleapis.com/auth/cloud-platform'])

    def get_token(self):
        self.creds.refresh(self.auth_req)

        return self.creds.token

google_token = GoogleToken()