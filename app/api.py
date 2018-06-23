import random
import redis
import string
import requests
from flask import Flask, jsonify, request
import config
import urllib.parse
import json

app = Flask(__name__)

r = redis.Redis(host='localhost', port=6379, db=0)

blocks = {
    'api_generic_message': '5b2e6e01e4b08d708b401776'
}

def get_random_string(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))


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


@app.route('/api/generate_engaging_token', methods=['GET'])
def gencode():
    print("Received message", request.args)
    received = request.args.to_dict(flat=False)

    engaging_token = get_random_string()

    print("Store to redis", f'person_secret_{engaging_token}', received['chatfuel user id'])
    r.set(f'engaging_token_{engaging_token}', received['chatfuel user id'][0])

    response = {
         "messages": [
           {"text": "This is your secret code you need to send your partner:"},
           {"text": engaging_token}
         ]
    }
    print("chatfuel_gencode response sent")
    return jsonify(response)


@app.route('/api/validate_engaging_token', methods=['GET'])
def validate_engaging_token():
    print("Received message", request.args)
    received = request.args.to_dict(flat=False)
    engaging_token = received['engaging_token'][0]

    print("Getting from redis", engaging_token, "from user", received['chatfuel user id'])
    partner_id = r.get(f"engaging_token_{engaging_token}")
    print(f"Id of matched partner is {partner_id}")

    if partner_id:
        response = {
          "set_attributes":
            {
              "found_match": "true",
              "partner_id": str(partner_id[0])
            },
          "type": "json_plugin_url",
          "messages": "Success :)",
        }
    else:
        response = {
            "set_attributes":
                {
                    "found_match": "false"
                },
            "messages": "Not found.",
        }

    print(response)
    print(json.dumps(response))

    return jsonify(response)