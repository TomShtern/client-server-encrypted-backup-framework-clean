Here is a comprehensive, step-by-step plan to migrate all CRC logic to the canonical shared modules, with detailed reasoning and risk mitigation:

---

## 1. **Preparation**

- **a. Create a new feature branch**  
  This allows you to make changes safely and revert if needed.
- **b. Ensure you have a clean working directory**  
  Commit or stash any unrelated changes.

---

## 2. **Locate All Legacy CRC Implementations**

- **Python:**  
  - `python_server/server/server.py`  
  - `python_server/server/file_transfer.py`
- **C++:**  
  - `Client/cpp/client.cpp`
- **Canonical modules:**  
  - Python: `python_server/shared/crc.py`
  - C++: `Client/deps/shared/crc.h` and `Client/deps/shared/crc.cpp`

---

## 3. **Migrate Python Code**

### a. In `python_server/server/server.py`:

- **Remove**:  
  - `_CRC32_TABLE`
  - `_calculate_crc`
  - `_finalize_crc`
- **Add**:  
  - `from python_server.shared.crc import calculate_crc32, CRC32Stream`
- **Replace all usages** of the old methods with the canonical ones.  
  - If you need streaming CRC, use `CRC32Stream`.
  - For one-shot, use `calculate_crc32(data)`.

### b. In `python_server/server/file_transfer.py`:

- **Repeat the same steps** as above.

---

## 4. **Migrate C++ Code**

### a. In `Client/cpp/client.cpp`:

- **Remove**:  
  - Any local CRC table and CRC calculation functions.
- **Add**:  
  - `#include "shared/crc.h"`
- **Replace all usages** of the old CRC functions with the canonical ones from `crc.h`.

---

## 5. **Update All Call Sites**

- **Search for all calls** to the old CRC functions in both Python and C++.
- **Replace** them with the new canonical function calls.
- **Adapt** the code if the function signatures are different.

---

## 6. **Test Thoroughly**

- **Run all unit and integration tests**:
  - Especially those that check file transfer, CRC validation, and cross-language compatibility.
  - Example: `tests/test_gui_filename_acceptance.py`
- **Manually test** a file transfer from the C++ client to the Python server and verify CRC checks pass.

---

## 7. **Cross-Language Verification**

- **Run the test vectors** in `Shared/test_vectors/headers.json` using both the Python and C++ canonical modules to confirm they produce the same CRCs.
- **If possible, add a test** that computes the CRC of the same data in both languages and compares the result.

---

## 8. **Cleanup**

- **Remove any remaining references** to the legacy CRC code.
- **Document** the migration in your commit message and/or project documentation.

---

## 9. **Rollback Plan**

- If any issues arise, revert the feature branch.
- The legacy code is preserved in git history and in the `archived/` directory.

---

## 10. **Merge and Deploy**

- Once all tests pass and you have verified correctness, merge the feature branch into your main branch.

---

### **Summary Table**

| File                                    | Legacy CRC? | Action Needed                                 |
|------------------------------------------|-------------|-----------------------------------------------|
| python_server/server/server.py           | Yes         | Remove legacy, use shared/crc.py              |
| python_server/server/file_transfer.py    | Yes         | Remove legacy, use shared/crc.py              |
| Client/cpp/client.cpp                    | Yes         | Remove legacy, use deps/shared/crc.h/.cpp     |

---

## **Extra Tips**

- **Do the migration in small steps**:  
  Migrate one file at a time, run tests after each.
- **If you’re nervous, keep the legacy code commented out** until you’re sure the new code works.
- **If you want, I can generate the exact code changes for you for each file.**

---

**This plan is designed to minimize risk and ensure a smooth migration. If you follow it step by step, you will safely and completely migrate all CRC logic to the canonical shared modules.**
