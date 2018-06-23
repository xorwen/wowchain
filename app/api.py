import random
import redis
import string
import requests
from flask import Flask, jsonify, request
import config
import urllib.parse

app = Flask(__name__)

r = redis.Redis(host='localhost', port=6379, db=0)

blocks = {
    'api_generic_message': '5b2e6e01e4b08d708b401776'
}

def get_random_string(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

5
def broadcast(block_name, attributes=None):
    payload = {
        'chatfuel_token': config.chatfuel_token,
        'chatfuel_block_id': blocks[block_name],
    }

    if attributes:
        payload.update(attributes)

    param_str = urllib.parse.urlencode(payload)
    print(payload)
    bot_id = config.chatfuel_bot_id
    user_id = '884740308318001'
    resp = requests.post(f'https://api.chatfuel.com/bots/{bot_id}/users/{user_id}/send?{param_str}')
    print(resp.json())


@app.route('/api/ping')
def chatbot_callback():
    a = int(request.args.get('a', 0))
    broadcast(block_name='api_generic_message', attributes={'api_message_body': 'this is a message body'})
    return jsonify({"pong": a})


@app.route('/api/gencode', methods=['GET'])
def chatfuel_gencode():
    print("Received message", request.args)

    user_name = request.args.get("first_name", 'noname')

    person_secret = get_random_string()
    r.set(f'person_secret_{person_secret}', user_name)

    response = {
         "messages": [
           {"text": "This is your secret code you need to send your partner:"},
           {"text": person_secret}
         ]
    }
    print("chatfuel_gencode response sent")
    return jsonify(response)
