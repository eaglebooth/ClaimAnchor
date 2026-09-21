# ClaimAnchor

ClaimAnchor is an optimistic citation-entailment registry built as a GenLayer Intelligent Contract. A publisher anchors a public statement to a commit-pinned source. Anyone except that publisher may challenge the statement using evidence from a different repository. GenLayer validators then decide whether the citation genuinely supports the statement. Repository separation prevents using the exact source namespace twice; it does not prove different real-world ownership.

**Live contract:** [`0x902365aFBc441aE06f249F5ff39a4928F3827Ee2`](https://explorer-studio.genlayer.com/address/0x902365aFBc441aE06f249F5ff39a4928F3827Ee2) on GenLayer Studionet (`61999`).

**Live verification:** [finalized supported, misleading and rejection-path transaction ledger](./docs/LIVE_STUDIONET_EVIDENCE.md).

This is intentionally not a pre-appointed reviewer pipeline. Challenge authority is permissionless and comes from `gl.message.sender_address`; documents provide evidence but never authority.

## Bounded rulings

- `SUPPORTED` — the cited source entails the statement.
- `MISREPRESENTED` — the statement contradicts, exaggerates or changes the source.
- `CONTEXT_MISSING` — omitted context makes the statement misleading.
- `CONFLICTED` — credible supplied sources materially disagree.
- `UNAVAILABLE` — evidence or model output failed; the challenge is cleared and the claim reopens so a bad URL cannot lock it.

## State and reputation telemetry

Claims move through `PUBLISHED -> CHALLENGED -> RESOLVED`. Resolution updates separate publisher and challenger counters:

- publishers: published, supported and faults;
- challengers: challenges, wins and losses.

Conflicted rulings are recorded without assigning a win or fault. Counters update only after a terminal ruling. They are transparent activity telemetry—not Sybil-resistant identity or a standalone trust score. Claim IDs are namespaced by publisher address, evidence is SHA-256 and byte-length bound, source repositories must differ, and nonces prevent replay.

## Methods

- `publish_claim`
- `challenge_claim`
- `resolve_claim`
- `get_claim`
- `get_reputation`
- `get_stats`
- `get_contract_version`

## Test

```bash
python -m pytest -q -p no:cacheprovider
```

The suite executes the real contract with `gltest` and covers input rejection, publisher namespaces, permissionless repository-separated challenges, all four terminal rulings, telemetry updates, retryable source/model failure, nonce replay and finalized-claim replay protection.

The deployed contract was also exercised with two wallets and two commit-pinned repositories. Ten transactions finalized, including `SUPPORTED`, `MISREPRESENTED`, duplicate/self-challenge/finality rejection paths, and canonical publisher/challenger telemetry readback.

## Deploy

Deploy `contracts/claim_anchor.py` in GenLayer Studio Next. The included Markdown files are synthetic fixtures, not claims about a real service.
