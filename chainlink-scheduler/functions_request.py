#!/usr/bin/env python3
"""
Python-only Chainlink Functions request runner (Sepolia)

- Reads Functions JS source from functions/source.js (plain text)
- Calls consumer.setSource(source)
- Calls consumer.sendRequest(subscriptionId, args)
- Polls for consumer's Response event
- Prints one-line JSON to stdout

Dependencies:
  pip install web3 python-dotenv
"""

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from web3 import Web3
from web3.exceptions import ContractLogicError, TransactionNotFound

load_dotenv()

SEPOLIA_RPC_URL = os.environ.get("SEPOLIA_RPC_URL", "").strip()
PRIVATE_KEY = os.environ.get("PRIVATE_KEY", "").strip()
CONSUMER_ADDRESS_RAW = os.environ.get("CONSUMER_ADDRESS", "").strip()
SUBSCRIPTION_ID_RAW = os.environ.get("SUBSCRIPTION_ID", "").strip()

# Minimal ABI: only what we call + event we listen for
ABI = [
    {
        "inputs": [{"internalType": "string", "name": "newSource", "type": "string"}],
        "name": "setSource",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint64", "name": "subscriptionId", "type": "uint64"},
            {"internalType": "string[]", "name": "args", "type": "string[]"},
        ],
        "name": "sendRequest",
        "outputs": [{"internalType": "bytes32", "name": "requestId", "type": "bytes32"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "bytes32", "name": "requestId", "type": "bytes32"},
            {"indexed": False, "internalType": "string", "name": "response", "type": "string"},
            {"indexed": False, "internalType": "bytes", "name": "err", "type": "bytes"},
        ],
        "name": "Response",
        "type": "event",
    },
]


def fail(payload: Dict[str, Any], exit_code: int = 1) -> None:
    print(json.dumps(payload))
    raise SystemExit(exit_code)


def wait_for_receipt(w3: Web3, tx_hash: bytes, timeout_s: int = 300) -> Dict[str, Any]:
    """Poll for a transaction receipt. Handles providers that raise TransactionNotFound."""
    start = time.time()
    while True:
        try:
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            if receipt is not None:
                return dict(receipt)
        except TransactionNotFound:
            pass

        if time.time() - start > timeout_s:
            raise TimeoutError(f"Timed out waiting for tx receipt: {tx_hash.hex()}")

        time.sleep(2)


def build_fees(w3: Web3) -> Dict[str, int]:
    """
    Build EIP-1559 fee fields conservatively.
    Many providers accept omitting these and letting eth_estimateGas handle it,
    but this explicit approach is stable across RPCs.
    """
    try:
        base = w3.eth.gas_price  # a usable heuristic on testnets
    except Exception:
        base = w3.to_wei(10, "gwei")

    max_priority = w3.to_wei(1, "gwei")
    max_fee = int(base * 2) + int(max_priority)
    return {
        "maxFeePerGas": max_fee,
        "maxPriorityFeePerGas": int(max_priority),
    }


def send_tx(w3: Web3, account, tx: Dict[str, Any]) -> bytes:
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    # Version-robust: web3.py may use raw_transaction (new) or rawTransaction (old)
    raw = getattr(signed, "rawTransaction", None) or getattr(signed, "raw_transaction")
    return w3.eth.send_raw_transaction(raw)


