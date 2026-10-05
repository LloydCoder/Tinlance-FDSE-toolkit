# Phase 12 — Secure Delivery

The historical remote-delivery component was audited and did not itself implement a real expiring portal or authenticated encryption. It primarily packaged files, calculated hashes, and generated delivery instructions. The maintained delivery core now provides a local encrypted package format.

## Cryptographic profile
- AES-256-GCM authenticated encryption.
- 96-bit random nonce per package.
- 128-bit random salt.
- scrypt password KDF with explicit cost parameters.
- authenticated metadata as AES-GCM associated data.
- restrictive output permissions where supported.
- SHA-256 manifest inside the plaintext ZIP before encryption.

Python documents scrypt as a password-based KDF defined by RFC 7914 and recommends a proper random salt; Cryptography documents AES-GCM with 256-bit keys and 12-byte nonces and warns never to reuse a nonce with a key. The implementation therefore does not claim that a hash-only ZIP is encrypted or that local package generation is a time-limited portal.

Actual expiring links, revocation, authentication, and download audit logs require a separate delivery service and are not represented as implemented by this private Toolkit.
