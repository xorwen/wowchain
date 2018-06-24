import random
import redis
import string
import requests
from flask import Flask, jsonify, request, send_from_directory, abort
# import config
import urllib.parse
import json
import subprocess
import pickle

app = Flask(__name__)

r = redis.Redis(host='localhost', port=6379, db=0)

blocks = {
    'group_pending': '5b2f72cfe4b08d708d4d9e9c',
    'group_ready': '5b2f733de4b08d708d4edd6d',
    'finalise_vow': '5b2f3e0ce4b08d708ce0a055',
    'final_yes': '5b2f4316e4b08d708ce8be5a',
    'smart_contract': ''
}

def store_to_blockchain(token, name_a, name_b):
    contract_id = token
    out = f'./assets/{contract_id}-'
    command = [
        "python3", "run_blockchain.py",
        name_a, name_b,
        token.decode('ascii')
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


def async_broadcast(user_id, message, block):
    subprocess.Popen(["python3", "broadcast.py", user_id, message, block])


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


@app.route('/static_file/<path:path>')
def send_static(path):
    print("Sending static file ", path)

    if not path.endswith(".png"):
        abort(404)

    return send_from_directory("../temp_files/", path)



@app.route('/api/eth_callback/<eng_key>')
def eth_callback(eng_key):

    print("ETH callback ", eng_key)

    json_data = {
        "eng_key": eng_key,
        "images": [
            "http://46.101.117.31:5000/static_file/cert_" + eng_key + ".png",
            "http://46.101.117.31:5000/static_file/power_of_a_" + eng_key + ".png",
            "http://46.101.117.31:5000/static_file/power_of_b_" + eng_key + ".png",
        ]
    }

    for image in json_data["images"]:

        print("Sending image ", image)

        # async_broadcast(partner_id_a, image)
        # async_broadcast(partner_id_b, image)

    return jsonify(json_data)



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


def calculate_agreement(agr_a, agr_b):
    agr_c = {}
    binary_keys = [
     'commitment_medial_records', 'commitment_hapiness', 'commitment_sexual_exclusivity',
     'commitment_indefinite']

    for k in binary_keys:
        if agr_a.get(k) == 'I do' and agr_b.get(k) == 'I do':
            agr_c[k] = "I do"
        else:
            agr_c[k] = "I don't"

    agr_c['commitment_duration'] = min(int(agr_a.get('commitment_duration', 999)), int(agr_b.get('commitment_duration', 999)))
    print(agr_c)
    return agr_c

@app.route('/api/load_aggrements_params', methods=['GET'])
def load_aggrements_params():
    print("Received message", request.args)
    received = request.args.to_dict(flat=False)
    user_id = received['chatfuel user id'][0]
    engagement_token = r.get(f"gettoken_{user_id}").decode('ascii')
    partner_id = r.get(f"partner_{user_id}").decode('ascii')
    print(f"engagement_token: {engagement_token}")

    params = {}
    keys = ['commitment_duration',
            'commitment_medial_records','commitment_hapiness','commitment_sexual_exclusivity',
            'commitment_indefinite']
    for key in keys:
        if key in received:
            print(f"(setting)> {key}\t{received[key][0]}")
            params[key] = received[key][0]

    r.set(f'commitment_{user_id}>{partner_id}', pickle.dumps(params))

    if r.get(f'commitment_{partner_id}>{user_id}'):
        print("Found partner and calculating.")
        agr = calculate_agreement(
            pickle.loads(r.get(f'commitment_{user_id}>{partner_id}')),
            pickle.loads(r.get(f'commitment_{partner_id}>{user_id}'))
        )
        print(f"Storing commitment_{engagement_token} to redis")
        r.set(f'commitment_{engagement_token}', json.dumps(agr))

        print("Broadcasting both partners")
        final = {}
        for k, v in agr.items():
            final[f"conj_{k}"] = v

        broadcast(user_id, 'finalise_vow', attributes=final)
        broadcast(partner_id, 'finalise_vow', attributes=final)

        response = {
            "set_attributes": final
        }
    else:
        print("Stored and witing for partner to answer.")
        response = {
            "set_attributes": {}
        }

    #store_to_blockchain(engagement_token, name_a=user_name, name_b=partner_name)
    return jsonify(params)

@app.route('/static_file/<path:path>')
def send_static(path):
    print("Sending static file ", path)

    if not path.endswith(".png"):
        abort(404)

    return send_from_directory("../temp_files/", path)


@app.route('/api/final_yes', methods=['GET'])
def final_yes():
    received = request.args.to_dict(flat=False)
    user_id = received['chatfuel user id'][0]
    engagement_token = r.get(f"gettoken_{user_id}").decode('ascii')
    my_name  = f"{received['first name'][0]} {received['last name'][0]}"
    partner_name = get_my_partner_name(user_id)
    store_to_blockchain(engagement_token, name_a=my_name, name_b=partner_name)

@app.route('/api/validate_engaging_token', methods=['GET'])
def validate_engaging_token():
    print("Received message", request.args)
    received = request.args.to_dict(flat=False)
    engaging_token = received['engaging_token'][0]
    user_id = received['chatfuel user id'][0]
    user_name = f"{received['first name'][0]} {received['last name'][0]}"

    print("User name is f{user_name}")
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
        r.set(f'gettoken_{partner_id}', engaging_token)
        r.set(f'gettoken_{user_id}', engaging_token)

        async_broadcast(partner_id, f"You have just been engaged with {user_name}", 'group_ready')
        async_broadcast(user_id, f"You have just been engaged with {get_my_partner_name(user_id)}", 'group_ready')
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