def main(argv: Optional[List[str]] = None) -> None:
    if not SEPOLIA_RPC_URL:
        fail({"ok": False, "error": "Missing SEPOLIA_RPC_URL in .env"})

    if not PRIVATE_KEY:
        fail({"ok": False, "error": "Missing PRIVATE_KEY in .env"})

    if not PRIVATE_KEY.startswith("0x"):
        # MetaMask often exports without 0x; add it if missing
        PRIVATE_KEY_FIXED = "0x" + PRIVATE_KEY
    else:
        PRIVATE_KEY_FIXED = PRIVATE_KEY

    # Update module-level for send_tx
    globals()["PRIVATE_KEY"] = PRIVATE_KEY_FIXED

    if not CONSUMER_ADDRESS_RAW:
        fail({"ok": False, "error": "Missing CONSUMER_ADDRESS in .env"})

    if not SUBSCRIPTION_ID_RAW:
        fail({"ok": False, "error": "Missing SUBSCRIPTION_ID in .env"})

    consumer_address = Web3.to_checksum_address(CONSUMER_ADDRESS_RAW)
    subscription_id = int(SUBSCRIPTION_ID_RAW)

    # Provider with timeout to reduce false negatives
    w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL, request_kwargs={"timeout": 30}))

    # More reliable than is_connected(): query chain id
    try:
        chain_id = w3.eth.chain_id
    except Exception as e:
        fail({"ok": False, "error": f"RPC not responding: {e}"})

    if chain_id != 11155111:
        fail({"ok": False, "error": f"Unexpected chain_id {chain_id}; expected 11155111 (Sepolia)"})

    acct = w3.eth.account.from_key(PRIVATE_KEY_FIXED)
    sender = acct.address

    contract = w3.eth.contract(address=consumer_address, abi=ABI)

    source_path = Path("functions/source.js")
    if not source_path.exists():
        fail({"ok": False, "error": "functions/source.js not found"})

    source = source_path.read_text(encoding="utf-8")

    # Args: optional CLI args after "--" (kept empty by default)
    args: List[str] = []
    if argv is None:
        argv = []
    if "--" in argv:
        i = argv.index("--")
        args = [str(a) for a in argv[i + 1 :]]

    fees = build_fees(w3)

    # 1) setSource
    try:
        nonce = w3.eth.get_transaction_count(sender)
        tx1 = contract.functions.setSource(source).build_transaction(
            {
                "from": sender,
                "nonce": nonce,
                "chainId": chain_id,
                "gas": 700_000,
                **fees,
            }
        )
        tx_hash1 = send_tx(w3, acct, tx1)
        receipt1 = wait_for_receipt(w3, tx_hash1)
        if receipt1.get("status") != 1:
            fail(
                {
                    "ok": False,
                    "stage": "setSource",
                    "txHash": tx_hash1.hex(),
                    "status": receipt1.get("status"),
                }
            )
    except ContractLogicError as e:
        fail({"ok": False, "stage": "setSource", "error": str(e)})
    except Exception as e:
        fail({"ok": False, "stage": "setSource", "error": str(e)})

    # 2) sendRequest
    try:
        nonce = w3.eth.get_transaction_count(sender)
        tx2 = contract.functions.sendRequest(subscription_id, args).build_transaction(
            {
                "from": sender,
                "nonce": nonce,
                "chainId": chain_id,
                "gas": 700_000,
                **fees,
            }
        )
        tx_hash2 = send_tx(w3, acct, tx2)
        receipt2 = wait_for_receipt(w3, tx_hash2)
        if receipt2.get("status") != 1:
            fail(
                {
                    "ok": False,
                    "stage": "sendRequest",
                    "txHash": tx_hash2.hex(),
                    "status": receipt2.get("status"),
                }
            )
    except ContractLogicError as e:
        fail({"ok": False, "stage": "sendRequest", "error": str(e)})
    except Exception as e:
        fail({"ok": False, "stage": "sendRequest", "error": str(e)})

    # 3) wait for Response event from consumer
    start_block = int(receipt2["blockNumber"])
    timeout_s = 10 * 60
    start_time = time.time()

    event_sig = w3.keccak(text="Response(bytes32,string,bytes)").hex()

    while True:
        if time.time() - start_time > timeout_s:
            fail(
                {
                    "ok": False,
                    "stage": "waitForResponse",
                    "txHash": tx_hash2.hex(),
                    "error": "Timed out waiting for Response event",
                }
            )

        latest = w3.eth.block_number
        try:
            logs = w3.eth.get_logs(
                {
                    "fromBlock": start_block,
                    "toBlock": latest,
                    "address": consumer_address,
                    "topics": [event_sig],
                }
            )
        except Exception:
            logs = []

        if logs:
            evt = contract.events.Response().process_log(logs[0])
            request_id = evt["args"]["requestId"].hex()
            response = evt["args"]["response"]
            err_bytes = evt["args"]["err"]

            if isinstance(err_bytes, (bytes, bytearray)):
                err_hex = "0x" + err_bytes.hex()
            else:
                err_hex = str(err_bytes)

            print(
                json.dumps(
                    {
                        "ok": err_hex in ("0x", "0x00", "0x0000") or err_hex == "0x",
                        "txHash": tx_hash2.hex(),
                        "requestId": request_id,
                        "response": response,
                        "err": err_hex,
                    }
                )
            )
            return

        time.sleep(3)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
