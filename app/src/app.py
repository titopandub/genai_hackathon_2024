from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from src.celery import celery
from src.service.vidio_chat import VidioChat

import src.bootstrap

app = Flask(__name__)
CORS(app)

@app.route('/async-chat-route', methods=['POST'])
def async_chat_route():
    data = request.json
    token = data.get('token', "")
    channel = data.get('channel', "")
    message = data.get("message", "")
    user_data = VidioChat.decode_token(token)

    user_id = user_data.get("id", -1)
    visit_id = str(user_id)
    user_age = user_data.get("age", -1)
    user_gender = user_data.get("gender", "")

    context = {
        "user_id": user_id,
        "user_age": user_age,
        "user_gender": user_gender,
        "visit_id": visit_id,
        "token": token,
        "channel": channel
    }
    # chat = process_chat.delay(context, message)
    chat = celery.send_task('process_chat', args=[context, message])


    return make_response(jsonify({"id": chat.id}), 200)

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return 'ok'

if __name__ == '__main__':
    app.run()