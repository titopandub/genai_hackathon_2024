from ddtrace import tracer
import requests
import os
import json
import logging

class Larva:
    @tracer.wrap(name="larva.get",resource="get_play_history")
    @staticmethod
    def get_play_history_film(user_id):
        api_key = os.environ.get("LARVA_APPLICATION_KEY", "")
        larva_url = os.environ.get("LARVA_URL", "")
        larva_response = requests.get(f"{larva_url}/vidio/user-play-start-history-films", params={'user_id': user_id}, headers={'key': api_key})

        user_history = []
        history_ids = []
        try:
            user_history = json.loads(larva_response.content)['records']
            history_ids = [play_history['film_id'] for play_history in user_history][:5]
        except Exception as e:
            logging.error(f"[Larva] Parse json error {user_id}: {str(e)}. json: {larva_response.content}")

        return history_ids