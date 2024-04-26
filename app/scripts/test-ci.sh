mkdir -p data

gsutil cp gs://genai_hackathon_2024/data/faq/latest/faq.json data/
gsutil cp gs://genai_hackathon_2024/data/film_metadata/latest/film_metadata.json data/

docker-compose -f docker-compose.ci.yml run --rm --service-ports api bash -c "python -m unittest discover -s tests -p '*_test.py'"