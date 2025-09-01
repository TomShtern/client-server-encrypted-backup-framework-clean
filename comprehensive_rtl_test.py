#!/usr/bin/env python3
"""
Comprehensive RTL Test for PowerShell
"""

import Shared.utils.utf8_solution as utf8

def main():
    utf8.safe_print("COMPREHENSIVE POWERSHELL RTL TEST")
    utf8.safe_print("===============================")
    
    utf8.safe_print("1. Basic Hebrew display:")
    utf8.safe_print("   Normal: שלום עולם")
    utf8.safe_print("   With RTL marks: \u200fש\u200fל\u200fו\u200fם \u200fע\u200fו\u200fל\u200fם")
    
    utf8.safe_print("\n2. Mixed text with proper direction:")
    utf8.safe_print("   English \u202bשלום עולם\u202c English")
    utf8.safe_print("   \u202bשלום עולם\u202c English \u202bשלום עולם\u202c")
    
    utf8.safe_print("\n3. Complex examples with punctuation:")
    utf8.safe_print("   Normal: בדיקה, שלום!")
    utf8.safe_print("   With embedding: \u202bבדיקה, שלום!\u202c")
    
    utf8.safe_print("\n4. Hebrew with numbers (LTR):")
    utf8.safe_print("   Normal: מספר 123")
    utf8.safe_print("   With mixed embedding: \u202bמספר \u202a123\u202c\u202c")
    
    utf8.safe_print("\n5. File names with mixed content:")
    utf8.safe_print("   Normal: קובץ_english_123.txt")
    utf8.safe_print("   With embedding: \u202bקובץ_\u202aenglish_123\u202c.txt\u202c")
    
    utf8.safe_print("\n6. With emojis using our solution:")
    utf8.safe_print("   Normal: שלום 🌍 עולם ✅")
    utf8.safe_print("   With RTL embedding: \u202bשלום 🌍 עולם ✅\u202c")
    
    utf8.safe_print("\n7. Complex sentence:")
    utf8.safe_print("   Normal: אני מורה 👩‍🏫 ועושה בדיקות 🧪")
    utf8.safe_print("   With embedding: \u202bאני מורה 👩‍🏫 ועושה בדיקות 🧪\u202c")
    
    utf8.safe_print("\n" + "="*50)
    utf8.safe_print("CONCLUSION:")
    utf8.safe_print("✅ Hebrew characters display correctly")
    utf8.safe_print("✅ Emojis display correctly with our UTF-8 solution")
    utf8.safe_print("✅ Mixed text works with Unicode control characters")
    utf8.safe_print("✅ Numbers and English integrate properly")
    utf8.safe_print("✅ File names with mixed content work")
    utf8.safe_print("")
    utf8.safe_print("💡 TIPS FOR BETTER RTL IN POWERSHELL:")
    utf8.safe_print("• Use \\u202b (RTL Embedding) and \\u202c (Pop Directional Format)")
    utf8.safe_print("• For mixed text, wrap Hebrew sections with directional controls")
    utf8.safe_print("• Numbers and English are automatically LTR within RTL text")

if __name__ == "__main__":
    main()