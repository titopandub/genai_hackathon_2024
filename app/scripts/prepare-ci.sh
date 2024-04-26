#!/bin/bash
gsutil cp gs://genai_hackathon_2024/files/service-account.json.enc .
gsutil cp gs://genai_hackathon_2024/files/.env.ci.enc .
sops -d service-account.json.enc > service-account.json
sops -d .env.ci.enc > .env
docker pull asia.gcr.io/tools-build/genai-api-base:latest

./scripts/start-db.sh

mkdir -p data

export USER_ID=$(id -u)
export GROUP_ID=$(id -g)

docker build --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) -f Dockerfile . -t asia.gcr.io/tools-build/genai-api:latest

docker-compose -f docker-compose.ci.yml build
docker-compose -f docker-compose.ci.yml run --rm --service-ports api bash -c "alembic upgrade head"
