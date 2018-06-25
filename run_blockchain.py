import json
import sys

import requests

from blockchain.create_contract.create import CreateContract
from contract_generator.cert import CertGenerator
from contract_generator.power_of import PowerOfGenerator
import redis
import json

eng_token = sys.argv[3]

print("Eng token ", eng_token)

redis_db = redis.Redis(host='localhost', port=6379, db=0)

partner_settings = json.loads(redis_db.get("commitment_"+eng_token))

# print(partner_settings)
# partner_settings = {}

medical = partner_settings.get("commitment_medial_records", "I don't") == "I do"
happiness = partner_settings.get("commitment_hapiness", "I don't") == "I do"
sexual = partner_settings.get("commitment_sexual_exclusivity", "I don't") == "I do"
duration = partner_settings.get("commitment_duration", 0)


template_settings = {
    "share_medical_records": ["bool",str(medical).lower()],
    "sexual_fidelity": ["bool", str(sexual).lower()],
    "relationship_duration_months": ["int", duration],
    "support_each_other": ["bool",  str(happiness).lower()],
}


# print(template_settings)
# print(json.dumps(template_settings))

contract_creator = CreateContract("./files/MarriageContract.sol", template_settings)

tx_id = contract_creator.deploy_contract()

account_a, account_a_pw = contract_creator.gen_account()
contract_creator.add_spouse(tx_id, account_a.address)

account_b, account_b_pw = contract_creator.gen_account()
contract_creator.add_spouse(tx_id, account_b.address)

generator = PowerOfGenerator("./files/power_of.png", "./temp_files/power_of_a_"+eng_token+".png", "./files/FiraSans-Black.ttf")
generator.add_names(sys.argv[1], sys.argv[2])

generator = PowerOfGenerator("./files/power_of.png", "./temp_files/power_of_b_"+eng_token+".png", "./files/FiraSans-Black.ttf")
generator.add_names(sys.argv[2], sys.argv[1])

generator = CertGenerator("./files/cert.png", "./temp_files/cert_"+eng_token+".png", "./files/FiraSans-Black.ttf")
generator.add_names(
    sys.argv[1],
    sys.argv[2],
    account_a.address,
    account_b.address
)

if duration != 0:
    generator.add_expiration_date(duration)

generator.add_contract_id(tx_id)
generator.save()

print("Executing callback")

cll = requests.get("http://localhost:5000/api/eth_callback/" + eng_token)
print("Status code ", cll.status_code)


