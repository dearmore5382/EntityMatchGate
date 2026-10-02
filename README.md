# EntityMatchGate v4

EntityMatchGate resolves whether one official GLEIF legal-entity record is the same as one exact OFAC historical candidate. A strong `DISTINCT_FROM_CANDIDATE` decision can activate a one-time on-chain permit that only a pre-named relying-party wallet can consume.

The v4 contract is deployed and lifecycle-verified on StudioNet at [`0xeC8dc7def8232b4fa1d8a0fF64354eDE88E76e2f`](https://explorer-studio.genlayer.com/address/0xeC8dc7def8232b4fa1d8a0fF64354eDE88E76e2f). The v4 interface is live at [entitymatchgate.pages.dev](https://entitymatchgate.pages.dev).

## Why v4 exists

The steward correctly identified three v3 limitations: applicant identity fields were self-asserted, the settled consequence was only a candidate-dismissal marker, and direct tests mocked the entire nondeterministic function. v4 addresses each limitation:

- The caller supplies identifiers only. Validators fetch legal name, registration identifier, jurisdiction, status, corroboration and revision from the official GLEIF API.
- Validators independently fetch the exact OFAC candidate. Both bounded records, revisions and SHA-256 digests are committed on-chain.
- A distinct decision does not itself grant anything. The requester must bind both source digests to activate an exact permit; only the independently named relying party may consume it, once.
- Direct tests call the public assessment entrypoint and execute both web fetches, the model call and validator re-execution. Only transport/model boundaries are deterministic test doubles.

## Proof boundary

**Claim:** at the committed GLEIF and OFAC source revisions, legal entity `L` is the same as, possibly related to, distinct from, or insufficiently evidenced against exact candidate `E`.

**Falsifier:** an exact registration-ID match defeats `DISTINCT`; a registration-ID or jurisdiction contradiction is required for `DISTINCT`; ambiguity produces `INSUFFICIENT_EVIDENCE`.

This contract does not provide current sanctions clearance, legal advice, wallet-to-company ownership proof, or global vendor approval.

## Roles and state machine

The deployer has no workflow privilege. Any wallet may become the requester, but it must name a different relying-party wallet. Assessment is permissionless.

```text
SOURCES_LOCKED
  -> SAME_ENTITY                       (no permit)
  -> POSSIBLE_MATCH                    (no permit)
  -> INSUFFICIENT_EVIDENCE             (retry, max 3)
  -> DISTINCT_FROM_CANDIDATE
       -> PERMIT_ACTIVE                (requester + exact source digests)
            -> PERMIT_CONSUMED         (named relying party, once)
```

## Sources

- GLEIF: `https://api.gleif.org/api/v1/lei-records/{lei}`
- OFAC: `https://sanctionslistservice.ofac.treas.gov/entities/{uid}`

Fetched content is untrusted input. The contract reduces it to bounded records before model input, validates exact output schema and semantic invariants, and requires validators to reproduce all consequential fields.

## Verify locally

```text
python -m pytest -q
npm run build
```

Expected current result: `6 passed` and a successful Vite production build. See `verification/STEWARD_RESPONSE_V4.md` for the reviewer-response matrix and `verification/E2E.md` for the finalized 11-transaction lifecycle.
