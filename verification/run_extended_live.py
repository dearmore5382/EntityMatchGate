"""Extended StudioNet matrix using only official live OFAC evidence."""
import json
from pathlib import Path

import run_live
from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet

OUT = Path(__file__).with_name("extended-live-" + run_live.ADDRESS.lower() + ".json")


def main():
    keys = run_live.load_keys()
    accounts = [create_account(account_private_key="0x" + key.removeprefix("0x")) for key in keys]
    clients = [create_client(chain=studionet, account=account) for account in accounts]
    journal = {"network": "studionet", "contract": run_live.ADDRESS,
        "official_source": "https://sanctionslistservice.ofac.treas.gov/entities/36",
        "steps": [], "complete": False}

    def send(step, actor, method, args, expected, target=None, unchanged=False):
        before = None if target is None else run_live.view("get_screening", [target])
        tx_hash = str(clients[actor].write_contract(address=run_live.ADDRESS,
            function_name=method, args=args, value=0, leader_only=False))
        tx = run_live.wait_final(tx_hash)
        actual = run_live.tx_return(tx)
        after = None if target is None else run_live.view("get_screening", [target])
        entry = {"id": step, "method": method, "return": actual, "expected": expected,
            "tx_hash": tx_hash, "explorer": "https://explorer-studio.genlayer.com/tx/" + tx_hash,
            "status": tx.get("status"), "consensus": tx.get("result_name"),
            "state_unchanged": None if not unchanged else before == after,
            "readback": None if after is None else json.loads(after)}
        journal["steps"].append(entry)
        OUT.write_text(json.dumps(journal, indent=2) + "\n", encoding="utf-8")
        if tx.get("result_name") != "MAJORITY_AGREE" or actual != expected:
            raise RuntimeError(step + ":UNEXPECTED:" + actual)
        if unchanged and before != after:
            raise RuntimeError(step + ":STATE_MUTATED")
        return actual

    start = json.loads(run_live.view("get_counts"))["screening_count"]
    send("A1-invalid-entry-uid", 0, "open_screening", [accounts[1].address, "{}", "bad uid"], "INVALID_ENTRY_UID")
    send("A2-invalid-profile", 0, "open_screening", [accounts[1].address, "{}", "36"], "INVALID_PROFILE")
    send("A3-assess-missing", 0, "assess_screening", [999999], "SCREENING_NOT_FOUND")
    send("A4-dismiss-missing", 1, "dismiss_candidate", [999999, "x", "y", "z"], "SCREENING_NOT_FOUND")

    profile = json.dumps({"schema": "entity-profile-v1", "profile_ref": "EMG-POSSIBLE-2026-001",
        "legal_name": "AEROCARIBBEAN AIRLINES", "aliases": ["AERO-CARIBBEAN"],
        "country": "Cuba", "registration_id": "NOT-PUBLISHED",
        "birth_or_incorporation": "NOT-PUBLISHED"}, separators=(",", ":"))
    screening_id = int(send("C1-open-name-match", 0, "open_screening",
        [accounts[1].address, profile, "36"], str(start)))
    send("C2-assess-name-match", 1, "assess_screening", [screening_id], "POSSIBLE_MATCH", screening_id)
    record = json.loads(run_live.view("get_screening", [screening_id]))
    send("C3-fail-closed-possible", 1, "dismiss_candidate",
        [screening_id, record["profile_digest"], record["source_digest"], record["source_revision"]],
        "DISMISSAL_NOT_ALLOWED", screening_id, unchanged=True)
    send("A5-terminal-assessment-replay", 0, "assess_screening", [screening_id],
        "SCREENING_NOT_ASSESSABLE", screening_id, unchanged=True)

    journal["final_readback"] = json.loads(run_live.view("get_screening", [screening_id]))
    journal["complete"] = (journal["final_readback"]["state"] == "POSSIBLE_MATCH" and
        all(x["status"] == "FINALIZED" and x["consensus"] == "MAJORITY_AGREE" for x in journal["steps"]) and
        all(x["state_unchanged"] is not False for x in journal["steps"]))
    OUT.write_text(json.dumps(journal, indent=2) + "\n", encoding="utf-8")
    print("EXTENDED_E2E_COMPLETE" if journal["complete"] else "EXTENDED_E2E_INCOMPLETE", OUT)


if __name__ == "__main__":
    main()
