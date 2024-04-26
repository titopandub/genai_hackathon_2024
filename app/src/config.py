import os

config = {
    'slow_timeout': 5,
    'project': 'vidio-quiz-prod',
    'gcs_bucket': 'gs://genai_hackathon_2024',
    'gcs_bucket_name': 'genai_hackathon_2024',
    'vertexai': {
        'project': 'vidio-quiz-prod',
        'location': 'asia-southeast1',
    },
    'aiplatform': {
        'project': 'vidio-quiz-prod',
        'location': 'asia-southeast1',
        'staging_bucket': 'gs://genai_hackathon_2024'
    },
    'embedding': {
        'pretrain_model_id': '7738653107357220864'
    }
}

# STAGING
if os.environ.get("ENVIRONMENT", "") == "staging":
    config['data_store'] = {
        'film': {
            'vertex_search': {
                'project_id': 328583281153,
                'location':  'global',
                'collection': 'default_collection',
                'data_store': 'staging-film_1712204816047'
            }
        },
        'vidio_info': {
            'vertex_search': {
                'project_id': 328583281153,
                'location':  'global',
                'collection': 'default_collection',
                'data_store': 'staging-vidio-info_1712204607239'
            }
        },
        'reindex_schedule_datastore': 'staging-vidio-info_1712204607239',
        'reindex_film_datastore': 'staging-film_1712204816047',
    }

# PRODUCTION
else:
    config['data_store'] = {
        'film': {
            'vertex_search': {
                'project_id': 328583281153,
                'location':  'global',
                'collection': 'default_collection',
                'data_store': 'film-metadata-2024-03-19_1710826473633'
            }
        },
        'vidio_info': {
            'vertex_search': {
                'project_id': 328583281153,
                'location':  'global',
                'collection': 'default_collection',
                'data_store': 'vidio-info-v3_1711610635224'
            }
        },
        'reindex_schedule_datastore': 'vidio-info-v3_1711610635224',
        'reindex_film_datastore': 'film-metadata-202403191330_1710829784824',
    }