#!/bin/bash
sops -d service-account.json.enc > service-account.json
sops -d .env.ci.enc > .env

mkdir -p data

export USER_ID=$(id -u)
export GROUP_ID=$(id -g)

docker build --build-arg GUARDRAILS_TOKEN=$(grep GUARDRAILS_TOKEN .env | cut -d '=' -f2) -f Dockerfile.base . -t asia.gcr.io/tools-build/genai-api-base:latest
docker push asia.gcr.io/tools-build/genai-api-base:latest