# Rule audit — candidate-specific identity review v3

## Proof obligation

- Claim: relation of one locked profile to one exact historical OFAC candidate and revision.
- Positive effect: dismiss only that candidate review.
- Explicitly not claimed: global vendor clearance, active sanctions screening, legal compliance, wallet ownership.

## Ground-truth map

| Fact | Authority | Binding | Consequential |
|---|---|---|---|
| Profile | applicant transaction sender | canonical JSON + stored SHA-256 | yes |
| Candidate | OFAC `/entities/{uid}` | exact UID in path and XML | yes |
| Revision | exact entity content | UID plus entity-digest prefix | yes |
| Source bytes | OFAC entity record | bounded `<entities>` bytes + computed SHA-256 | yes |
| Semantic relation | independent GenLayer validator observation | exact bounded enum | yes |
| Consumer | applicant nomination | sender-enforced and distinct | yes |

## Consensus boundary

- AI returns only relation and bounded field categories.
- Contract supplies UID, stable entity-content revision and digest deterministically; volatile response-generation timestamps are excluded.
- Validator independently refetches and reassesses.
- Exact equality applies only to consequential UID, revision, digest and enum.
- Diagnostics cannot grant candidate dismissal.

## Failure and liveness

- Source/model/consensus failure rolls back and grants no effect.
- `INSUFFICIENT_EVIDENCE` permits retry but never dismissal.
- Retry count is capped at three.
- Other semantic terminal outcomes are not replayable.
- Candidate dismissal is single-use and exact-commitment bound.

## Regression evidence

- Same applicant/consumer rejected.
- Wrong consumer rejected with complete readback unchanged.
- Premature dismissal rejected.
- Wrong profile/source/revision commitment rejected with complete readback unchanged.
- Same/possible/insufficient cannot dismiss.
- Terminal dismissal replay rejected with complete readback unchanged.
- Insufficient retry cap enforced with complete readback unchanged.
- Model output schema and cross-field invariants enforced.
- Official XML is reduced to publication and entity sections before model input.

## Release gate

Local tests prove contract behavior only. Release remains blocked until a fresh v3 deployment passes exact source parity and a finalized StudioNet two-wallet lifecycle with authoritative pre/post readbacks.
