#!/bin/bash
docker pull asia.gcr.io/tools-build/genai-api-base:latest
docker build -f Dockerfile . -t asia.gcr.io/tools-build/genai-api:latest
docker push asia.gcr.io/tools-build/genai-api:latest