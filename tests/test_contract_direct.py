from pathlib import Path
import importlib
import json
import sys
from unittest.mock import patch

from gltest.direct import VMContext, create_address, deploy_contract

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "EntityMatchGate.py"


def eth(value):
    if isinstance(value, bytes):
        return "0x" + bytes(value).hex()
    text = str(value)
    return "0x" + text[5:] if text.startswith("addr#") else text


def profile(ref="VENDOR-1"):
    return json.dumps({"schema": "entity-profile-v1", "profile_ref": ref,
        "legal_name": "Northstar Industrial Trading Ltd", "aliases": ["Northstar Trading"],
        "country": "Singapore", "registration_id": "SG-201912345N",
        "birth_or_incorporation": "2019-04-18"}, separators=(",", ":"))


def deploy():
    deployer, applicant, consumer, outsider = [create_address(x) for x in ("deployer", "applicant", "consumer", "outsider")]
    vm = VMContext(deployer)
    with patch("os.unlink", lambda _path: None), vm.activate():
        contract = deploy_contract(CONTRACT, vm)
        proxy = contract._instance.open_screening.__globals__["gl"]
        _ = proxy.nondet
        _ = proxy.vm
    sdk_root = str(Path(proxy._cached_gl.__file__).resolve().parents[2])
    if sdk_root not in sys.path:
        sys.path.insert(0, sdk_root)
    importlib.import_module("genlayer")
    return vm, contract, deployer, applicant, consumer, outsider


def sync(vm, contract):
    proxy = contract._instance.open_screening.__globals__["gl"]
    sender = vm.sender
    if isinstance(sender, bytes):
        sender = type(proxy.message.sender_address)(sender)
    proxy._cached_gl.message = proxy.message._replace(sender_address=sender, origin_address=sender,
        value=type(proxy.message.value)(vm.value))
    proxy._cached_gl.message_raw["sender_address"] = sender
    proxy._cached_gl.message_raw["origin_address"] = sender


def open_as(vm, contract, applicant, consumer):
    with vm.prank(applicant):
        sync(vm, contract)
        return contract.open_screening(eth(consumer), profile(), "OFAC-UID-123")


def assess_as(vm, contract, screening_id, sender, decision):
    module = contract._instance.open_screening.__globals__
    with vm.prank(sender), patch.dict(module, {"_screen": lambda *_: decision}):
        sync(vm, contract)
        return contract.assess_screening(screening_id)


def test_two_wallet_happy_path_is_open_to_reviewers():
    vm, contract, _, applicant, consumer, outsider = deploy()
    screening_id = open_as(vm, contract, applicant, consumer)
    decision = {"relation": "DISTINCT_FROM_CANDIDATE", "official_entry_uid": "OFAC-UID-123",
        "source_revision": "2026-09-30T00:00:00Z", "source_digest": "d" * 64, "matched_fields": ["COUNTRY"],
        "conflicting_fields": ["REGISTRATION_ID"]}
    assert assess_as(vm, contract, screening_id, outsider, decision) == "DISTINCT_FROM_CANDIDATE"
    record = json.loads(contract.get_screening(screening_id))
    with vm.prank(consumer):
        sync(vm, contract)
        assert contract.dismiss_candidate(screening_id, record["profile_digest"], record["source_digest"], record["source_revision"]) == "CANDIDATE_DISMISSED"
    assert json.loads(contract.get_screening(screening_id))["state"] == "CANDIDATE_DISMISSED"


def test_potential_match_fails_closed():
    vm, contract, _, applicant, consumer, outsider = deploy()
    screening_id = open_as(vm, contract, applicant, consumer)
    decision = {"relation": "SAME_ENTITY", "official_entry_uid": "OFAC-UID-123",
        "source_revision": "rev-1", "source_digest": "d" * 64, "matched_fields": ["REGISTRATION_ID"], "conflicting_fields": []}
    assert assess_as(vm, contract, screening_id, outsider, decision) == "SAME_ENTITY"
    with vm.prank(consumer):
        sync(vm, contract)
        assert contract.dismiss_candidate(screening_id, "x", "y", "z") == "DISMISSAL_NOT_ALLOWED"


def test_same_wallet_and_unauthorized_activation_rejected():
    vm, contract, _, applicant, consumer, outsider = deploy()
    with vm.prank(applicant):
        sync(vm, contract)
        assert contract.open_screening(eth(applicant), profile(), "OFAC-UID-123") == "INDEPENDENT_CONSUMER_REQUIRED"
    screening_id = open_as(vm, contract, applicant, consumer)
    decision = {"relation": "DISTINCT_FROM_CANDIDATE", "official_entry_uid": "OFAC-UID-123",
        "source_revision": "rev-1", "source_digest": "d" * 64, "matched_fields": [], "conflicting_fields": ["COUNTRY"]}
    assess_as(vm, contract, screening_id, outsider, decision)
    before = contract.get_screening(screening_id)
    with vm.prank(outsider):
        sync(vm, contract)
        assert contract.dismiss_candidate(screening_id, "x", "y", "z") == "CONSUMER_ONLY"
    assert contract.get_screening(screening_id) == before


