# ClaimAnchor live Studionet evidence

Network: GenLayer Studionet (`61999`)

Contract: [`0x902365aFBc441aE06f249F5ff39a4928F3827Ee2`](https://explorer-studio.genlayer.com/address/0x902365aFBc441aE06f249F5ff39a4928F3827Ee2)

Schema readback: `{"name":"ClaimAnchor","schema":"optimistic-citation-challenge-v1","version":1}`

## Run

- Run ID: `muaparlu`
- Publisher: `0xeb57bc7125fa60d7482ce12058397369ab3581f8`
- Permissionless challenger: `0x2da5393d7bbb9a037dc3abb56dbbc5c150fc843f`
- [Commit-pinned publisher source](https://raw.githubusercontent.com/eaglebooth/PatchProof/086c4ee10aca8fb208fcb0f7455239ee3f17efb3/docs/LIVE_STUDIONET_EVIDENCE.md), SHA-256 `a3190e5d0275725016eb103120c9f5158e038b336c5763bcac0d49c6a66283b5`
- [Repository-separated counter-source](https://raw.githubusercontent.com/eaglebooth/ForkRight/011fd33fbe6aa1fde66c8489c6ca3c7b282d6e36/docs/patchproof-independent-verification.md), SHA-256 `3b08705cb8bdb358262a83b95302f2b2728e27943916a805e11f3718cf7fcc23`

The evidence is explicitly synthetic. The run intentionally publishes one bounded statement that preserves that scope and one misleading statement that invents production exploitation and customer losses.

## Finalized transaction ledger

| Transition | Explorer | GenVM | Outcome |
|---|---|---|---|
| Publish bounded claim | [`0x12127c4e…2837`](https://explorer-studio.genlayer.com/tx/0x12127c4e89c7fbf304d3a05fc5ccf34b9d233896d7b81720c4f45edc5b152837) | SUCCESS | Publisher-scoped claim anchored |
| Duplicate claim | [`0x8aaecdb3…ccfe`](https://explorer-studio.genlayer.com/tx/0x8aaecdb349919610541ab20fd8c163e9e67ff05a4578a924ad943a9dac44ccfe) | ERROR | Duplicate ID rejected |
| Publisher challenges itself | [`0x39ccb194…a449`](https://explorer-studio.genlayer.com/tx/0x39ccb194d0fd824687a2caf56890ca169f524c8488142e5a6ecb1b9bba57a449) | ERROR | Self-challenge rejected |
| Repository-separated challenge | [`0xe49309a8…0734`](https://explorer-studio.genlayer.com/tx/0xe49309a87806ff6c9828551cf06f0bafffdac7d1746c7f30cbd35b64b7490734) | SUCCESS | Challenger sender and counter-source recorded |
| Resolve bounded claim | [`0x042300e0…56f5`](https://explorer-studio.genlayer.com/tx/0x042300e0156375e55c66151e31b4d51e454e4330e8938cfa4e8cd4794fdf56f5) | SUCCESS | Consensus ruling `SUPPORTED` |
| Resolve a second time | [`0x0027fc4d…36da`](https://explorer-studio.genlayer.com/tx/0x0027fc4dcce95f6e0c2756c4e04c559c1762e2d6199a860d3882d761ba1036da) | ERROR | Finalized ruling cannot replay |
| Challenge after final ruling | [`0xcdc6dfc4…cc66`](https://explorer-studio.genlayer.com/tx/0xcdc6dfc415ce32f90623f863d7c09119fe5220d63d926bfc765625dfce19cc66) | ERROR | Resolved claim cannot be replaced |
| Publish misleading claim | [`0x663fc8a6…9a1b`](https://explorer-studio.genlayer.com/tx/0x663fc8a6ca929bd89f4dde59e4061adb2a424f74fba9ef2bc61410b8bb989a1b) | SUCCESS | Adversarial claim anchored |
| Challenge misleading claim | [`0xf8e545f6…9559`](https://explorer-studio.genlayer.com/tx/0xf8e545f6bf93b525a9982846873ca562ccea2bd68c0445df47e75b93192a9559) | SUCCESS | Missing production evidence identified |
| Resolve misleading claim | [`0xdddbba61…72fa`](https://explorer-studio.genlayer.com/tx/0xdddbba6102af31d56f06cf0422f58b798bd0b60af88cb027c8caf6c7ca6972fa) | SUCCESS | Consensus ruling `MISREPRESENTED` |

All ten transactions reached `FINALIZED`. Expected successes had agreed validator execution `SUCCESS`; expected rejection paths had execution `ERROR`.

## Canonical final state

- `supported-muaparlu`: `RESOLVED / SUPPORTED`; ruling digest `77018bcfaf770de153ac0c7a19a55b1ba677077f6f721da72e3d3428ca5a6ddb`.
- `misleading-muaparlu`: `RESOLVED / MISREPRESENTED`; ruling digest `e2471744a919298525fe5e449c06e07bfe9fad3e56a4800c3af5899126cd56a8`.
- Publisher telemetry: `published=2`, `supported=1`, `faults=1`.
- Challenger telemetry: `challenges=2`, `challenge_wins=1`, `challenge_losses=1`.
- Contract stats: `claims=2`, `resolved=2`.

Full source byte counts, hashes, transaction statuses, assertions and readback are preserved in [`live-e2e-run.json`](./live-e2e-run.json).
