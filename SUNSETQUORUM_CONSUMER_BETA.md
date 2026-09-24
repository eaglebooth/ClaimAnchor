# SunsetQuorum Consumer Migration Evidence

- Service ID: `sunset-demo-api`
- Revision: `1`
- Consumer ID: `consumer-beta`
- Consumer account: `0x2da5393d7bbb9a037dc3abb56dbbc5c150fc843f`
- Consumer repository: `eaglebooth/claimanchor`
- Sealed terms digest: `b65a0b4d362f104dac887e33f143a0550fbfc079f7773f7a753f6c79a02ea0e2`

## Endpoint and schema mapping

The ClaimAnchor integration now calls `GET /v2/customers/{id}/profile` instead of `GET /v1/customer-profile/{id}`. The consumer maps the flat `id` and `displayName` fields into its internal profile record.

## Authentication migration

Requests now use an OAuth 2 bearer token containing `profile:read`. Code and configuration no longer send the deprecated `X-Legacy-Key` header.

## Error semantics and regression results

The integration recognizes HTTP 404 and parses the RFC 9457 problem document instead of expecting HTTP 200 with `customer: null`. Replacement-path regression tests passed for successful profile lookup, absent profile, invalid authorization, and upstream failure.

## Rollback procedure

The rollback procedure restores the legacy client adapter and secret reference behind a feature flag. The procedure was exercised with the same regression matrix and does not modify the sealed terms or consumer registry.
