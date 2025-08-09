# Demo/Test Cryptographic Keys

This directory is intended to hold NON-PRODUCTION sample or test keys used by the C++ client during local development.

Current status:
- No tracked key files were moved automatically (existing keys in `data/` were untracked). Keep real secrets out of git.

Guidelines:
1. Do NOT commit real private keys.
2. Prefer environment or secure secret storage for production.
3. If adding representative sample keys, clearly mark them and ensure they are generated for test only.
