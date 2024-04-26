from datetime import datetime
import logging
import os

import requests
from google.cloud import storage
from src.lib.google_token import GoogleToken
from src.config import config


class ReindexSchedule:
    def run(self):
        result = self.get_vidio_schedule()
        self.write_to_schedule_text(result)
        self.upload_blob("genai_hackathon_2024", "data/schedule.txt", "data/schedule.txt")
        self.reindex_schedule()
        return result

    def get_vidio_schedule(self):
        api_auth = os.environ.get("VIDIO_X_API_AUTH", "")
        params = {
            'content_size': 100,
            'filter[state]': 'upcoming'
        }
        headers = {
            'X-API-AUTH': api_auth,
            'accept': 'application/json'
        }
        vidio_host = os.environ.get("VIDIO_HOST", "https://api.vidio.com")
        response = requests.get(f"{vidio_host}/sport_events", params=params, headers=headers)
        result = self.join_jsonapi_data(response.json())
        parsed_result = [self.parse_result(i) for i in result]
        joined_result = "\n".join(parsed_result)
        return joined_result

    def join_included_data(self, data, included):
        included_map = {(item['type'], item['id']): item for item in included}
        
        for item in data:
            for relation_key, relation_value in item.get('relationships', {}).items():
                relation_data = relation_value.get('data')
                if relation_data:
                    key = (relation_data['type'], relation_data['id'])
                    if key in included_map:
                        item[relation_key] = included_map[key]['attributes']
        
        return data

    def join_jsonapi_data(self, jsonapi_data):
        # Helper function to find item by ID in 'included'
        def find_included_by_id(included, id):
            return next((item for item in included if item['id'] == id), None)

        # Joining logic
        for event in jsonapi_data['data']:
            # Append related 'included' items' attributes to the 'data' item
            for relationship_key, relationship_value in event['relationships'].items():
                related_item = find_included_by_id(jsonapi_data['included'], relationship_value['data']['id'])
                if related_item:
                    event[relationship_key] = related_item

            # Append 'meta' information where applicable
            for grouping in jsonapi_data['meta']['grouping']:
                if event['id'] in grouping['sport_event_ids']:
                    event['grouping'] = grouping

        return jsonapi_data['data']

    def parse_result(self, result):
        date_format = '%Y-%m-%dT%H:%M:%S%z'
        output_date_format = '%d %B %Y %H:%M'
        return (
            f"{result['grouping']['name']}"
            " - "
            f"{result['home_team']['attributes']['name']}"
            " vs "
            f"{result['away_team']['attributes']['name']}"
            " - "
            f"{datetime.strptime(result['attributes']['start_time'], date_format).strftime(output_date_format)}"
        )

    def write_to_schedule_text(self, joined_result):
        with open('data/schedule.txt', 'w') as file:
            file.write(joined_result)

    def upload_blob(self, bucket_name, source_file_name, destination_blob_name):
        storage.blob._DEFAULT_CHUNKSIZE = 35 * 1024 * 1024  # 35 MB
        storage.blob._MAX_MULTIPART_SIZE = 35 * 1024 * 1024  # 35 MB

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)

    def reindex_schedule(self):
        token = GoogleToken().get_token()
        project_id = config["project"]
        location = "global"
        data_store_id = config['data_store']['reindex_schedule_datastore']
        self.reindex_from_gcs(token, project_id, location, data_store_id, f"{config['gcs_bucket']}/data/schedule.txt")
        logging.info("success reindex from Vidio Schedule")

    def reindex_from_gcs(self, token, project_id, location, data_store_id, gcs_url):
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data={
            "reconciliationMode": "INCREMENTAL",
            "gcsSource":{
                "inputUris": [
                    gcs_url
                ],
                "dataSchema": "content"
            }
        }
        response = requests.post(
            f"https://discoveryengine.googleapis.com/v1beta/projects/{project_id}/locations/{location}/collections/default_collection/dataStores/{data_store_id}/branches/0/documents:import",
            headers=headers,
            json=data
        )
        return response
