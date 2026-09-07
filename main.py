import requests
from rich import console
from web3 import Web3
from rich.console import Console
from rich.table import Table
import os 
from dotenv import load_dotenv
load_dotenv()




class Wallet:
    def __init__(self):
        self.node = os.getenv('NODE_URL')
        self.private_key = os.getenv('PRIVATE_KEY')
        self.console  = Console()
        self.table = Table()


    def check_node(self):
        base_url = self.node.split('/v2/')[0]
        response = requests.get(base_url)
        if response.status_code == 200:
            self.console.print("URL/NODE ATIVO")
        else:
            self.console.print(f"URL/NODE INVALIDO OU OFFLINE {base_url}")

    def connect(self):
        self.w3 = Web3(Web3.HTTPProvider(self.node))
        return self.w3

    def config(self):
        self.connect()
        self.account = self.w3.eth.account.from_key(self.private_key)
        return self.account

    def show_info_loged(self):
        self.console.print(f"WALLET ADDRESS: {self.account.address}")
        self.console.print(f"BALANCE: {self.w3.from_wei(self.w3.eth.get_balance(self.account.address), 'ether'):.2f} ETH")
        self.console.print(f"LATEST BLOCK: {self.w3.eth.block_number}")
    def explore(self, limit=5):
        api_key = os.getenv('ETHERSCAN_API_KEY')
        api_url = (f"https://api-sepolia.etherscan.io/api?module=account&action=txlist"
                   f"&address={self.account.address}&startblock=0&endblock=99999999"
                   f"&sort=desc&page=1&offset={limit}&apikey={api_key}")
        response = requests.get(api_url).json()
        if response['status'] != '1':
            print(f"Erro Etherscan: {response.get('message')}")
            return
        for tx in response['result']:
            self.console.print(f"HASH: {tx['hash']}")
            self.console.print(f"  From: {tx['from']}")
            self.console.print(f"  To: {tx['to']}")
            self.console.print(f"  Value: {Web3.from_wei(int(tx['value']), 'ether')} ETH")
            self.console.print(f"  Link: https://sepolia.etherscan.io/tx/{tx['hash']}")
            self.console.print("-" * 40)

    def explorer_link(self, tx_hash):
        self.console.print(f"Veja no explorador: https://sepolia.etherscan.io/tx/{tx_hash}")

    def send_token(self):
        txn = {
            'from': self.account.address,
            'to': input("Wallet To Send: "),
            'value': self.w3.to_wei(float(input("Ammount, Ex: 0.001: ")),  'ether'),
            'gas': 21000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
                }
        sign_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(sign_txn.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.console.print(f"Tx Hash: {tx_hash.hex()}")
        self.console.print(f"Confirmed On Block: {receipt.blockNumber}")


if __name__ == "__main__":
    wallet = Wallet()
    wallet.config()
    wallet.show_info_loged()
    wallet.send_token()
