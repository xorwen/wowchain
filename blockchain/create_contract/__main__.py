
import sys
from .create import CreateContract

template_settings = {
    "share_medical_records": ["bool", "true"],
    "sexual_fidelity": ["bool", "true"],
    "relationship_duration_months": ["int", 10],
    "support_each_other": ["bool", "true"],
}

contract_creator = CreateContract(sys.argv[1], template_settings)

tx_id = contract_creator.deploy_contract()

account, account_pw = contract_creator.gen_account()
contract_creator.add_spouse(tx_id, account.address)

account, account_pw = contract_creator.gen_account()
contract_creator.add_spouse(tx_id, account.address)