import os
import requests
from web3 import Web3
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv
from pywalletconnect import WCClient, WCClientInvalidOption

from config.config import chains

load_dotenv()

console = Console()


class Wallet:
    def __init__(self):
        self.private_key = os.getenv('PRIVATE_KEY')
        self.chain = None
        self.wc_client = None
        self.connected_dapps = []

    def select_chain(self):
        table = Table(title="Selecione a Rede")
        table.add_column("#", style="cyan")
        table.add_column("Nome", style="yellow")
        table.add_column("Chain ID", justify="right")
        names = list(chains.keys())
        for i, name in enumerate(names, 1):
            table.add_row(str(i), chains[name]["name"], str(chains[name]["chainId"]))
        console.print(table)
        choice = int(input("Rede (numero): "))
        self.chain = chains[names[choice - 1]]
        self.node = f'{self.chain["rpc"]}/{os.getenv("ALCHEMY_API_KEY")}'
        console.print(f"Conectando a: {self.chain['name']} ({self.chain['chainId']})", style="bold green")

    def connect(self):
        self.w3 = Web3(Web3.HTTPProvider(self.node))
        return self.w3

    def config(self):
        self.connect()
        if not self.w3.is_connected():
            console.print("Falha ao conectar no no. Verifique NODE_URL.", style="bold red")
            raise SystemExit
        self.account = self.w3.eth.account.from_key(self.private_key)
        return self.account

    def show_info_loged(self):
        balance = self.w3.from_wei(self.w3.eth.get_balance(self.account.address), 'ether')
        console.rule(f"[bold cyan]{self.chain['name'].upper()} - INFORMACOES[/bold cyan]")
        console.print(f"WALLET ADDRESS: {self.account.address}")
        console.print(f"BALANCE: {balance:.2f}")
        console.print(f"LATEST BLOCK: {self.w3.eth.block_number}")

    def check_node(self):
        base_url = self.node.split('/v2/')[0] if '/v2/' in self.node else self.node
        response = requests.get(base_url)
        if response.status_code == 200:
            console.print("URL/NODE ATIVO", style="bold green")
        else:
            console.print(f"URL/NODE INVALIDO OU OFFLINE {base_url}", style="bold red")

    def explore(self, limit=5):
        api_key = os.getenv('ETHERSCAN_API_KEY')
        api_host = self.chain.get("explorer_api", "api-sepolia.etherscan.io")
        api_url = (f"https://{api_host}/api?module=account&action=txlist"
                   f"&address={self.account.address}&startblock=0&endblock=99999999"
                   f"&sort=desc&page=1&offset={limit}&apikey={api_key}")
        response = requests.get(api_url).json()
        if response['status'] != '1':
            console.print(f"Erro Etherscan: {response.get('message')}", style="bold red")
            return
        table = Table(title=f"Ultimas Transacoes - {self.chain['name']}")
        table.add_column("Hash", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_column("Link")
        explorer = self.chain.get("explorer", "sepolia.etherscan.io")
        for tx in response['result']:
            value = Web3.from_wei(int(tx['value']), 'ether')
            table.add_row(tx['hash'][:20], str(value), f"https://{explorer}/tx/{tx['hash']}")
        console.print(table)

    def explorer_link(self, tx_hash):
        explorer = self.chain.get("explorer", "sepolia.etherscan.io")
        console.print(f"Veja no explorador: https://{explorer}/tx/{tx_hash}")

    def send_token(self):
        to = input("Wallet To Send: ")
        amount = input("Amount, Ex: 0.001: ")
        txn = {
            'from': self.account.address,
            'to': to,
            'value': self.w3.to_wei(float(amount), 'ether'),
            'gas': 21000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
        }
        sign_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(sign_txn.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        console.print(f"Tx Hash: {tx_hash.hex()}", style="bold cyan")
        console.print(f"Confirmed On Block: {receipt.blockNumber}", style="bold green")
    def show_tokens(self):
        pass

    def connect_walletconnect(self):
        uri = input("Paste the WC URI (wc:...): ").strip()
        project_id = os.getenv('WALLETCONNECT_PROJECT_ID')
        if 'projectId=' in uri:
            import urllib.parse
            q = urllib.parse.parse_qs(uri.split('?')[1])
            project_id = q.get('projectId', [project_id])[0]
        WCClient.set_project_id(project_id)
        try:
            self.wc_client = WCClient.from_wc_uri(uri)
        except WCClientInvalidOption as exc:
            console.print(f"URI invalida: {exc}", style="bold red")
            return
        console.print("Aguardando sessionRequest do dapp...", style="yellow")
        try:
            req_id, chain_ids, request_info = self.wc_client.open_session()
        except Exception as exc:
            console.print(f"Timeout/erro na sessao: {exc}", style="bold red")
            return
        console.print(f"Requester name: {request_info.get('name')}", style="cyan")
        console.print(f"URL: {request_info.get('url')}", style="cyan")
        self.chain = self._detect_chain(chain_ids)
        if self.chain is None:
            console.print(f"Nenhuma rede suportada (dapp pediu: {chain_ids})", style="bold red")
            self.wc_client.close()
            return
        self.node = self._build_node(self.chain)
        self.config()
        console.print(f"Rede detectada: {self.chain['name']} ({self.chain['chainId']})", style="bold green")
        approve = input(f"Aprovar sessao do dapp? [y/N]: ")
        if approve.lower() == "y":
            self.wc_client.reply_session_request(req_id, self.chain["chainId"], self.account.address)
            self.connected_dapps.append({
                "name": request_info.get('name'),
                "url": request_info.get('url'),
                "chain": self.chain["name"],
                "client": self.wc_client,
            })
            console.print("Sessao aprovada. Aguardando requests (wallet_approve encerra)...", style="green")
            self._wc_message_loop()
        else:
            self.wc_client.reject_session_request(req_id)
            console.print("Sessao rejeitada.", style="red")

    def _detect_chain(self, chain_ids):
        for chain_id in chain_ids:
            chain_id = str(chain_id).split(':')[-1]
            if chain_id.isdigit():
                for name, info in chains.items():
                    if str(info["chainId"]) == chain_id:
                        return info
        return None

    def _build_node(self, chain):
        if "/v2" in chain["rpc"]:
            return f'{chain["rpc"]}/{os.getenv("ALCHEMY_API_KEY")}'
        return chain["rpc"]

    def _wc_message_loop(self):
        while True:
            call_id, method, params = self.wc_client.get_message()
            if call_id is None:
                continue
            console.print(f"[yellow]>> NEW REQUEST[/yellow] id={call_id} method={method}")
            if method == 'eth_sendTransaction':
                self._handle_send_transaction(call_id, params)
            elif method == 'eth_signTransaction':
                self._handle_sign_transaction(call_id, params)
            elif method == 'personal_sign':
                self._handle_personal_sign(call_id, params)
            elif method in ('eth_signTypedData', 'eth_signTypedData_v3', 'eth_signTypedData_v4'):
                self._handle_sign_typed(call_id, method, params)
            elif method == 'eth_sign':
                self._handle_eth_sign(call_id, params)
            elif method in ('wallet_addEthereumChain', 'wallet_switchEthereumChain'):
                self.wc_client.reply(call_id, None)
            elif method == 'wc_sessionRequest':
                self.wc_client.reply(call_id, True)
            elif method == 'wallet_approve':
                self.wc_client.reply(call_id, True)
                self.wc_client.close()
                console.print("Dapp fechou a sessao.", style="red")
                break
            else:
                console.print(f"[red]Metodo sem handler: {method}[/red] (params: {params})")
                if input("Responder com erro? [y/N]: ").lower() == 'y':
                    self.wc_client.reject(call_id)
                else:
                    self.wc_client.reply(call_id, None)

    def _handle_send_transaction(self, call_id, params):
        tx = params[0]
        console.print(f"  From: {tx.get('from')}")
        console.print(f"  To: {tx.get('to')}")
        console.print(f"  Value: {Web3.from_wei(int(tx.get('value', 0)), 'ether')} ETH")
        console.print(f"  Data: {str(tx.get('data'))[:40]}...")
        if input("Enviar esta transacao? [y/N]: ").lower() == 'y':
            signed = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            self.wc_client.reply(call_id, tx_hash.hex())
            console.print(f"Tx enviada: {tx_hash.hex()}", style="bold green")
        else:
            self.wc_client.reject(call_id)

    def _handle_sign_transaction(self, call_id, params):
        tx = params[0]
        console.print(f"  Sign Tx -> To: {tx.get('to')} Value: {Web3.from_wei(int(tx.get('value', 0)), 'ether')} ETH")
        if input("Assinar transacao? [y/N]: ").lower() == 'y':
            signed = self.w3.eth.account.sign_transaction(tx, self.private_key)
            self.wc_client.reply(call_id, signed.raw_transaction.hex())
            console.print("Transacao assinada.", style="bold green")
        else:
            self.wc_client.reject(call_id)

    def _handle_personal_sign(self, call_id, params):
        msg_hex = params[0]
        msg = bytes.fromhex(msg_hex[2:]) if msg_hex.startswith('0x') else msg_hex.encode()
        console.print(f"  Mensagem: {msg[:64]!r}")
        if input("Assinar mensagem? [y/N]: ").lower() == 'y':
            sig = self.w3.eth.account.sign_message(msg, self.private_key).signature.hex()
            self.wc_client.reply(call_id, "0x" + sig)
            console.print("Mensagem assinada.", style="bold green")
        else:
            self.wc_client.reject(call_id)

    def _handle_sign_typed(self, call_id, method, params):
        domain = params[1]
        console.print(f"  TypedData domain name: {domain.get('name', 'N/A')}")
        console.print(f"  VerifyingContract: {domain.get('verifyingContract', 'N/A')}")
        if input(f"Assinar {method}? [y/N]: ").lower() == 'y':
            from eth_account.messages import encode_typed_data
            data = encode_typed_data(full_message=params[1]) if method in ('eth_signTypedData', 'eth_signTypedData_v4') else encode_typed_data(full_message=params[1])
            sig = self.w3.eth.account.sign_message(data, self.private_key).signature.hex()
            self.wc_client.reply(call_id, "0x" + sig)
            console.print("TypedData assinado.", style="bold green")
        else:
            self.wc_client.reject(call_id)

    def _handle_eth_sign(self, call_id, params):
        message = bytes.fromhex(params[1][2:]) if params[1].startswith('0x') else params[1].encode()
        if input("Assinar com eth_sign (perigoso)? [y/N]: ").lower() == 'y':
            from eth_account.messages import encode_defunct
            data = encode_defunct(primitive=message)
            sig = self.w3.eth.account.sign_message(data, self.private_key).signature.hex()
            self.wc_client.reply(call_id, "0x" + sig)
        else:
            self.wc_client.reject(call_id) 

    def show_dapps(self):
        table = Table(title="Dapps Conectados")
        table.add_column("#", style="cyan")
        table.add_column("Nome", style="yellow")
        table.add_column("URL", style="magenta")
        table.add_column("Rede", style="green")
        if not self.connected_dapps:
            console.print("Nenhum dapp conectado.", style="red")
            return
        for i, dapp in enumerate(self.connected_dapps, 1):
            table.add_row(str(i), dapp["name"], dapp["url"], dapp["chain"])
        console.print(table)
        choice = input("Digite o numero do dapp para desconectar (Enter p/ voltar): ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(self.connected_dapps):
                removed = self.connected_dapps.pop(idx)
                removed["client"].close()
                console.print(f"Desconectado: {removed['name']}", style="bold red")


if __name__ == "__main__":
    wallet = Wallet()
    mode = input("Modo: [1] Rede manual [2] WalletConnect: ")
    if mode == "2":
        while True:
            console.print("\n[bold cyan]=== WalletConnect ===[/bold cyan]")
            console.print("1 - Conectar dapp")
            console.print("2 - Ver dapps conectados")
            console.print("3 - Sair")
            option = input("Opcao: ")
            if option == "1":
                wallet.connect_walletconnect()
            elif option == "2":
                wallet.show_dapps()
            elif option == "3":
                break
            else:
                console.print("Opcao invalida.", style="bold red")
    else:
        wallet.select_chain()
        wallet.config()
        wallet.show_info_loged()
        wallet.send_token()
