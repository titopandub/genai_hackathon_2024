# Development
## setup pyenv
1. https://github.com/pyenv/pyenv-installer
2. `pyenv virtualenv genai_hackathon_2024` if you don't have `genai_hackathon_2024` virtualenv
3. `pyenv activate genai_hackathon_2024`
## setup envrioment variable and credential

1. `cp .env.example .env`

2. in .env file adjust `GOOGLE_APPLICATION_CREDENTIALS`

2. in .env file, change `LARVA_APPLICATION_ENV`, `QUIZ_JWT_SECRET` to secret from nakhoda (production)

2. in .env file, change `GUARDRAILS_TOKEN` to secret on [Guardrails Token](https://hub.guardrailsai.com/tokens)

3. install depedencies `pip install -r requirements.txt`

4. run `./scripts/setup_dev.sh`

## running test
all: `python -m unittest discover -s tests -p '*_test.py'` or `./scripts/test_all.sh`

one file: `python -m unittest tests/chain_router_test.py`


## running app
`python -m streamlit run src/basic_chat.py --server.port=8080 --server.address=0.0.0.0`

## running app (docker)

docker compose need to sync
~/.config/gcloud/ to docker volumes so the streamlit app can access Vertex ai, make sure the credentials is synced

Run this
`docker compose build`

`docker compose up`

visit `localhost`
in your browser

## access in browser
1. get quiz token from `https://www.vidio.com/interactions.json`, find "quiz": "eyJ........."
2. access `localhost:8080?token=eyJ.....` or `localhost?token=eyJ.....`

## API server (development)
1. Change directory to `streamlit-server`
2. Run with `PYTHONPATH=. python src/app.py`
3. cURL with `curl -X POST -d '{"user_id": 54936340, "visit_id": "random", "message": "Hi, how are you?"}' localhost:5000/chat-route`

## API server (production)
1. Change directory to `streamlit-server`
2. Run with `PYTHONPATH=. gunicorn -w 4 'src.app:app'`
3. cURL with `curl -X POST -d '{"user_id": 54936340, "visit_id": "random", "message": "Hi, how are you?"}' localhost:8000/chat-route`

## Connecting with Larva  
Run `kubectl port-forward service/larva-web-primary 6000:6000 -n larva --address=0.0.0.0` in nakhoda

## Connect to DB from local
Run `kubectl port-forward deployment/vidio-chatbot-proxy 5432:5432 -n vidio-chatbot --address=0.0.0.0` in nakhoda
