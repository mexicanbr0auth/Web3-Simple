import requests
from web3 import Web3


class Wallet:
    def __init__(self):
        import os
        from dotenv import load_dotenv
        load_dotenv()
        self.node = os.getenv('NODE_URL')
        self.private_key = os.getenv('PRIVATE_KEY')

    def check_node(self):
        base_url = self.node.split('/v2/')[0]
        response = requests.get(base_url)
        if response.status_code == 200:
            print("URL/NODE ATIVO")
        else:
            print(f"URL/NODE INVALIDO OU OFFLINE {base_url}")

    def connect(self):
        self.w3 = Web3(Web3.HTTPProvider(self.node))
        return self.w3

    def config(self):
        self.connect()
        self.account = self.w3.eth.account.from_key(self.private_key)
        return self.account

    def show_info_loged(self):
        print(f"WALLET ADDRESS: {self.account.address}")
        print(f"BALANCE: {self.w3.from_wei(self.w3.eth.get_balance(self.account.address), 'ether'):.2f} ETH")
        print(f"LATEST BLOCK: {self.w3.eth.block_number}")


if __name__ == "__main__":
    wallet = Wallet()
    wallet.config()
    wallet.show_info_loged()
