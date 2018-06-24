import json
import random
import string
import web3
from solc import compile_source
from web3.auto import w3
from rlp import encode
from ethereum.transactions import Transaction
import secret_keys




class CreateContract(object):

    system_account_private = secret_keys.system_account_private

    system_account = w3.eth.account.privateKeyToAccount(system_account_private)

    web3 = web3.Web3(web3.HTTPProvider(secret_keys.infura_url))

    template_settings = {
        "share_medical_records": ["bool", "true"],
        "sexual_fidelity": ["bool", "true"],
        "relationship_duration_months": ["int", 10],
        "support_each_other": ["bool", "true"],
    }

    def __init__(self, contract_file_path, template_settings):

        compiled_sol = self.compile_source_file(contract_file_path)
        self.template_settings = template_settings

        contract_interface = compiled_sol[list(compiled_sol.keys())[0]]

        self.prepared_contract = self.web3.eth.contract(
            abi=contract_interface['abi'],
            bytecode=contract_interface['bin'],
        )

    def compile_source_file(self, file_path):

        with open(file_path, 'r') as f:
            source = f.read()

        for conf_name, conf_val in self.template_settings.items():

            source = source.replace(conf_name + "_val", str(conf_val[1]))
            source = source.replace(conf_name + "_type", conf_val[0])

        print("Contract source : ")
        print(source)
        print()

        return compile_source(source)

    def gen_account_password(self):

        password = []

        all_chars = string.ascii_letters + string.punctuation + string.digits

        for _ in range(20):

            password.append(random.choice(all_chars))

        return "".join(password)


    def gen_account(self):

        account_password = self.gen_account_password()

        account = w3.eth.account.create(account_password)


        # self.send_eth_to_account(account, 16302952000000000)

        print("Generated account ", account.address)

        account_json = {
            "public_key": account.address,
            "private_key": self.web3.toHex(account.privateKey),
            "password": account_password
        }
        account_json = json.dumps(account_json)

        account_file = "./temp_files/"+account.address+".txt"

        print("Saved account to ",account_file)

        text_file = open(account_file, "w")
        text_file.write(account_json)
        text_file.close()

        return account, account_password

    def send_eth_to_account(self, account, amount):

        print("Sending amount ", amount)
        print("Sending to account ", account.address)
        print("Sending from system account ", self.system_account.address)

        tx = Transaction(
            nonce=self.web3.eth.getTransactionCount(self.system_account.address),
            gasprice=w3.toWei('100', 'gwei'),
            startgas=90000,
            to=account.address,
            value=amount,
            data="0x0"
        )

        tx.sign(self.system_account.privateKey)

        tx_hex_signed = self.web3.toHex(encode(tx))

        self.web3.eth.sendRawTransaction(tx_hex_signed)


    def deploy_contract(self):

        print("Constructing transaction")

        construct_txn = self.prepared_contract.constructor().buildTransaction({
            'from': self.system_account.address,
            'nonce': self.web3.eth.getTransactionCount(self.system_account.address),
            'gas': 503116,
            'gasPrice': w3.toWei('100', 'gwei')}
        )

        print("Signing transaction")

        signed = self.system_account.signTransaction(construct_txn)

        print("Sending transaction")

        print("System account ",self.system_account.address)

        transaction_id = self.web3.eth.sendRawTransaction(signed.rawTransaction)

        transaction_id = self.web3.eth.waitForTransactionReceipt(transaction_id, timeout=120)

        print("Contract ID ", str(transaction_id["contractAddress"]))

        return transaction_id["contractAddress"]

    def add_spouse(self, contract_id, spouse_address):

        print("Adding ",spouse_address, "to countract ", contract_id)

        transaction = self.prepared_contract(contract_id).functions.addSpouse(spouse_address).buildTransaction({
            'from': self.system_account.address,
            'nonce': self.web3.eth.getTransactionCount(self.system_account.address),
            'gas': 503116,
            'gasPrice': w3.toWei('100', 'gwei')}
        )

        transaction = self.system_account.signTransaction(transaction)

        print("Sending transaction")

        transaction_id = self.web3.eth.sendRawTransaction(transaction.rawTransaction)

        transaction_id = self.web3.eth.waitForTransactionReceipt(transaction_id, timeout=120)

        return transaction_id["contractAddress"]

