# EntityMatchGate v4 — live StudioNet evidence

Verified on 2026-10-02 against contract [`0xeC8d…6e2f`](https://explorer-studio.genlayer.com/address/0xeC8dc7def8232b4fa1d8a0fF64354eDE88E76e2f).

## Integrity and roles

- Deployed source equals `contracts/EntityMatchGate.py` byte-for-byte.
- SHA-256: `9c7f62b64530bc57b6d4ad7913311b5b468ba56c012960ab58cfe54883e48932`.
- Requester: `0x736A168247e3f0C52F7907c9a8fDac572DF9c8bB`.
- Relying party: `0xA63DE24e30C88FB1019E8956654730316e36eDBE`.
- Independent identity source: GLEIF LEI `5493001KJTIIGC8Y1R12`, Golden Copy revision `2026-10-01T16:00:00Z`, committed digest `05e3c41b…610d9`.
- Exact historical candidate: OFAC entity `36`, committed digest `e311b28b…5156`.

## Finalized lifecycle

| Path | Result | Transaction |
|---|---|---|
| Reject same requester/relying-party | `INDEPENDENT_RELYING_PARTY_REQUIRED` | [0x0fd5…93d8](https://explorer-studio.genlayer.com/tx/0x0fd5a0e8066da462a420ab61bb61c9165e93b588d57ab52cbf2216d2d83b93d8) |
| Open screening 1 | `1` | [0x0397…9e27](https://explorer-studio.genlayer.com/tx/0x03976c5e2fe627f05898c7b35abb2f971ef2cf71dd2117031c82639f95a29e27) |
| Block premature permit | `PERMIT_NOT_ALLOWED` | [0x2d99…95e9](https://explorer-studio.genlayer.com/tx/0x2d99f3a25525c1732e96efc3caa1945b65af8de656d69e63222ffeca5e3995e9) |
| Permissionless live GLEIF↔OFAC assessment | `DISTINCT_FROM_CANDIDATE` | [0xbb18…a8c8](https://explorer-studio.genlayer.com/tx/0xbb18d34a5351cd6662917b8974ee8c6de6d62e1b5fd506f5a2ef9e02d062a8c8) |
| Reject assessment replay | `SCREENING_NOT_ASSESSABLE` | [0x11b8…7d71](https://explorer-studio.genlayer.com/tx/0x11b8aa96abe2c78f3a590dffd81e2a1b19f0671b73e0e60f214ab24c91037d71) |
| Reject activation by relying party | `REQUESTER_ONLY` | [0x6ecd…1085](https://explorer-studio.genlayer.com/tx/0x6ecd0d6a153481f27f28d2aeb6719ffb32fd8a33d2f45dc8c35b3b462bf71085) |
| Reject substituted GLEIF digest | `COMMITMENT_MISMATCH` | [0x8e69…6ca6](https://explorer-studio.genlayer.com/tx/0x8e69e2e4037a05d3bb3cc7cd6de613fc4e7177e9fa0adba1363021ed6d356ca6) |
| Activate one-time permit | `PERMIT_ACTIVE` | [0xd62c…707f](https://explorer-studio.genlayer.com/tx/0xd62c9f49fc4c72f65ad383e5f6e5199eae81d7b971281c0601d20066304e707f) |
| Reject consumption by requester | `RELYING_PARTY_ONLY` | [0x356e…0088](https://explorer-studio.genlayer.com/tx/0x356e4862bde6d8c135617f6b7f21b39a77e7f5aa649bc3c48ae380a668970088) |
| Consume by named relying party | `PERMIT_CONSUMED` | [0xe245…2d47](https://explorer-studio.genlayer.com/tx/0xe245170c419f7ff8cf0613d2032825fc792d01a4de2843b5d7bc8803f0782d47) |
| Reject consumption replay | `NO_ACTIVE_PERMIT` | [0xb352…26c7](https://explorer-studio.genlayer.com/tx/0xb3529f612b9650f43831a33c0dbd024b59c86b7a7c1c0cbabe8957fd93cb26c7) |

All 11 transactions are `FINALIZED` with `MAJORITY_AGREE`. Final authoritative readback for screening 1 is `PERMIT_CONSUMED`, and `permit_consumer` equals the named relying-party wallet.

## Adversarial test boundary

The live matrix proves real official-source consensus and the consequential two-wallet lifecycle. The direct suite separately exercises poisoned source text, malformed model output, substituted source schema, decision invariants, wrong roles, wrong commitments and replay. It calls the public nondeterministic entrypoint and `vm.run_validator()`; it does not replace `_screen`.

Machine-readable receipts: [`live-0xec8d…json`](live-0xec8dc7def8232b4fa1d8a0ff64354ede88e76e2f.json).
