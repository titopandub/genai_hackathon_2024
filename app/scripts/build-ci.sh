#!/bin/bash
sops -d service-account.json.enc > service-account.json
sops -d .env.ci.enc > .env

docker pull asia.gcr.io/tools-build/genai-api-base:latest

mkdir -p data

docker build -f Dockerfile . -t asia.gcr.io/tools-build/genai-api:latest