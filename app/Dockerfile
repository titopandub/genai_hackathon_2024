# app/Dockerfile

FROM asia.gcr.io/tools-build/genai-api-base:latest

COPY requirements.txt .

RUN pip3 install -r requirements.txt

ARG GROUP_ID=1000
ARG USER_ID=1000

WORKDIR /app

RUN groupadd -r quiz --gid=$GROUP_ID && \
    useradd --create-home -r quiz -g quiz --uid=$USER_ID && \
    chown quiz:quiz -R /app

RUN mv /root/nltk_data /home/quiz/nltk_data && chown -R quiz:quiz /home/quiz/nltk_data
COPY src src
COPY migrations migrations
COPY alembic.ini alembic.ini

RUN chown quiz:quiz -R /app

ENV PYTHONPATH=.

USER quiz

CMD ["ddtrace-run", "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.app:app"]