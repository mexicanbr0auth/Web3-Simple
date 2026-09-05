# Wallet - Web3 Python

Um projeto simples de carteira Ethereum usando a biblioteca [Web3.py](https://web3py.readthedocs.io) conectada a um nó da Alchemy na rede **Sepolia** (testnet).

## ⚙️ Funcionalidades

- Consultar o estado do nó da Alchemy
- Conectar à rede Sepolia
- Carregar carteira a partir da chave privada
- Exibir endereço, saldo e último bloco da rede

## 📦 Pré-requisitos

- Python 3.x
- [pip](https://pip.pypa.io)

## 🚀 Instalação

```bash
pip install web3 requests python-dotenv
```

## 🔧 Configuração

Crie um arquivo `.env` na mesma pasta do projeto com:

```env
NODE_URL=https://eth-sepolia.g.alchemy.com/v2/SUA_API_KEY
PRIVATE_KEY=SUA_CHAVE_PRIVADA
```

> ⚠️ **Importante:** Nunca compartilhe sua chave privada. O `.env` já está no `.gitignore`, então ele não vai para o GitHub.

## ▶️ Como usar

```bash
python main.py
```

Saída esperada:

```
WALLET ADDRESS: 0x09ac...a49b
BALANCE: 0.05 ETH
LATEST BLOCK: 5123456
```

## 🧱 Estrutura

```
PYTHON/
├── .env          # Credenciais (não versionado)
├── .gitignore
├── main.py       # Código principal
└── README.md
```

## 📚 Recursos usados

| Conceito | Explicação |
|----------|-----------|
| `Web3.HTTPProvider` | Conecta a um nó via HTTP |
| `from_key()` | Cria conta a partir da chave privada |
| `get_balance()` | Retorna saldo em Wei |
| `from_wei()` | Converte Wei para ETH |
| `block_number` | Último bloco minerado |

## 🗒️ Guar: testar na Sepolia

Para conseguir ETH de teste (faucet):

- [sepoliafaucet.com](https://sepoliafaucet.com)

## 📝 Licença

Projeto de estudo pessoal.