
import requests
import json
from datetime import datetime
import os
import jwt.utils
import json
import logging
import src.bootstrap

vidio_chat_host = os.environ.get("VIDIO_CHAT_HOST","http://live.vidio.test:8080")

chatbot_profile = {
    'id': 0,
    'avatar_url_big': 'https://thumbor.prod.vidiocdn.com/8HbPvfUKRPffQd7UgpKfjBx-RZw=/filters:quality(90)/vidio-media-production/uploads/image/source/8340/b8795e.png',
    'avatar_url_small': 'https://thumbor.prod.vidiocdn.com/8HbPvfUKRPffQd7UgpKfjBx-RZw=/filters:quality(90)/vidio-media-production/uploads/image/source/8340/b8795e.png',
    'initial': 'V',
    'links': {'self': None},
    'name': 'Vidio Chatbot',
    'role': 'admin',
    'username': 'vidio-chatbot',
}

class VidioChat:
    @staticmethod
    def decode_token(token):
        return json.loads(jwt.utils.b64decode(token.split(".")[1]).decode('utf-8'))

    @staticmethod
    def get_user_profile(decoded):
        try:
            return {
                'id': decoded['id'],
                'avatar_url_big': decoded['avatar_url_big'],
                'avatar_url_small': decoded['avatar_url_small'],
                'initial': decoded['initial'],
                'links': {'self': None},
                'name': decoded['name'],
                'role': decoded['role'],
                'username': decoded['username'],
            }
        except KeyError:
            return {
                'id': -1,
                'avatar_url_big': 'https://static-web.prod.vidiocdn.com/assets/default/user_original-b548dab4ae77346e1a0c25b8329f6ade96844fe0decc84b5a6581fe9246749fd.png',
                'avatar_url_small': 'https://static-web.prod.vidiocdn.com/assets/default/user_original-b548dab4ae77346e1a0c25b8329f6ade96844fe0decc84b5a6581fe9246749fd.png',
                'initial': 'K',
                'links': {'self': None},
                'name': 'Kamu',
                'role': 'external_ugc',
                'username': 'kamu',
            }

    @staticmethod
    def send_bot_chat(request_id, token, channel, message):
        logging.warn("masuk send bot chat ")
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8'
        }

        content = {
            'id': request_id,
            'content': message,
            'user': chatbot_profile,
            'type': 'chat/message',
            'created_at': str(datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))
        }

        payload = {
            'data': json.dumps({
                'channelParam': [{
                    'channelName': channel,
                    'data': json.dumps(content),
                    'type': 'chat/message'
                }]
            })
        }

        chat_resp = requests.post(f'{vidio_chat_host}/v1/chatbot/publish', headers=headers, data=payload)
        logging.warn(f"resp: {chat_resp.status_code} {chat_resp}")
        logging.warn(f"resp text: {chat_resp.text}")

    @staticmethod
    def send_user_chat(request_id, token, channel, message):
        logging.warn("masuk send chat user ")
        decoded = VidioChat.decode_token(token)
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8'
        }

        content = {
            'content': message,
            'user': VidioChat.get_user_profile(decoded),
            'type': 'chat/message',
            'created_at': str(datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))
        }

        loading_content = {
            'id': request_id,
            'content': '<div class="livestreaming-discussion__loading"><div></div></div>',
            'user': chatbot_profile,
            'type': 'chat/message',
            'created_at': str(datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))
        }

        payload = {
            'data': json.dumps({
                'channelParam': [
                    {
                        'channelName': channel,
                        'data': json.dumps(content),
                        'type': 'chat/message'
                    },
                    {
                        'channelName': channel,
                        'data': json.dumps(loading_content),
                        'type': 'chat/message'
                    }
                ]
            })
        }

        chat_resp = requests.post(f'{vidio_chat_host}/v1/chatbot/publish', headers=headers, data=payload)
        logging.warn(f"resp: {chat_resp.status_code} {chat_resp}")
        logging.warn(f"resp text: {chat_resp.text}")