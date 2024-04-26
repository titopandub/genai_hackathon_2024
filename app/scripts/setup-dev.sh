#!/bin/bash

mkdir -p data

docker compose up -d db

gsutil cp gs://genai_hackathon_2024/data/faq/latest/faq.json data/
gsutil cp gs://genai_hackathon_2024/data/film_metadata/latest/film_metadata.json data/

alembic upgrade head