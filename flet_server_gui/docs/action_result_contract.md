# ActionResult Contract (GUI Unified Actions)

This document defines the unified ActionResult contract for all button-triggered operations in the Flet GUI.

## Goals
1. Eliminate ad-hoc bool/None/dict returns from handlers.
2. Provide stable, machine-readable codes and human messages.
3. Enable centralized notification, tracing, analytics, and retry logic.
4. Support bulk, single, and streamed operations consistently.

## Data Model
Field | Type | Description
----- | ---- | -----------
code | str | One of SUCCESS, WARNING, ERROR, CANCELLED, INFO, PARTIAL, RETRYING
success | bool | True if terminal non-error success (code in {SUCCESS, INFO})
message | str | User-facing human message (already localized / ready to show)
details | str | Optional longer detail (stack, validation list, etc.)
data | Any | Domain payload (IDs, file info, counts, preview text, etc.)
selection | list[str] | IDs/keys acted upon (after validation & filtering)
count | int | Convenience mirror of len(selection) when applicable
duration_ms | int | Wall clock duration (executor fills)
error_code | str | Machine error code (e.g., VALIDATION_FAILED, IO_ERROR)
severity | str | success, info, warning, error
meta | dict | Arbitrary extra (attempts, partial_failures, skipped_items)
timestamp | str | ISO8601 emission time (executor fills)

## Codes & Semantics
Code | success? | Typical severity | Meaning
---- | -------- | ---------------- | -------
SUCCESS | True | success | Operation completed fully
INFO | True | info | Informational (no state change or benign no-op)
WARNING | False | warning | Completed with non-fatal issues (e.g. some skips)
PARTIAL | False | warning | Bulk: subset succeeded (meta.partial_failures)
ERROR | False | error | Failed (no meaningful completion)
CANCELLED | False | info | User or precondition cancelled
RETRYING | False | info | Transient state (intermediate, not final)

Terminal codes: SUCCESS, INFO, WARNING, PARTIAL, ERROR, CANCELLED.
Non-terminal (intermediate) codes: RETRYING.

## Constructor Helpers (to implement / enforce)
```python
ActionResult.success(message: str, data=None, selection=None, meta=None)
ActionResult.info(message: str, data=None, selection=None, meta=None)
ActionResult.warning(message: str, details=None, data=None, selection=None, meta=None)
ActionResult.partial(message: str, failed: list=None, data=None, selection=None, meta=None)
ActionResult.error(message: str, error_code: str=None, details=None, selection=None, meta=None)
ActionResult.cancelled(message: str="Cancelled by user", selection=None, meta=None)
ActionResult.retrying(message: str, attempt: int, max_attempts: int, selection=None, meta=None)
```

Executor will wrap legacy ActionResult (base_action.ActionResult) into this richer structure until all references updated.

## Adapter Strategy
Legacy Return | Mapping Rule
------------- | ------------
True | SUCCESS with generic message if none produced
False | ERROR with message "Operation failed"
None | INFO (no-op) unless selection required & missing ⇒ ERROR validation
dict with 'valid': bool | valid True ⇒ SUCCESS else ERROR (details=error)
Existing base_action.ActionResult | Translate: success→SUCCESS or ERROR; carry error_message/error_code into message/error_code
List[ActionResult] (legacy) | If all success ⇒ SUCCESS; mixed ⇒ PARTIAL with meta.partial_failures; all fail ⇒ ERROR

## Selection Validation Rules
1. If requires_selection and empty ⇒ ERROR(code=VALIDATION_FAILED)
2. If min_selection > len(selection) ⇒ ERROR
3. If max_selection and len(selection) > max ⇒ WARNING (auto-truncate) OR ERROR (strict) — we choose truncate + meta.truncated=True.
4. Duplicate IDs removed with meta.duplicates_removed count.

## Bulk Operation Normalization
For bulk handlers performing per-item operations:
1. Collect per-item results into arrays.
2. successes = [r for r in per_item if r.success]
3. failures = [... if not r.success]
4. Code selection:
   - if len(failures)==0 ⇒ SUCCESS
   - elif len(successes)==0 ⇒ ERROR (message summarizing first failure)
   - else ⇒ PARTIAL (meta.partial_failures list of {id, error})
5. Provide meta counts: total, succeeded, failed, skipped.

## Tracing Alignment
TraceCenter events will include: {action_name, code, success, duration_ms, count, severity}.
Intermediate RETRYING events allowed; only last terminal event surfaces notification.

## Notification Mapping
severity success → success style
severity info / code INFO/CANCELLED → neutral style
severity warning / code WARNING/PARTIAL → warning style
severity error / code ERROR → error style

## Transitional Plan
Phase A (current): Introduce contract doc + implement new ActionResult class (parallel to existing) with adapter.
Phase B: Refactor handlers to construct new ActionResult helpers directly.
Phase C: Remove legacy prints, ensure executor consumes unified format only.
Phase D: Deprecate base_action.ActionResult or subclass it from unified.

## Edge Cases
Case | Handling
---- | --------
User cancels dialog | CANCELLED
Missing dialog system (fallback) | INFO or WARNING (meta.fallback_used=True)
Selection partially invalid | PARTIAL (meta.invalid_ids)
Network timeout | ERROR(error_code=TIMEOUT)
Retry succeeding on attempt N | SUCCESS(meta.attempts=N)

## Example (Bulk Delete Files)
```json
{
  "code": "PARTIAL",
  "success": false,
  "message": "Deleted 8 of 10 files",
  "count": 10,
  "selection": ["a.txt", "b.txt", ...],
  "meta": {
    "succeeded": 8,
    "failed": 2,
    "partial_failures": [
      {"id": "i.txt", "error": "Not found"},
      {"id": "j.txt", "error": "Permission denied"}
    ]
  },
  "duration_ms": 742
}
```

---
This contract is authoritative; future GUI logic (notifications, adaptive UX, analytics) must rely solely on these fields.
