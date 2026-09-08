# Wallet - Web3 Python CLI

Carteira Ethereum em terminal usando [Web3.py](https://web3py.readthedocs.io), **rich** para visual e **WalletConnect** para conectar dapps — multi-rede (Sepolia, Amoy, Base, Arbitrum...).

## ⚙️ Funcionalidades

- Seleção de rede (mainnet e testnets EVM) via `config/config.py`
- Exibir endereço, saldo e último bloco
- Enviar ETH (rede manual)
- Explorar transações recentes via Etherscan API
- Verificar status do nó
- **WalletConnect v2**: conectar a dapps pelo link `wc:`, detectar a rede automaticamente, gerenciar sessões conectadas
- Responder a requests do dapp: `eth_sendTransaction`, `personal_sign`, `eth_signTypedData` (EIP-712), `eth_sign`, `eth_signTransaction`

## 📦 Pré-requisitos

- Python 3.x
- [pip](https://pip.pypa.io)

## 🚀 Instalação

```bash
pip install -r requirements.txt
```

## 🔧 Configuração

Crie um arquivo `.env` na mesma pasta do projeto com:

```env
NODE_URL=https://eth-sepolia.g.alchemy.com/v2/SUA_API_KEY
ALCHEMY_API_KEY=SUA_API_KEY
PRIVATE_KEY=SUA_CHAVE_PRIVADA
ETHERSCAN_API_KEY=SEU_KEY_ETHERSCAN
WALLETCONNECT_PROJECT_ID=SEU_PROJECT_ID
```

### Onde pegar cada chave

| Chave | Onde pegar |
|-------|-----------|
| `ALCHEMY_API_KEY` | [alchemy.com](https://www.alchemy.com) → App → View Key |
| `ETHERSCAN_API_KEY` | [etherscan.io/myapikey](https://etherscan.io/myapikey) |
| `WALLETCONNECT_PROJECT_ID` | [cloud.walletconnect.com](https://cloud.walletconnect.com) → New Project |

> ⚠️ **Importante:** Nunca compartilhe sua chave privada. O `.env` já está no `.gitignore`, então ele não vai para o GitHub.

## ▶️ Como usar

```bash
python main.py
```

### Modo 1 - Rede manual

```
Modo: [1] Rede manual [2] WalletConnect: 1
```

Lista as redes do `config/config.py`, escolhe, vê informações e envia ETH.

### Modo 2 - WalletConnect

```
Modo: [1] Rede manual [2] WalletConnect: 2

=== WalletConnect ===
1 - Conectar dapp
2 - Ver dapps conectados
3 - Sair
```

1. No dapp, clique em Connect Wallet → copie o link `wc:...` (ou escaneie o QR)
2. Cole o link no terminal
3. A rede é **detectada automaticamente** do sessionRequest
4. Aprove a sessão — o terminal vira a carteira
5. Requests do dapp (assinatura/envio) aparecem pra você aprovar

## 🧱 Estrutura

```
PYTHON/
├── .env               # Credenciais (não versionado)
├── .gitignore
├── main.py            # Código principal
├── config/
│   └── config.py      # Definições de redes (chainId, RPC, explorer)
├── docs/
│   └── web3_functions.md  # Guia de referência web3.py
├── requirements.txt
└── README.md
```

## 🌐 Redes suportadas

| Rede | Chain ID | RPC | Explorer |
|------|----------|-----|----------|
| Sepolia | 11155111 | Alchemy | sepolia.etherscan.io |
| Holesky | 17000 | Alchemy | holesky.etherscan.io |
| Polygon Amoy | 80002 | Alchemy | amoy.polygonscan.com |
| Base Sepolia | 84532 | Alchemy | sepolia.basescan.org |
| Arbitrum Sepolia | 421614 | Alchemy | sepolia.arbiscan.io |
| Optimism Sepolia | 11155420 | Alchemy | sepolia-optimistic.etherscan.io |
| BNB Testnet | 97 | Público | testnet.bscscan.com |
| Avalanche Fuji | 43113 | Público | testnet.snowtrace.io |

## 📚 Recursos usados

| Conceito | Explicação |
|----------|-----------|
| `Web3.HTTPProvider` | Conecta a um nó via HTTP |
| `from_key()` | Cria conta a partir da chave privada |
| `get_balance()` | Retorna saldo em Wei |
| `from_wei()` | Converte Wei para ETH |
| `WCClient.from_wc_uri()` | Conecta wallet a dapp via link `wc:` |
| `open_session()` | Retorna chain IDs e metadata do dapp |
| rich `Console`/`Table` | Visual colorido no terminal |

## 🗒️ Faucets (ETH de teste)

- Sepolia: [sepoliafaucet.com](https://sepoliafaucet.com)
- Amoy (Polygon): [faucets.chain.link](https://faucets.chain.link)

## 📝 Licença

Projeto de estudo pessoal.