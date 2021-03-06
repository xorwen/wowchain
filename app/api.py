import random
import redis
import string
import requests
from flask import Flask, jsonify, request, send_from_directory, abort
import config
import urllib.parse
import json
import subprocess
import time
import pickle
from flask_cors import cross_origin

import sys

sys.path.append('..')

from blockchain.create_contract.create import CreateContract

app = Flask(__name__)

r = redis.Redis(host='localhost', port=6379, db=0)

blocks = {
    'group_pending': '5b2f72cfe4b08d708d4d9e9c',
    'group_ready': '5b2f733de4b08d708d4edd6d',
    'finalise_vow': '5b2f3e0ce4b08d708ce0a055',
    'final_yes': '5b2f4316e4b08d708ce8be5a',
    'contract_created': '5b2f79f7e4b08d708d5da209',
    'get_documents': '5b30d9c5e4b08507221cc383'
}


def store_to_blockchain(token, name_a, name_b):
    contract_id = token
    out = f'./assets/{contract_id}-'
    print(token)
    command = [
        "python3", "run_blockchain.py",
        name_a, name_b,
        token
    ]
    subprocess.Popen(command, cwd='..')


def get_random_string(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def broadcast(user_id, block_name, attributes=None):
    time.sleep(1)
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
    user_id = request.args.get('user_id', '')
    print(f"Broadcasting test mesage to {user_id}")
    async_broadcast(user_id, "test broadcast message")
    return jsonify({"ok": 1})


@app.route('/api/test_marrige')
def test_marrige():
    store_to_blockchain()
    return jsonify({"ok": 1})


@app.route('/api/contract_state/<contract_id>')
@cross_origin()
def eth_cotract_state(contract_id):
    contract_creator = CreateContract("../files/MarriageContract.sol", template_settings=None)

    caller = contract_creator.get_contract_caller(contract_id)

    contract_values = {
        "share_medical_records": caller.share_medical_records(),
        "sexual_fidelity": caller.sexual_fidelity(),
        "relationship_duration_months": caller.relationship_duration_months(),
        "support_each_other": caller.support_each_other(),
    }

    return jsonify(contract_values)


@app.route('/api/eth_callback/<eng_key>')
def eth_callback(eng_key):
    print("ETH callback ", eng_key)

    user_a, user_b = str(r.get("engaged_" + eng_key).decode('ascii')).split("-")
    print("Broadcasting eth_callback to ", user_a, user_b)

    time.sleep(1)
    broadcast(user_a, 'get_documents')
    time.sleep(1)
    broadcast(user_b, 'get_documents')
    time.sleep(1)

    return jsonify({})


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
    print(f"Getting from redis partner id: partner_{my_id}")
    partner_id = r.get(f"partner_{my_id}")
    if partner_id:
        partner_id = partner_id.decode('ascii')
    print(f"Getting from redis partner name: username_{partner_id}")
    partner_name = r.get(f"username_{partner_id}")
    print("Got", partner_name)
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

    a_duration = int(agr_a['commitment_duration']) if agr_a.get('commitment_duration', '').isnumeric() else None
    b_duration = int(agr_b['commitment_duration']) if agr_b.get('commitment_duration', '').isnumeric() else None

    if a_duration or b_duration:
        agr_c['commitment_duration'] = min(a_duration, b_duration)
    else:
        agr_c['commitment_duration'] = 'indefinite'

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
            'commitment_medial_records', 'commitment_hapiness', 'commitment_sexual_exclusivity',
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
        time.sleep(1)
        broadcast(partner_id, 'finalise_vow', attributes=final)
        time.sleep(1)

        response = {
            "set_attributes": final
        }
    else:
        print("Stored and witing for partner to answer.")
        response = {
            "set_attributes": {}
        }

    # store_to_blockchain(engagement_token, name_a=user_name, name_b=partner_name)
    return jsonify(params)


@app.route('/static_file/<path:path>')
def send_static(path):
    print("Sending static file ", path)

    if not (path.endswith(".png") or path.endswith(".jpeg")):
        abort(404)

    return send_from_directory("../temp_files/", path)


@app.route('/api/final_yes', methods=['GET'])
def final_yes():
    received = request.args.to_dict(flat=False)
    user_id = received['chatfuel user id'][0]  # b'MSHM8W'
    print(f"Received user_id {user_id}")
    engagement_token = str(r.get(f"gettoken_{user_id}"))[2:-1]
    my_name = f"{received['first name'][0]} {received['last name'][0]}"
    partner_name = get_my_partner_name(user_id)
    print("partner name:", partner_name)
    if not partner_name:
        partner_name = "Pavel"
    print(f"user_id {user_id},  engagement_token {engagement_token}, my_name {my_name}, partner_name {partner_name} ")
    store_to_blockchain(engagement_token, name_a=my_name, name_b=partner_name)

    return jsonify({
        "set_attributes":
            {
                "blockchain_recored_started": "true"
            }
    })


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
        time.sleep(1)
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


@app.route('/api/get_documents', methods=['GET'])
def get_documents():
    print("Received message", request.args)
    received = request.args.to_dict(flat=False)
    user_id = received['chatfuel user id'][0]
    engaging_token = r.get(f"gettoken_{user_id}").decode('ascii')
    print(f"engtoken: {engaging_token}")
    domain = 'plants.id'  # 46.101.117.31
    port = ""

    certificate_url = f"http://{domain}{port}/static_file/cert_{engaging_token}"
    power_a_url = f"http://{domain}{port}/static_file/power_of_a_{engaging_token}"
    power_b_url = f"http://{domain}{port}/static_file/power_of_b_{engaging_token}"

    print(f"""
    cert {certificate_url}
    powA {power_a_url}
    powB {power_b_url}
    """)

    resp = {
        "messages": [
            {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "image_aspect_ratio": "square",
                        "elements": [
                            {
                                "title": "Certificate",
                                "image_url": f"{certificate_url}.png",
                                "subtitle": "Your ETH certificate",
                                "buttons": [
                                    {
                                        "type": "web_url",
                                        "url": f"{certificate_url}.png",
                                        "title": "View Item"
                                    }
                                ]
                            },
                            {
                                "title": "Power of attorney (A)",
                                "image_url": f"{power_a_url}.png",
                                "subtitle": "To print and sign up",
                                "default_action": {
                                    "type": "web_url",
                                    "url": f"{power_a_url}.png"
                                },
                                "buttons": [
                                    {
                                        "type": "web_url",
                                        "url": f"{power_a_url}.png",
                                        "title": "View Item"
                                    }
                                ]
                            },
                            {
                                "title": "Power of attorney (B)",
                                "image_url": f"{power_b_url}.png",
                                "subtitle": "To print and sign up",
                                "default_action": {
                                    "type": "web_url",
                                    "url": f"{power_b_url}.png"
                                },
                                "buttons": [
                                    {
                                        "type": "web_url",
                                        "url": f"{power_b_url}.png",
                                        "title": "View Item"
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        ]
    }

    return jsonify(resp)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
