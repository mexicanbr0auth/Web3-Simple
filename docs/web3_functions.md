# Funções Web3.py — Guia Rápido

Tabela de referência para consulta rápida. Mostre com `self.` quando estiver dentro de uma classe.

---

## 🔌 Conexão e Nó

| Função | Descrição |
|--------|-----------|
| `Web3(Web3.HTTPProvider(url))` | Conecta a um nó via HTTP |
| `Web3(Web3.WebsocketProvider(url))` | Conecta a um nó via WebSocket |
| `w3.is_connected()` | Retorna `True`/`False` se conectou |
| `w3.eth.block_number` | Último bloco minerado |
| `w3.eth.gas_price` | Preço atual do gas (Wei) |
| `w3.eth.chain_id` | ID da rede (1=mainnet, 11155111=Sepolia) |
| `w3.client_version` | Versão do cliente do nó |
| `w3.eth.max_priority_fee_per_gas` | Taxa prioritária (EIP-1559) |
| `w3.eth.max_fee_per_gas` | Taxa máxima (EIP-1559) |

## 💱 Conversão de Unidades

| Função | Descrição |
|--------|-----------|
| `Web3.to_wei(valor, 'ether')` | ETH → Wei |
| `Web3.from_wei(valor, 'ether')` | Wei → ETH |
| `Web3.to_wei(valor, 'gwei')` | Gwei → Wei |
| `Web3.to_checksum_address(addr)` | Valida/corrige endereço |
| `w3.to_hex(valor)` | Converte para formato hex |
| `w3.to_int(valor)` | Converte para int |
| `w3.sha3(text='...')` | Hash keccak256 de texto |
| `w3.solidity_keccak([tipos], [valores])` | Hash de tipos Solidity |

## 👤 Contas

| Função | Descrição |
|--------|-----------|
| `w3.eth.account.create()` | Cria nova carteira |
| `w3.eth.account.from_key(pk)` | Carrega carteira pela chave privada |
| `account.address` | Endereço da conta |
| `account.key.hex()` | Chave privada em texto |
| `w3.eth.accounts` | Contas do nó (se houver) |
| `w3.eth.account.recover_message(msg, sig)` | Recupera conta de uma assinatura |
| `w3.eth.account.sign_message(msg, pk)` | Assina uma mensagem |

## 🔍 Consultas

| Função | Descrição |
|--------|-----------|
| `w3.eth.get_balance(addr)` | Saldo em Wei |
| `w3.eth.get_transaction_count(addr)` | Nonce da conta |
| `w3.eth.get_transaction(tx_hash)` | Dados de uma tx |
| `w3.eth.get_transaction_receipt(tx_hash)` | Recibo de confirmação |
| `w3.eth.get_block(num)` | Dados do bloco (`'latest'`, `'pending'`) |
| `w3.eth.get_code(addr)` | Código do contrato |
| `w3.eth.get_storage_at(addr, slot)` | Storage do contrato |
| `w3.eth.estimate_gas(txn)` | Gas estimado para executar a tx |
| `w3.eth.get_logs({...})` | Busca eventos/logs |

## 🚀 Envio de Transações

| Função | Descrição |
|--------|-----------|
| `w3.eth.send_raw_transaction(signed)` | Envia tx ASSINADA → retorna `tx_hash` |
| `w3.eth.send_transaction(txn)` | Envia tx (nó assina; requer chave no nó) |
| `w3.eth.account.sign_transaction(txn, pk)` | Assina a transação |
| `w3.eth.wait_for_transaction_receipt(hash)` | Espera mineração, retorna recibo |
| `tx_hash.hex()` | Converte hash em string |
| `receipt.blockNumber` | Bloco onde foi confirmada |
| `receipt.status` | `1` = sucesso, `0` = falhou |
| `w3.eth.replace_transaction(hash)` | Substitui tx pendente |

### Fluxo padrão de envio (com `self.` dentro da classe)

```python
txn = {
    'from': self.account.address,
    'to': destino,
    'value': self.w3.to_wei(valor, 'ether'),
    'gas': 21000,
    'gasPrice': self.w3.eth.gas_price,
    'nonce': self.w3.eth.get_transaction_count(self.account.address),
}

signed = self.w3.eth.account.sign_transaction(txn, self.private_key)
tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
```

## 📜 Contratos

| Função | Descrição |
|--------|-----------|
| `w3.eth.contract(address, abi)` | Cria instância do contrato |
| `contract.functions.METODO(...).call()` | LÊ dados (sem gas) |
| `contract.functions.METODO(...).build_transaction({...})` | ESCREVE (gasta gas) |
| `contract.functions.METODO(...).transact({...})` | Envia direto |
| `contract.events.EVENTO.create_filter(...)` | Filtra eventos |
| `contract.events.EVENTO.get_logs(...)` | Busca logs antigos |
| `contract.functions.METODO(...).estimate_gas()` | Estima gas do método |
| `contract.encodeABI(fn_name='...')` | Codifica chamada ABI |

## 🎯 Regras de Ouro

1. **Dentro da classe** use sempre `self.w3` / `self.account` (nunca `w3`)
2. **Ler** contrato = `.call()`, **escrever** = `.build_transaction()`
3. Saldo vem em **Wei**, sempre converta com `from_wei`
4. `send_raw_transaction` recebe a tx **assinada**
5. Para mutar state (escrever), você precisa de `nonce`, `gas` e assinatura
6. `tx_hash.hex()` transforma o hash em string legível

---

### Links úteis
- Documentação oficial: https://web3py.readthedocs.io
- Faucet Sepolia: https://sepoliafaucet.com