import requests
from web3 import Web3

class Wallet:
    def __init__(self, private_key=None):
        self.node = "https://eth-sepolia.g.alchemy.com/v2/alch_JucH1ob__oCy8NasW_ypV"
        self.private_key = private_key

    def check_node(self):
        base_url = self.node.split('/v2/')[0]
        response = requests.get(base_url)
        if response.status_code == 200:
            print("URL/NODE ATIVO")
        else:
            return print(f"URL/NODE INVALIDO OU OFFLINE  {base_url} ")
    def connect(self):
        self.w3 = Web3(Web3.HTTPProvider(self.node))
        print(f"LOG:  {self.w3}")
        return self.w3

    def config(self):
        call = connect()
        self.account = w3.e1th.account.from_key(self.private_key)
        return self.account
    def show_info_loged(self):
        call = connect()
        pass 
       # print(f"WALLET ADDRESS: {}")
        #terminar maanha kkkkkkkkkk e corrigir erros 






if __name__ == "__main__":
    contact = Wallet()
    contact.check_node()
