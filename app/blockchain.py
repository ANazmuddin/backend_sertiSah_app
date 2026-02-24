import os
from web3 import Web3
from dotenv import load_dotenv

# =============================
# LOAD ENVIRONMENT VARIABLES
# =============================
load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
RPC_URL = os.getenv("RPC_URL")

# =============================
# VALIDATION
# =============================
if not PRIVATE_KEY:
    raise ValueError("PRIVATE_KEY tidak ditemukan di .env")

if not WALLET_ADDRESS:
    raise ValueError("WALLET_ADDRESS tidak ditemukan di .env")

if not CONTRACT_ADDRESS:
    raise ValueError("CONTRACT_ADDRESS tidak ditemukan di .env")

if not RPC_URL:
    raise ValueError("RPC_URL tidak ditemukan di .env")

# =============================
# WEB3 CONNECTION
# =============================
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    raise ConnectionError("Gagal terhubung ke RPC Polygon Amoy")

# =============================
# SMART CONTRACT ABI
# =============================
contract_abi = [
    {
        "inputs": [{"internalType": "string", "name": "_hash", "type": "string"}],
        "name": "storeCertificate",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "_hash", "type": "string"}],
        "name": "verifyCertificate",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# =============================
# CONTRACT INSTANCE
# =============================
contract = w3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=contract_abi
)

# =============================
# STORE CERTIFICATE ON BLOCKCHAIN
# =============================
def store_certificate_on_chain(certificate_hash: str):
    try:
        nonce = w3.eth.get_transaction_count(WALLET_ADDRESS)

        txn = contract.functions.storeCertificate(
            certificate_hash
        ).build_transaction({
            "chainId": 80002,  # Polygon Amoy
            "gas": 200000,
            "gasPrice": w3.to_wei("30", "gwei"),
            "nonce": nonce,
        })

        signed_txn = w3.eth.account.sign_transaction(
            txn,
            private_key=PRIVATE_KEY
        )

        tx_hash = w3.eth.send_raw_transaction(
            signed_txn.raw_transaction
        )

        tx_hash_hex = w3.to_hex(tx_hash)

        # Tunggu sampai transaksi mined (lebih aman)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status != 1:
            raise Exception("Transaksi gagal di blockchain")

        return tx_hash_hex

    except Exception as e:
        print("BLOCKCHAIN STORE ERROR:", str(e))
        return None


# =============================
# VERIFY CERTIFICATE ON BLOCKCHAIN
# =============================
def verify_certificate_on_chain(certificate_hash: str):
    try:
        return contract.functions.verifyCertificate(
            certificate_hash
        ).call()
    except Exception as e:
        print("BLOCKCHAIN VERIFY ERROR:", str(e))
        return False