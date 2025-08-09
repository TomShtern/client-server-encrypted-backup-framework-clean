# Archived Duplicate / Generated Files (2025-08-10)

This directory contains files moved from their original locations because they are generated artifacts or duplicates and should not live in active config/data trees.

Contents:
- `config/server/client/transfer.info` (generated sample connection file)
- (Untracked `data/transfer.info` existed but was not under version control so it was not archived via git mv.)

Origin commit: (pending commit SHA after staging)  
Reason: Normalize repository so only canonical runtime configs remain; transfer.info is generated per run.

Do not restore unless a test explicitly requires a committed static transfer.info (prefer creating it dynamically in tests instead).
