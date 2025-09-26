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
        # sourcery skip: assign-if-exp, hoist-statement-from-if
        return set(os.listdir(path)) if os.path.exists(path) else set()
    except Exception:  # sourcery skip: raise-specific-error
        return set()


def find_new_files(initial_snapshots):
    # sourcery skip: merge-list-append, list-comprehension
    new_files = []
    for idx, d in enumerate(RECEIVED_DIRS):
        before = initial_snapshots[idx]
        after = list_dir_safe(d)
        if after - before:
            new_files.extend((d, f) for f in sorted(after - before))
    return new_files


def print_directory_info(message, directories):
    """Helper function to print directory information."""
    print(message)
    print("   Checked:")
    for d in directories:
        print(f"   - {d}")


def print_candidates_info(message, candidates):
    """Helper function to print candidate files information."""
    print(message)
    print("   Candidates inspected:")
    for p in candidates:
        print(f"   - {p}")


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

    # sourcery skip: no-conditionals-in-tests
    if resp.status_code != 200:
        print("❌ API did not accept the upload request.")
        return False

    # Wait for processing and check for the new file, up to ~20s
    deadline = time.time() + 20
    found_paths = []
    # sourcery skip: no-loop-in-tests
    while time.time() < deadline:
        time.sleep(1.0)
        if new_files := find_new_files(initial_snapshots):
            found_paths = new_files
            break

    if not found_paths:
        print_directory_info("❌ No new files detected in received directories.", RECEIVED_DIRS)
        return False

    # Try to locate the uploaded file among new files (filenames on server are usually prefixed)
    # sourcery skip: merge-list-append, list-comprehension
    matched = [
        os.path.join(d, fname)
        for d, fname in found_paths
        if base_filename in fname or fname.endswith(base_filename)
    ]

    # Fall back to checking all new files if name-prefixing scheme differs
    to_check = matched or [os.path.join(d, f) for d, f in found_paths]

    for path in to_check:
        try:
            with open(path, encoding="utf-8", errors="ignore") as rf:
                if unique_sig in rf.read():
                    print(f"✅ Verified uploaded file content at: {path}")
                    return True
        except Exception as e:  # sourcery skip: raise-specific-error
            print(f"⚠️  Could not read candidate file {path}: {e}")

    print_candidates_info("❌ Uploaded file not found or content did not match unique signature.", to_check)
    return False


def main():
    print("=" * 60)
    print("Filename Acceptance E2E Test (GUI API)")
    print("=" * 60)
    ok = test_filename_acceptance_via_gui_api()
    print("\n" + "=" * 60)

    result_msg = ("🎉 PASS: Filename with punctuation accepted and verified end-to-end."
                  if ok else "💥 FAIL: Filename acceptance test did not pass.")
    print(result_msg)
    print("=" * 60)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
