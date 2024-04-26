import streamlit as st
from jwt import JWT, jwk_from_dict
from jwt.utils import b64encode
import os


class User:
    def __init__(self):
        secret = os.environ.get("QUIZ_JWT_SECRET", "")
        secret_staging = os.environ.get("QUIZ_JWT_SECRET_STAGING", "")
        self.is_internal_only = os.environ.get("ONLY_INTERNAL", "true") == "true"
        jwt = JWT()
        key = jwk_from_dict({
            'kty': 'oct',
            'alg': 'HS512',
            'k': b64encode(secret.encode("utf-8")),
        })
        staging_key = jwk_from_dict({
            'kty': 'oct',
            'alg': 'HS512',
            'k': b64encode(secret_staging.encode("utf-8")),
        })
        token = self.get_token_from_query_params()

        try:
            self.data = jwt.decode(token, key, do_time_check=False)
        except:
            self.data = None
        
        if self.data:
            return
        
        try:
            self.data = jwt.decode(token, staging_key, do_time_check=False)
        except:
            self.data = None

    def get_token_from_query_params(self):
        token = None
        if st.query_params.get("token"):
            token = st.query_params.get("token")
        
        return token

    def is_login(self):
        if self.is_internal_only and not self.is_internal():
            return False

        return True if self.data else False
    
    def id(self):
        return self.data['id'] if self.data else None

    def is_internal(self):
        return self.data['is_internal'] if self.data else None
    
    def gender(self):
        return self.data.get('gender', "") if self.data else ""
    
    def age(self):
        return self.data.get('age', -1) if self.data else -1
