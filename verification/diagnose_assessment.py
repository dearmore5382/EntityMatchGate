"""Capture a finalized assessment receipt without printing wallet secrets."""
import json
import sys
from pathlib import Path

from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet

import run_live

values = {}
for line in run_live.KEY_SOURCE.read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.lstrip().startswith("#"):
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
if len(sys.argv) > 1:
    tx_hash = sys.argv[1]
    tx = run_live.rpc("eth_getTransactionByHash", [tx_hash])
else:
    secret = values["WALLET_B_PRIVATE_KEY"]
    account = create_account(account_private_key="0x" + secret.removeprefix("0x"))
    client = create_client(chain=studionet, account=account)
    tx_hash = str(client.write_contract(address=run_live.ADDRESS,
        function_name="assess_screening", args=[0], value=0, leader_only=False))
    tx = run_live.wait_final(tx_hash)
out = Path(__file__).with_name("assessment-diagnostic.json")
out.write_text(json.dumps({"tx_hash": tx_hash,
    "explorer": "https://explorer-studio.genlayer.com/tx/" + tx_hash,
    "status": tx.get("status"), "consensus": tx.get("result_name"),
    "consensus_data": tx.get("consensus_data")}, indent=2) + "\n", encoding="utf-8")
print(tx_hash, tx.get("status"), tx.get("result_name"), out)
