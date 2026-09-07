import os
import requests
from web3 import Web3
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from dotenv import load_dotenv

from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll, Container
from textual.widgets import Header, Footer, Button, Static, Input, Label
from textual.binding import Binding
from textual import on

load_dotenv()


class WalletApp(App):
    TITLE = "Wallet Sepolia"
    SUB_TITLE = "web3.py + rich + textual"
    CSS = """
    Screen {
        layout: horizontal;
        background: $surface;
    }

    #sidebar {
        width: 32;
        height: 100%;
        background: $panel;
        border-right: solid $primary;
        padding: 1;
    }

    #sidebar Button {
        width: 100%;
        margin-top: 1;
    }

    #content {
        width: 1fr;
        height: 100%;
        padding: 1 2;
    }

    #status {
        color: $text-muted;
        padding: 0 2;
    }

    #form {
        display: none;
        margin-top: 1;
    }

    Label {
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Sair"),
        Binding("1", "show_info", "Info"),
        Binding("2", "show_send", "Enviar"),
        Binding("3", "show_explore", "Explorar"),
        Binding("4", "check_node", "Node"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Container(id="sidebar"):
                yield Static("[b]CARTEIRA[/b]", id="logo")
                yield Button("1 - Informacoes", id="btn-info", variant="default")
                yield Button("2 - Enviar ETH", id="btn-send", variant="default")
                yield Button("3 - Explorar Txs", id="btn-explore", variant="default")
                yield Button("4 - Verificar Node", id="btn-node", variant="default")
                yield Static("", id="status")
            with VerticalScroll(id="content"):
                yield Static("", id="output")
                yield Container(
                    Label("Wallet destino:"),
                    Input(placeholder="0x...", id="in-to"),
                    Label("Quantidade (ETH):"),
                    Input(placeholder="0.001", id="in-amount"),
                    Button("Executar Envio", id="btn-exec", variant="success"),
                    id="form",
                )
        yield Footer()

    def on_mount(self) -> None:
        self.theme = "dracula"
        self.w3 = Web3(Web3.HTTPProvider(os.getenv('NODE_URL')))
        self.account = self.w3.eth.account.from_key(os.getenv('PRIVATE_KEY'))
        self.query_one("#status").update(f"[b cyan]{self.account.address[:14]}...[/b cyan]")

    def _show(self, renderable) -> None:
        self.query_one("#output").update(renderable)

    @on(Button.Pressed, "#btn-info")
    def on_info(self) -> None:
        self.show_info()

    def action_show_info(self) -> None:
        self.show_info()

    def show_info(self) -> None:
        self.query_one("#form").display = False
        balance = self.w3.from_wei(
            self.w3.eth.get_balance(self.account.address), "ether"
        )
        self._show(Panel(Text.from_markup(
            f"[b purple]ENDEREÇO[/b purple]\n{self.account.address}\n\n"
            f"[b purple]BALANCE[/b purple]\n{balance:.4f} [b green]ETH[/b green]\n\n"
            f"[b purple]BLOCO ATUAL[/b purple]\n{self.w3.eth.block_number}"
        ), border_style="purple", title="[b cyan]CARTEIRA[/b cyan]"))

    @on(Button.Pressed, "#btn-send")
    def on_send(self) -> None:
        self.show_send()

    def action_show_send(self) -> None:
        self.show_send()

    def show_send(self) -> None:
        self.query_one("#form").display = True
        self._show(Panel(
            "Preencha o destino e a quantidade abaixo:",
            border_style="orange3", title="[b pink]ENVIAR ETH[/b pink]",
        ))

    @on(Button.Pressed, "#btn-exec")
    def on_exec(self) -> None:
        self.execute_send()

    @on(Button.Pressed, "#btn-explore")
    def on_explore(self) -> None:
        self.show_explore()

    def action_show_explore(self) -> None:
        self.show_explore()

    def show_explore(self) -> None:
        self.query_one("#form").display = False
        api_key = os.getenv('ETHERSCAN_API_KEY')
        api_url = (f"https://api-sepolia.etherscan.io/api?module=account&action=txlist"
                   f"&address={self.account.address}&startblock=0&endblock=99999999"
                   f"&sort=desc&page=1&offset=5&apikey={api_key}")
        data = requests.get(api_url).json()
        if data['status'] != '1':
            self._show(Text.from_markup(f"[b red]Erro: {data.get('message')}[/b red]"))
            return
        table = Table(
            title="[b pink]ULTIMAS TRANSACOES[/b pink]",
            border_style="purple", expand=True,
        )
        table.add_column("Hash", style="cyan")
        table.add_column("Value", style="yellow", justify="right")
        table.add_column("Link")
        for tx in data['result']:
            value = self.w3.from_wei(int(tx['value']), 'ether')
            table.add_row(
                tx['hash'][:20],
                str(value),
                f"sepolia.etherscan.io/tx/{tx['hash'][:8]}",
            )
        self._show(table)

    @on(Button.Pressed, "#btn-node")
    def on_node(self) -> None:
        self.action_check_node()

    def action_check_node(self) -> None:
        self.query_one("#form").display = False
        base_url = self.node_url()
        try:
            status = requests.get(base_url).status_code
            color = "green" if status == 200 else "red"
            msg = f"[b {color}]● Node {'ATIVO' if status == 200 else 'OFELINE'} ({status})[/b {color}]"
        except requests.RequestException:
            msg = "[b red]● Node INACESSIVEL[/b red]"
        self._show(Panel(Text.from_markup(msg), border_style="green", title="[b cyan]NODE[/b cyan]"))

    def node_url(self) -> str:
        return os.getenv('NODE_URL').split('/v2/')[0]

    def execute_send(self) -> None:
        to = self.query_one("#in-to").value
        amount = self.query_one("#in-amount").value
        if not to or not amount:
            self._show(Text.from_markup("[b red]Preencha os dois campos![/b red]"))
            return
        txn = {
            'from': self.account.address,
            'to': to,
            'value': self.w3.to_wei(float(amount), 'ether'),
            'gas': 21000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
        }
        signed = self.w3.eth.account.sign_transaction(txn, os.getenv('PRIVATE_KEY'))
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self._show(Panel(Text.from_markup(
            f"[b green]✓ Confirmada no bloco {receipt.blockNumber}[/b green]\n\n"
            f"[cyan]https://sepolia.etherscan.io/tx/{tx_hash.hex()}[/cyan]"
        ), border_style="green", title="[b pink]ENVIO CONCLUIDO[/b pink]"))


if __name__ == "__main__":
    WalletApp().run()