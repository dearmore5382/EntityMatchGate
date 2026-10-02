# Steward response — EntityMatchGate v4

The September 30 submission was not sufficient. Contract v3 compared an applicant-authored profile with OFAC, its terminal effect only marked one candidate dismissed, and its direct tests replaced the entire `_screen` function. The repository keeps the v3 receipts as historical evidence, but they do not prove v4.

## Changes mapped to the request

1. **Applicant facts are no longer self-asserted.** A requester supplies only a 20-character LEI and an OFAC entity UID. During assessment, validators fetch the exact legal-entity record from the official GLEIF API and the exact historical candidate from the official OFAC endpoint. The bounded bytes, source revisions, and SHA-256 digests are committed to contract state.
2. **The consequence is now an enforceable one-time authorization.** `DISTINCT_FROM_CANDIDATE` is only an assessment result. The original requester must re-bind both official-source digests to activate a permit. Only the independently named relying-party wallet can consume it, and it can be consumed once. Same, possible, insufficient, wrong-role, and commitment-mismatch paths never grant the permit.
3. **The nondeterministic path is exercised by tests.** `tests/test_contract_direct.py` mocks transport and model boundaries, not `_screen`. Tests call the public `assess_screening` entrypoint, execute both `gl.nondet.web.get` calls, execute `gl.nondet.exec_prompt`, and run `vm.run_validator()` to prove validator re-execution. Poisoned source data, malformed model output, source substitution, authorization, commitment mismatch, replay, and fail-closed outcomes are covered.

## Honest verification status

- Local contract tests: `6 passed` on 2026-10-02.
- Frontend production build: passed on 2026-10-02.
- New v4 StudioNet deployment: **verified** at `0xeC8dc7def8232b4fa1d8a0fF64354eDE88E76e2f`.
- v4 live lifecycle receipts and source parity: **verified**, 11 finalized `MAJORITY_AGREE` transactions, final state `PERMIT_CONSUMED`.
- Updated v4 Pages deployment: **verified** at `https://entitymatchgate.pages.dev` (immutable deployment `https://8ae1ebc5.entitymatchgate.pages.dev`). Both URLs returned HTTP 200 and their production bundle contains the v4 contract address, GLEIF flow and permit state.

The v4 source and evidence were pushed to GitHub at commit `45ba5b3`. Contract source parity, live source consensus, the consequential lifecycle, final readback, local adversarial suite and public Pages deployment are complete.
