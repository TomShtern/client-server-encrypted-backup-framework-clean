#!/usr/bin/env python3
"""
Filename Acceptance E2E Test (GUI API)

Purpose:
- Verify that filenames with common punctuation (spaces, &, parentheses, +, comma, dash, underscore, dot)
  are accepted end-to-end through the GUI → Flask API → C++ client → Python server chain.
- This test DOES NOT change protocol or crypto. It only exercises the existing pipeline.

How it works:
- Creates a small markdown file with a special-character filename and a unique signature.
- POSTs it to http://localhost:9090/api/start_backup using the same pattern as other GUI tests.
- Waits briefly for processing, then checks server/received_files (and fallback received_files) for the new file
  and verifies the content includes the unique signature.

Safe to run multiple times; it will detect new files compared to the initial directory snapshot.
"""

import os
import time
import uuid
import requests


API_URL = "http://localhost:9090/api/start_backup"
RECEIVED_DIRS = [
    os.path.join("server", "received_files"),
    os.path.join("received_files"),
]


def list_dir_safe(path):
    try:
        return set(os.listdir(path)) if os.path.exists(path) else set()
    except Exception:
        return set()


def find_new_files(initial_snapshots):
    new_files = []
    for idx, d in enumerate(RECEIVED_DIRS):
        before = initial_snapshots[idx]
        after = list_dir_safe(d)
        if after - before:
            for f in sorted(after - before):
                new_files.append((d, f))
    return new_files


def test_filename_acceptance_via_gui_api():
    # Prepare special filename and content
    base_filename = "Final & Plan (v1)+notes,checklist.md"
    unique_sig = f"FILENAME_ACCEPT_TEST_SIGNATURE::{uuid.uuid4()}"
    content = f"# Acceptance Test\n\nThis is a test.\n\n{unique_sig}\n"

    # Create the file in the working directory (kept local; server will receive a copy)
    with open(base_filename, "w", encoding="utf-8") as f:
        f.write(content)

    # Snapshot received directories before upload
    initial_snapshots = [list_dir_safe(d) for d in RECEIVED_DIRS]

    # Perform upload via GUI API
    try:
        with open(base_filename, "rb") as f:
            files = {"file": (base_filename, f, "text/markdown")}
            resp = requests.post(API_URL, files=files, timeout=30)
    except Exception as e:
        print(f"❌ Upload request failed: {e}")
        return False

    print(f"📡 API status: {resp.status_code}")
    print(f"📄 API response: {getattr(resp, 'text', '')[:500]}")

    if resp.status_code != 200:
        print("❌ API did not accept the upload request.")
        return False

    # Wait for processing and check for the new file, up to ~20s
    deadline = time.time() + 20
    found_paths = []
    while time.time() < deadline:
        time.sleep(1.0)
        new_files = find_new_files(initial_snapshots)
        if new_files:
            found_paths = new_files
            break

    if not found_paths:
        print("❌ No new files detected in received directories.")
        print("   Checked:")
        for d in RECEIVED_DIRS:
            print(f"   - {d}")
        return False

    # Try to locate the uploaded file among new files (filenames on server are usually prefixed)
    matched = []
    for d, fname in found_paths:
        if base_filename in fname or fname.endswith(base_filename):
            matched.append(os.path.join(d, fname))

    # Fall back to checking all new files if name-prefixing scheme differs
    to_check = matched or [os.path.join(d, f) for d, f in found_paths]

    for path in to_check:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as rf:
                data = rf.read()
            if unique_sig in data:
                print(f"✅ Verified uploaded file content at: {path}")
                return True
        except Exception as e:
            print(f"⚠️  Could not read candidate file {path}: {e}")

    print("❌ Uploaded file not found or content did not match unique signature.")
    print("   Candidates inspected:")
    for p in to_check:
        print(f"   - {p}")
    return False


def main():
    print("=" * 60)
    print("Filename Acceptance E2E Test (GUI API)")
    print("=" * 60)
    ok = test_filename_acceptance_via_gui_api()
    print("\n" + "=" * 60)
    if ok:
        print("🎉 PASS: Filename with punctuation accepted and verified end-to-end.")
    else:
        print("💥 FAIL: Filename acceptance test did not pass.")
    print("=" * 60)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
