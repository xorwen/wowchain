import random
import redis
import string
import requests
from flask import Flask, jsonify, request
import config
import urllib.parse
import json
import subprocess

app = Flask(__name__)

r = redis.Redis(host='localhost', port=6379, db=0)

blocks = {
    'api_generic_message': '5b2e6e01e4b08d708b401776'
}

def store_to_blockchain():
    contract_id = 'xxx'
    out = f'./assets/{contract_id}-'
    command = [
        "python3", "run_blockchain.py",
        "./files/MarriageContract.sol", "./files/power_of.png", f"{out}power_of_OUT.png",
        "./files/Merriweather-Bold.ttf",
        "aa", "bb",
        "./files/cert.png", f"{out}cert_OUT.png", f"{out}out.png"
    ]
    subprocess.Popen(command)

def get_random_string(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))


def broadcast(user_id, block_name, attributes=None):
    payload = {
        'chatfuel_token': config.chatfuel_token,
        'chatfuel_block_id': blocks[block_name],
    }

    if attributes:
        payload.update(attributes)

    param_str = urllib.parse.urlencode(payload)
    print(payload)
    bot_id = config.chatfuel_bot_id
    resp = requests.post(f'https://api.chatfuel.com/bots/{bot_id}/users/{user_id}/send?{param_str}')
    print(resp.json())

def async_broadcast(user_id, message):
    subprocess.Popen(["python3", "broadcast.py", user_id, message])


@app.route('/api/test_broadcast')
def chatbot_callback():
    user_id = request.args.get('user_id','')
    print(f"Broadcasting test mesage to {user_id}")
    async_broadcast(user_id, "test broadcast message")
    return jsonify({"ok": 1})

@app.route('/api/test_marrige')
def test_marrige():
    store_to_blockchain()
    return jsonify({"ok": 1})

@app.route('/api/generate_engaging_token', methods=['GET'])
def gencode():
    print("Received message", request.args)
    received = request.args.to_dict(flat=False)

    engaging_token = get_random_string()
    user_id = received['chatfuel user id'][0]

    print("Store to redis", f'person_secret_{engaging_token}', received['chatfuel user id'])
    r.set(f'engaging_token_{engaging_token}', user_id)
    r.set(f'username_{user_id}', f"{received['first name'][0]} {received['last name'][0]}")

    response = {
        "set_attributes":
            {
                "engaging_token": engaging_token
            }
    }

    print("engaging_token response sent")
    return jsonify(response)

def get_my_partner_name(my_id):
    partner_id = r.get(f"partner_{my_id}")
    partner_name = r.get(f"username_{partner_id}")
    return partner_name



@app.route('/api/validate_engaging_token', methods=['GET'])
def validate_engaging_token():
    print("Received message", request.args)
    received = request.args.to_dict(flat=False)
    engaging_token = received['engaging_token'][0]
    user_id = received['chatfuel user id'][0]
    user_name = f"{received['first name'][0]} {received['last name'][0]}"

    r.set(f'username_{user_id}', user_name)

    print("Getting from redis", engaging_token, "from user", received['chatfuel user id'])
    partner_id = r.get(f"engaging_token_{engaging_token}")
    print(f"Found partner_id {partner_id} type {type(partner_id)}")
    if partner_id:
        partner_id = partner_id.decode('ascii')
    print(f"Id of matched partner is {partner_id} type {type(partner_id)}")

    if partner_id:
        response = {
          "set_attributes":
            {
              "found_match": "true",
              "partner_id": partner_id
            }
        }
        r.set(f'engaged_{engaging_token}', f"{partner_id}-{user_id}")
        r.set(f'partner_{partner_id}', user_id)
        r.set(f'partner_{user_id}', partner_id)

        async_broadcast(partner_id, f"Prave jsi byl zasoubeny s {user_name}")
        async_broadcast(user_id, f"Prave jsi byl zasoubeny s {get_my_partner_name(user_id)}")
    else:
        response = {
            "set_attributes":
                {
                    "found_match": "false"
                }
        }

    print(response)
    print(json.dumps(response))

    return jsonify(response)