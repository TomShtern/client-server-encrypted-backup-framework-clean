# Protocol Canonicalization Specification

## Overview

This document defines the exact canonicalization rules for the Client-Server Encrypted Backup Framework protocol, ensuring consistent behavior across Python and C++ implementations.

## Header Canonicalization Rules

### Text Encoding
- **Encoding**: UTF-8
- **Unicode Normalization**: NFC (Canonical Decomposition followed by Canonical Composition)
- **Line Endings**: `\n` (LF) for all platforms including Windows

### Header Field Processing

#### Name Normalization
```
canonical_name = original_name.strip().lower()
```

#### Value Normalization
1. Apply Unicode NFC normalization
2. Strip leading and trailing whitespace
3. Collapse internal whitespace to single space
4. Remove control characters (ASCII 0-31 except tab/newline)

```python
import unicodedata
import re

def normalize_value(value):
    # Unicode normalization
    normalized = unicodedata.normalize('NFC', value)
    # Strip whitespace
    stripped = normalized.strip()
    # Collapse internal whitespace
    collapsed = re.sub(r'\s+', ' ', stripped)
    # Remove control characters except tab
    clean = re.sub(r'[\x00-\x08\x0B-\x1F\x7F]', '', collapsed)
    return clean
```

#### Header Ordering
- Sort header fields alphabetically by canonical name
- Case-insensitive sorting (already handled by name normalization)

#### Duplicate Headers
- **Policy**: Reject duplicates - protocol violation
- **Implementation**: Raise error if duplicate header names detected

### Canonical Format

#### BHI Header Format
```
<bhi>
name1:value1
name2:value2
...
nameN:valueN
</bhi>
```

#### Canonical Byte Sequence Generation
1. Start with opening tag: `<bhi>\n`
2. For each header (sorted by name):
   - Append: `{canonical_name}:{normalized_value}\n`
3. End with closing tag: `</bhi>\n`
4. Encode as UTF-8 bytes

### Timestamp Format
- **Standard**: ISO 8601 format
- **Pattern**: `YYYY-MM-DDThh:mm:ssZ` (UTC timezone)
- **Example**: `2025-08-09T22:23:45Z`

## CRC32 Calculation

### Algorithm Parameters
- **Polynomial**: 0x04C11DB7 (IEEE 802.3 / POSIX cksum)
- **Initial Value**: 0x00000000
- **Reflect Input**: No
- **Reflect Output**: No
- **Final XOR**: 0xFFFFFFFF (one's complement)

### Implementation Requirements
1. Process canonical byte sequence
2. Include length processing (POSIX cksum compatible)
3. Apply final inversion
4. Return 32-bit unsigned integer

### Cross-Language Compatibility
- Python and C++ implementations MUST produce identical results
- Test vectors provided for verification

## Canonicalization Examples

### Example 1: Basic Headers
**Input:**
```
<bhi>
  Content-Type  :  application/json  
filename:  test.txt
</bhi>
```

**Canonical Output:**
```
<bhi>
content-type:application/json
filename:test.txt
</bhi>
```

**Expected CRC32**: `0x12345678` (calculated from canonical bytes)

### Example 2: Unicode and Whitespace
**Input:**
```
<bhi>
description:  Multiple   spaces   and	tabs
filename: tëst_fîle.txt  
</bhi>
```

**Canonical Output:**
```
<bhi>
description:Multiple spaces and tabs
filename:tëst_fîle.txt
</bhi>
```

### Example 3: Timestamp
**Input:**
```
<bhi>
timestamp: 2025-08-09T22:23:45Z
filename: backup.dat
</bhi>
```

**Canonical Output:**
```
<bhi>
filename:backup.dat
timestamp:2025-08-09T22:23:45Z
</bhi>
```

## Implementation Guidelines

### Python Implementation
- Use `unicodedata.normalize('NFC', text)`
- Use `re.sub()` for whitespace normalization
- Sort using `sorted()` with key function
- Encode with `.encode('utf-8')`

### C++ Implementation
- Use ICU library for Unicode normalization (if available)
- Implement equivalent whitespace normalization
- Use `std::sort()` with custom comparator
- Ensure UTF-8 encoding consistency

### Error Handling
- Invalid UTF-8 sequences: Reject with clear error
- Duplicate headers: Reject with protocol violation error
- Malformed timestamps: Reject with format error
- Control characters: Remove silently (except in filenames)

## Test Vector Requirements

All implementations MUST pass the test vectors defined in:
- `Shared/test_vectors/headers.json`
- `Shared/test_vectors/crc_vectors.json`

Test vectors include edge cases:
- Empty headers
- Unicode edge cases
- Maximum length values
- Boundary conditions
- Error conditions

## Compliance Verification

Implementations MUST:
1. Pass all test vectors
2. Produce identical canonical bytes for identical input
3. Generate identical CRC32 values
4. Handle all specified error conditions
5. Maintain cross-language compatibility
