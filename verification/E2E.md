# StudioNet E2E evidence

## Release identity

- Contract: [`0x3FAff7499A1eAC6100635267F594Ec6B0827Ee03`](https://explorer-studio.genlayer.com/address/0x3FAff7499A1eAC6100635267F594Ec6B0827Ee03)
- Schema: `candidate-specific-identity-review-v3`
- Local/deployed source SHA-256: `0cd9be11353c031fb20c2062dad3442e8bb5ab20a4bc4787e2b458e531341695`
- Source parity: `true`
- Applicant: `0x736A168247e3f0C52F7907c9a8fDac572DF9c8bB`
- Consumer: `0xA63DE24e30C88FB1019E8956654730316e36eDBE`

## Finalized matrix

| Path | Result | Transaction |
|---|---|---|
| Reject applicant as its own consumer | `INDEPENDENT_CONSUMER_REQUIRED` | [Explorer](https://explorer-studio.genlayer.com/tx/0xd2beb0025221e3e85aa5545df9813727efff130fc00634226aa3023596b34f56) |
| Open screening with independent consumer | screening `0` | [Explorer](https://explorer-studio.genlayer.com/tx/0x5a954ebbbe2ec7ce5927dd76eb8773cb347f0ad8b01755dab1f0d89e067524e5) |
| Reject wrong consumer | `CONSUMER_ONLY` | [Explorer](https://explorer-studio.genlayer.com/tx/0xc747a655180f96db2f06538913dae9d6c36997c2643032218bf65174a7c48f49) |
| Reject premature dismissal | `DISMISSAL_NOT_ALLOWED` | [Explorer](https://explorer-studio.genlayer.com/tx/0x8c02428ce19ee93810f746d9a016a1389262f1c69d69e95e9fffcf3b534ade60) |
| Permissionless GenLayer assessment | `DISTINCT_FROM_CANDIDATE`, `MAJORITY_AGREE` | [Explorer](https://explorer-studio.genlayer.com/tx/0x01b99130300f5ce8e24977420da6a0da70c9847f5f4fa5a90f83aa38dffb1a1a) |
| Reject terminal assessment replay | `SCREENING_NOT_ASSESSABLE` | [Explorer](https://explorer-studio.genlayer.com/tx/0x28f3da447e9f057a0fbbbc5e409197462eb5f389fe9778f6f7ca2c849b9cd454) |
| Reject wrong commitment | `COMMITMENT_MISMATCH` | [Explorer](https://explorer-studio.genlayer.com/tx/0x44b5c2370aaabf1b1dfc5b770b064d9f8b33541e5a6724890ac627de06885999) |
| Consumer dismisses exact candidate | `CANDIDATE_DISMISSED` | [Explorer](https://explorer-studio.genlayer.com/tx/0x39290454d819cb847881a0eb7da1957ea5e9981ee36cbf95b05a83df7c0f1887) |
| Reject dismissal replay | `DISMISSAL_NOT_ALLOWED` | [Explorer](https://explorer-studio.genlayer.com/tx/0x9ebecf0513b0da4074136b22485ca4070c26a5f1c7ff766e0edd10678d468dea) |

Every row finalized with `MAJORITY_AGREE`. The machine-readable receipt is `live-0x3faff7499a1eac6100635267f594ec6b0827ee03.json`.

## Authoritative final readback

- State: `CANDIDATE_DISMISSED`
- Relation: `DISTINCT_FROM_CANDIDATE`
- Candidate: OFAC entity `36`
- Stable source revision: `OFAC-ENTITY-36-e311b28b87e82288`
- Source digest: `e311b28b87e8228874cadd5acebc19448b6be75a762f059cf04ee1f2c8a65156`
- Assessment attempts: `1`
- Conflicting fields: `COUNTRY`, `NAME`

This evidence supports dismissal of this exact historical candidate only. It does not establish current sanctions clearance or global applicant approval.

## Extended conflict and adversarial matrix

The second live run uses the same official OFAC entity 36 and a name/alias-matching profile. It deliberately omits any published strong identifier, so the valid fail-closed outcome is `POSSIBLE_MATCH`, not `SAME_ENTITY`.

| Path | Result | Transaction |
|---|---|---|
| Reject malformed entry UID | `INVALID_ENTRY_UID` | [Explorer](https://explorer-studio.genlayer.com/tx/0x90be1a237e7fb0d075bf36cd7cb0a5be7221bc0e3ed04f245370124a2f5e77b3) |
| Reject malformed profile | `INVALID_PROFILE` | [Explorer](https://explorer-studio.genlayer.com/tx/0x97f76631ab227d1c902e3862c4aeeabf4a66994da0ceae2608fd91350c5c44b7) |
| Reject assessment of missing screening | `SCREENING_NOT_FOUND` | [Explorer](https://explorer-studio.genlayer.com/tx/0x0ade6380d1703dcddf9a8da1d164ed0035659f084e24c5818d82e7e886ce0c0e) |
| Reject dismissal of missing screening | `SCREENING_NOT_FOUND` | [Explorer](https://explorer-studio.genlayer.com/tx/0x6ebdc0e1406676c311ead2b6e4b683083b54f5d5a84df76da4e71d985a29db6a) |
| Open official-source name-match review | screening `1` | [Explorer](https://explorer-studio.genlayer.com/tx/0xd7f19efbaff2c31b57cf05bd0d932ce1c5698da1431568c09666481d5529b6e0) |
| Assess name/alias/country match without strong ID | `POSSIBLE_MATCH` | [Explorer](https://explorer-studio.genlayer.com/tx/0x21c0954b9a850dba095dfa7a9232586fea9834116990f3c8ef11737e266f889f) |
| Reject dismissal of possible match | `DISMISSAL_NOT_ALLOWED`, full readback unchanged | [Explorer](https://explorer-studio.genlayer.com/tx/0x2da165db89038998ca305436a1fd36624646f68a69b20d60477be972776f88ff) |
| Reject terminal assessment replay | `SCREENING_NOT_ASSESSABLE`, full readback unchanged | [Explorer](https://explorer-studio.genlayer.com/tx/0xb195e0ea437df0fb955fcc135c18537226a94f2b4d53881dabdcd3f6091c9d5b) |

All eight transactions finalized with `MAJORITY_AGREE`. The machine-readable receipt is `extended-live-0x3faff7499a1eac6100635267f594ec6b0827ee03.json`.

## UI-to-chain verification

The production build was exercised in a browser against the deployed contract after correcting the numeric `u256` screening-ID encoding.

- Screening `0` displayed `CANDIDATE_DISMISSED`, relation `DISTINCT_FROM_CANDIDATE`, UID `36`, attempts `1`, conflicts `COUNTRY, NAME`, and the exact on-chain source revision/digest.
- Screening `1` displayed `POSSIBLE_MATCH`, UID `36`, attempts `1`, matches `ALIAS, COUNTRY, NAME`, and the same exact source revision/digest.
- The candidate label now derives from authoritative `official_source`, and links to the exact OFAC record instead of reading a nonexistent response field.
- Action availability matched state: dismissal disabled for `CANDIDATE_DISMISSED` and `POSSIBLE_MATCH`; assessment disabled for both terminal states.

## Evidence-level boundary

- `DISTINCT_FROM_CANDIDATE`, `POSSIBLE_MATCH`, successful dismissal, role failures, malformed input, missing IDs, commitment tampering, and replay protection: verified live on StudioNet.
- `SAME_ENTITY`: regression-tested, but not claimed live for entity 36 because its official record contains no registration or birth/incorporation identifier. Fabricating one would violate the source-evidence rule.
- `INSUFFICIENT_EVIDENCE` retry cap: regression-tested for three attempts and fail-closed behavior. It is not mislabeled as live evidence.