def test_replay_and_invalid_input_are_rejected():
    vm, contract, _, applicant, consumer, outsider = deploy()
    screening_id = open_as(vm, contract, applicant, consumer)
    decision = {"relation": "INSUFFICIENT_EVIDENCE", "official_entry_uid": "OFAC-UID-123",
        "source_revision": "rev-1", "source_digest": "d" * 64, "matched_fields": [], "conflicting_fields": []}
    assert assess_as(vm, contract, screening_id, outsider, decision) == "INSUFFICIENT_EVIDENCE"
    assert assess_as(vm, contract, screening_id, outsider, decision) == "INSUFFICIENT_EVIDENCE"
    with vm.prank(applicant):
        sync(vm, contract)
        assert contract.open_screening(eth(consumer), "{}", "OFAC-UID-123") == "INVALID_PROFILE"


def test_decision_schema_rejects_weak_and_unbounded_outputs():
    module = deploy()[1]._instance.open_screening.__globals__
    valid = {"relation": "SAME_ENTITY", "matched_fields": ["REGISTRATION_ID"], "conflicting_fields": []}
    assert module["_decision"](valid, "UID", "rev", "d" * 64)["relation"] == "SAME_ENTITY"
    invalid = [
        {**valid, "matched_fields": ["NAME"]},
        {**valid, "relation": "DISTINCT_FROM_CANDIDATE", "matched_fields": [], "conflicting_fields": []},
        {**valid, "relation": "CLEAR"},
    ]
    for value in invalid:
        try:
            module["_decision"](value, "UID", "rev", "d" * 64)
            assert False
        except Exception:
            pass


def test_manifest_separates_live_source_from_fixtures():
    manifest = json.loads((ROOT / "verification" / "TEST_RESOURCE_MANIFEST.json").read_text())
    assert manifest["authoritative_source"]["dynamic"] is True
    assert all(item["kind"] in ("synthetic", "template") for item in manifest["local_fixtures"])


def test_official_xml_is_bounded_to_stable_entity_before_model_input():
    source = CONTRACT.read_text(encoding="ascii")
    assert 'source.find("<publicationInfo>")' not in source
    assert 'source.find("<dataAsOf>")' not in source
    assert 'source.find("<entities>")' in source
    assert 'source.find("<entities>")' in source
    assert "bounded_source" in source
    assert "ENTITY_RECORD_TOO_LARGE" in source


def test_commitment_mismatch_and_terminal_replay_do_not_mutate():
    vm, contract, _, applicant, consumer, outsider = deploy()
    screening_id = open_as(vm, contract, applicant, consumer)
    decision = {"relation": "DISTINCT_FROM_CANDIDATE", "official_entry_uid": "OFAC-UID-123",
        "source_revision": "rev-1", "source_digest": "d" * 64,
        "matched_fields": [], "conflicting_fields": ["REGISTRATION_ID"]}
    assess_as(vm, contract, screening_id, outsider, decision)
    record = json.loads(contract.get_screening(screening_id))
    with vm.prank(consumer):
        sync(vm, contract)
        before = contract.get_screening(screening_id)
        assert contract.dismiss_candidate(screening_id, "0" * 64, record["source_digest"], record["source_revision"]) == "COMMITMENT_MISMATCH"
        assert contract.get_screening(screening_id) == before
        assert contract.dismiss_candidate(screening_id, record["profile_digest"], record["source_digest"], record["source_revision"]) == "CANDIDATE_DISMISSED"
        terminal = contract.get_screening(screening_id)
        assert contract.dismiss_candidate(screening_id, record["profile_digest"], record["source_digest"], record["source_revision"]) == "DISMISSAL_NOT_ALLOWED"
        assert contract.get_screening(screening_id) == terminal


def test_insufficient_retry_is_bounded_and_never_positive():
    vm, contract, _, applicant, consumer, outsider = deploy()
    screening_id = open_as(vm, contract, applicant, consumer)
    decision = {"relation": "INSUFFICIENT_EVIDENCE", "official_entry_uid": "OFAC-UID-123",
        "source_revision": "rev-1", "source_digest": "d" * 64,
        "matched_fields": [], "conflicting_fields": []}
    for _ in range(3):
        assert assess_as(vm, contract, screening_id, outsider, decision) == "INSUFFICIENT_EVIDENCE"
    before = contract.get_screening(screening_id)
    assert assess_as(vm, contract, screening_id, outsider, decision) == "ATTEMPT_LIMIT_REACHED"
    assert contract.get_screening(screening_id) == before
    with vm.prank(consumer):
        sync(vm, contract)
        assert contract.dismiss_candidate(screening_id, "d" * 64, "d" * 64, "rev-1") == "DISMISSAL_NOT_ALLOWED"
