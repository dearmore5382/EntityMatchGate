# EntityMatchGate

EntityMatchGate compares one immutable applicant profile with one exact OFAC historical entity record. A separately named consumer may dismiss only that candidate after validators conclude `DISTINCT_FROM_CANDIDATE`.

It does **not** provide active sanctions clearance, certify a vendor, or prove absence from the full OFAC list.

## Proof obligation

**Claim:** Profile `P` is the same as, possibly related to, distinct from, or insufficiently evidenced against exact candidate `E` at revision `R`.

**Falsifier:** A strong identifier match falsifies distinct; a material identity conflict falsifies same; missing or ambiguous evidence prevents either conclusion.

**Evidence:** The locked canonical profile plus the bounded entity record returned by OFAC `/entities/{uid}`. Volatile response-generation metadata such as `dataAsOf` is deliberately excluded from consensus commitments.

**Boundary:** This establishes only the relationship between `P` and `E`. OFAC warns that this endpoint may contain historical data and is not active transaction-screening clearance.

## Authority separation

- OFAC endpoint: source bytes, entity UID and publication revision.
- GenLayer validators: semantic relation between the locked profile and candidate.
- Contract: sender roles, canonical profile, SHA-256 commitments, retry bound, replay protection and last-mile consumption.
- Frontend: non-authoritative client and readback surface.

The deployer has no workflow privilege. Wallet A opens a review and nominates a different Wallet B. Assessment is permissionless. Only Wallet B can dismiss a distinct candidate after resupplying the exact profile digest, source digest and source revision.

## State machine

```text
PROFILE_LOCKED
  -> SAME_ENTITY
  -> POSSIBLE_MATCH
  -> DISTINCT_FROM_CANDIDATE -> CANDIDATE_DISMISSED
  -> INSUFFICIENT_EVIDENCE -> retry, maximum three attempts
```

Other outcomes, source/model failure, and exhausted retries never grant dismissal. Rejected calls must leave authoritative state unchanged.

## Consensus boundary

Leader and validators independently fetch and assess the bounded entity evidence. Exact agreement is required for consequential fields: candidate UID, stable entity-content revision, entity digest and relation enum. Volatile response timestamps are excluded because they differ across validator fetches. Diagnostics do not authorize dismissal. Deterministic checks require a strong identifier for `SAME_ENTITY`, a name/alias signal for `POSSIBLE_MATCH`, and a conflict for `DISTINCT_FROM_CANDIDATE`.

## Reviewer path

Verified StudioNet v3 contract: [`0x3FAff7499A1eAC6100635267F594Ec6B0827Ee03`](https://explorer-studio.genlayer.com/address/0x3FAff7499A1eAC6100635267F594Ec6B0827Ee03).

The deployed bytes match `contracts/EntityMatchGate.py` at SHA-256 `0cd9be11353c031fb20c2062dad3442e8bb5ab20a4bc4787e2b458e531341695`. The recorded two-wallet lifecycle reached `CANDIDATE_DISMISSED`; see `verification/E2E.md` and the machine-readable live receipt.

1. Open the DApp and connect any funded StudioNet wallet as applicant.
2. Open a review with a different wallet as consumer and an exact OFAC entity UID.
3. Run assessment and wait for finalized consensus plus authoritative readback.
4. If `DISTINCT_FROM_CANDIDATE`, switch to the nominated consumer and dismiss the exact candidate.
5. Verify transaction hashes and final readback in Studio Explorer.

## Verification

```text
python -m pytest -q
genvm-lint contracts/EntityMatchGate.py
npm run build
```

Local model outputs are synthetic and prove only contract behavior. The checked-in live receipt records source parity, finalized hashes, consensus results and authoritative readbacks. Superseded deployments are retained transparently but must not be submitted as final.
