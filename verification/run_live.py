"""StudioNet E2E runner. Wallet secrets are loaded from an external ignored file."""
import base64
import hashlib
import json
import os
import time
from pathlib import Path

import requests
from genlayer_py import create_account, create_client
from genlayer_py.abi import calldata
from genlayer_py.abi.transactions import serialize
from genlayer_py.chains import studionet

ROOT = Path(__file__).resolve().parents[1]
ADDRESS = "0xeC8dc7def8232b4fa1d8a0fF64354eDE88E76e2f"
RPC = "https://studio.genlayer.com/api"
KEY_SOURCE = ROOT.parent / "DAOProposalContextVerifier" / ".env.lifecycle"
OUT = ROOT / "verification" / ("live-" + ADDRESS.lower() + ".json")


def rpc(method, params):
    response = requests.post(RPC, json={"jsonrpc": "2.0", "id": 1,
        "method": method, "params": params}, timeout=120)
    response.raise_for_status()
    payload = response.json()
    if "error" in payload:
        raise RuntimeError(str(payload["error"]))
    return payload["result"]


def view(method, args=None):
    encoded = serialize([calldata.encode({"method": method, "args": args or []}), b"\x00"])
    raw = rpc("gen_call", [{"type": "read", "to": ADDRESS,
        "from": "0x0000000000000000000000000000000000000001", "value": "0x0",
        "data": encoded, "transaction_hash_variant": "latest-final"}])
    return str(calldata.decode(bytes.fromhex(raw.removeprefix("0x"))))


def wait_final(tx_hash):
    deadline = time.monotonic() + 1500
    while time.monotonic() < deadline:
        tx = rpc("eth_getTransactionByHash", [tx_hash])
        if tx and tx.get("status") == "FINALIZED":
            return tx
        time.sleep(5)
    raise RuntimeError("FINALITY_TIMEOUT")


def tx_return(tx):
    receipts = (tx.get("consensus_data") or {}).get("leader_receipt") or []
    receipts = [receipts] if isinstance(receipts, dict) else receipts
    leaders = [item for item in receipts if item.get("mode") == "leader"]
    if not leaders or leaders[-1].get("execution_result") != "SUCCESS":
        raise RuntimeError("LEADER_EXECUTION_FAILED")
    result = leaders[-1].get("result")
    raw = base64.b64decode(result["raw"] if isinstance(result, dict) else result)
    if not raw or raw[0] != 0:
        raise RuntimeError("CONTRACT_EXECUTION_ERROR")
    return str(calldata.decode(raw[1:]))


def load_keys():
    values = {}
    for line in KEY_SOURCE.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    keys = [values.get("WALLET_A_PRIVATE_KEY"), values.get("WALLET_B_PRIVATE_KEY")]
    if not all(keys):
        raise RuntimeError("TWO_LOCAL_ROLE_KEYS_REQUIRED")
    return keys


def main():
    local = (ROOT / "contracts" / "EntityMatchGate.py").read_bytes()
    deployed = base64.b64decode(rpc("gen_getContractCode", [ADDRESS]))
    if deployed != local:
        raise RuntimeError("SOURCE_PARITY_FAILED")
    accounts = [create_account(account_private_key="0x" + key.removeprefix("0x")) for key in load_keys()]
    clients = [create_client(chain=studionet, account=account) for account in accounts]
    journal = {"network": "studionet", "contract": ADDRESS,
        "source_sha256": hashlib.sha256(local).hexdigest(), "source_parity": True,
        "official_sources": ["https://api.gleif.org/api/v1/lei-records/{lei}",
            "https://sanctionslistservice.ofac.treas.gov/entities/{entity_uid}"],
        "roles": {"requester": accounts[0].address, "relying_party": accounts[1].address},
        "steps": [], "complete": False}

    def send(step_id, actor, method, args, expected, screening_id=None):
        tx_hash = str(clients[actor].write_contract(address=ADDRESS, function_name=method,
            args=args, value=0, leader_only=False))
        tx = wait_final(tx_hash)
        actual = tx_return(tx)
        allowed = expected if isinstance(expected, tuple) else (expected,)
        readback = None if screening_id is None else view("get_screening", [screening_id])
        entry = {"id": step_id, "actor": accounts[actor].address, "method": method,
            "args": args, "return": actual, "expected": list(allowed), "tx_hash": tx_hash,
            "explorer": "https://explorer-studio.genlayer.com/tx/" + tx_hash,
            "status": tx.get("status"), "consensus": tx.get("result_name"),
            "readback": json.loads(readback) if readback and readback.startswith("{") else readback}
        journal["steps"].append(entry)
        OUT.write_text(json.dumps(journal, indent=2) + "\n", encoding="utf-8")
        if tx.get("result_name") != "MAJORITY_AGREE" or actual not in allowed:
            raise RuntimeError(step_id + ":UNEXPECTED:" + actual)
        return actual

    lei = "5493001KJTIIGC8Y1R12"
    start = json.loads(view("get_counts"))["screening_count"]
    send("F1-same-wallet-relying-party", 0, "open_screening",
        [accounts[0].address, lei, "36"], "INDEPENDENT_RELYING_PARTY_REQUIRED")
    screening_id = int(send("H1-open-screening", 0, "open_screening",
        [accounts[1].address, lei, "36"], str(start)))
    send("F2-premature-permit", 0, "activate_permit", [screening_id, "0" * 64, "0" * 64],
        "PERMIT_NOT_ALLOWED", screening_id)
    relation = send("H2-permissionless-assessment", 1, "assess_screening", [screening_id],
        "DISTINCT_FROM_CANDIDATE", screening_id)
    send("F3-replay-assessment", 0, "assess_screening", [screening_id], "SCREENING_NOT_ASSESSABLE", screening_id)
    if relation == "DISTINCT_FROM_CANDIDATE":
        record = json.loads(view("get_screening", [screening_id]))
        send("F4-wrong-requester", 1, "activate_permit", [screening_id, record["gleif_digest"], record["ofac_digest"]], "REQUESTER_ONLY", screening_id)
        send("F5-wrong-commitment", 0, "activate_permit", [screening_id, "0" * 64, record["ofac_digest"]], "COMMITMENT_MISMATCH", screening_id)
        send("H3-activate-permit", 0, "activate_permit", [screening_id, record["gleif_digest"], record["ofac_digest"]], "PERMIT_ACTIVE", screening_id)
        send("F6-wrong-consumer", 0, "consume_permit", [screening_id], "RELYING_PARTY_ONLY", screening_id)
        send("H4-consume-permit", 1, "consume_permit", [screening_id], "PERMIT_CONSUMED", screening_id)
        send("F7-replay-consumption", 1, "consume_permit", [screening_id], "NO_ACTIVE_PERMIT", screening_id)
    journal["final_screening"] = json.loads(view("get_screening", [screening_id]))
    journal["complete"] = relation == "DISTINCT_FROM_CANDIDATE" and journal["final_screening"]["state"] == "PERMIT_CONSUMED"
    OUT.write_text(json.dumps(journal, indent=2) + "\n", encoding="utf-8")
    print("E2E_COMPLETE" if journal["complete"] else "E2E_REVIEW", OUT)


if __name__ == "__main__":
    main()
