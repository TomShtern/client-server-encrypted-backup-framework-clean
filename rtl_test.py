#!/usr/bin/env python3
"""
RTL Test for PowerShell
"""

import Shared.utils.utf8_solution as utf8

def main():
    utf8.safe_print("POWERSHELL RTL UNICODE CHARACTERS TEST")
    utf8.safe_print("====================================")
    
    # Test with actual RTL Unicode control characters
    utf8.safe_print("Normal Hebrew: שלום עולם")
    utf8.safe_print("With RTL mark: \u200fשלום עולם")  # Right-to-Left Mark
    utf8.safe_print("With LTR mark: \u200eשלום עולם")  # Left-to-Right Mark
    utf8.safe_print("RTL override: \u202eשלום עולם\u202c")  # RTL Override + Pop Directional Format
    utf8.safe_print("LTR override: \u202dשלום עולם\u202c")  # LTR Override + Pop Directional Format
    utf8.safe_print("With embedding: \u202bשלום עולם\u202c")  # RTL Embedding + PDF
    
    utf8.safe_print("")
    utf8.safe_print("Mixed text examples:")
    utf8.safe_print("English \u202bשלום עולם\u202c English")
    utf8.safe_print("\u202bשלום עולם\u202c English \u202bשלום עולם\u202c")

if __name__ == "__main__":
    main()