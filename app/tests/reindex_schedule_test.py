import os
import unittest
from tests.base import BaseTest
from unittest.mock import patch
import tests.bootstrap as _
import requests_mock
from src.lib.google_token import GoogleToken
from src.etl.reindex_schedule import ReindexSchedule
from src.config import config

class ReindexScheduleTest(BaseTest):
    def setUp(self) -> None:
        super().setUp()
        self.file_path = "data/schedule.txt"

    def tearDown(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    @patch.object(ReindexSchedule, 'upload_blob')
    @patch.object(GoogleToken, '__init__')
    @patch.object(GoogleToken, 'get_token')
    @patch.object(ReindexSchedule, 'reindex_from_gcs')
    def test_run(self, 
                 reindex_from_gcs_func,
                 get_token_func,
                 token_init_func,
                 upload_blob_func):
        token_init_func.return_value = None
        get_token_func.return_value = 'abcdef'
        vidio_schedule_url = "https://api.vidio.com/sport_events"
        mock_response = self.mock_response()
        with requests_mock.Mocker() as mock:
            mock.get(vidio_schedule_url, json=mock_response) # Mock the GET request
            
            result = ReindexSchedule().run()
            assert mock.called
            self.assertEqual(mock.call_count, 1)
            self.assertEqual(result, 'Serie A - Bologna FC vs U.S. Salernitana 1919 - 01 April 2024 17:30')
            self.assertTrue(os.path.exists(self.file_path))
            with open(self.file_path, 'r') as file:
                content = file.read()
                self.assertEqual(content, 'Serie A - Bologna FC vs U.S. Salernitana 1919 - 01 April 2024 17:30', "File content does not match.")
            upload_blob_func.assert_called_with("genai_hackathon_2024", self.file_path, self.file_path)
            reindex_from_gcs_func.assert_called_with('abcdef', config["project"], 'global', 'vidio-info-v3_1711610635224', f"{config['gcs_bucket']}/data/schedule.txt")

    def mock_response(self):
        return {
            "data": [
                {
                    "id": "8699",
                    "type": "sport_event",
                    "attributes": {
                        "start_time": "2024-04-01T17:30:00+07:00",
                        "end_time": "2024-04-01T19:30:00+07:00",
                        "home_team_score": None,
                        "away_team_score": None,
                        "home_team_score_detail": {
                            "et": None,
                            "ft": None,
                            "ht": None,
                            "pen": None
                        },
                        "away_team_score_detail": {
                            "et": None,
                            "ft": None,
                            "ht": None,
                            "pen": None
                        },
                        "winner": None,
                        "with_penalty": None
                    },
                    "relationships": {
                        "home_team": {
                            "data": {
                                "id": "13992195",
                                "type": "sport_team"
                            }
                        },
                        "away_team": {
                            "data": {
                                "id": "13992196",
                                "type": "sport_team"
                            }
                        },
                        "sport_event_content": {
                            "data": {
                                "id": "9235",
                                "type": "sport_event_content"
                            }
                        }
                    }
                },
            ],
            "included": [
                {
                    "id": "13992195",
                    "type": "sport_team",
                    "attributes": {
                        "name": "Bologna FC",
                        "image": "https://thumbor.prod.vidiocdn.com/AAr3FHlVFRg1kAC__LRf9SpJUvU=/168x168/filters:quality(70)/vidio-web-prod-topic/uploads/topic/image/29016/3a2220.png",
                        "links": {
                            "self_web": "https://www.vidio.com/tags/bologna-fc-1909"
                        }
                    }
                },
                {
                    "id": "13992196",
                    "type": "sport_team",
                    "attributes": {
                        "name": "U.S. Salernitana 1919",
                        "image": "https://thumbor.prod.vidiocdn.com/yowwVsoHspefPzCpkbLbjrHNUkY=/168x168/filters:quality(70)/vidio-web-prod-topic/uploads/topic/image/29017/356271.png",
                        "links": {
                            "self_web": "https://www.vidio.com/tags/us-salernitana-1919"
                        }
                    }
                },
                {
                    "id": "9235",
                    "type": "sport_event_content",
                    "attributes": {
                        "image": "https://thumbor.prod.vidiocdn.com/s__KELoqi5D1jTxGhQdPWBuwlI0=/filters:quality(70)/vidio-media-production/uploads/livestreaming/schedule/thumbnail/3353027/94cba9.jpg"
                    },
                    "link": {
                        "self_web": "https://www.vidio.com/live/6299?schedule_id=3353027"
                    },
                    "links": {
                        "self_web": "https://www.vidio.com/live/6299?schedule_id=3353027"
                    }
                },
            ],
            "meta": {
                "grouping": [
                    {
                        "name": "Serie A",
                        "sport_event_ids": [
                            "8699",
                        ],
                        "links": {
                            "self_web": "https://www.vidio.com/schedule/sports/football/13992103-italy-serie-a"
                        }
                    },
                ]
            }
        }
