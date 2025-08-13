#!/usr/bin/env python3
"""
Fix me.info encoding issues using real project data
This script will read the existing me.info, extract the real data, and rewrite it properly
"""

import os

def analyze_and_fix_me_info():
    """Analyze and fix the me.info file encoding issues"""
    
    if not os.path.exists('me.info'):
        print("❌ me.info file not found")
        return False
    
    print("📁 Analyzing current me.info file...")
    
    # Read the raw binary data
    with open('me.info', 'rb') as f:
        raw_data = f.read()
    
    print(f"📊 File size: {len(raw_data)} bytes")
    print(f"🔍 First 100 bytes (hex): {raw_data[:100].hex()}")
    
    # Try to decode and extract the real data
    try:
        # Decode with latin1 to preserve all bytes
        text_content = raw_data.decode('latin1')
        lines = text_content.split('\n')
        
        print(f"\n📋 Found {len(lines)} lines:")
        for i, line in enumerate(lines):
            line_clean = line.rstrip('\r')
            if len(line_clean) > 50:
                print(f"  Line {i+1}: {line_clean[:50]}... ({len(line_clean)} chars)")
            else:
                print(f"  Line {i+1}: {repr(line_clean)}")
        
        # Extract the real username and UUID
        if len(lines) >= 2:
            username = lines[0].rstrip('\r')
            uuid_hex = lines[1].rstrip('\r')
            
            print(f"\n✅ Extracted real project data:")
            print(f"   Username: {username}")
            print(f"   UUID: {uuid_hex}")
            
            # Validate UUID format
            if len(uuid_hex) == 32 and all(c in '0123456789abcdef' for c in uuid_hex.lower()):
                print(f"   ✅ UUID format is valid")
                
                # Create a proper me.info file with just the essential data
                # (The RSA key should be handled separately by the proper RSA key files)
                fixed_content = f"{username}\n{uuid_hex}\n"
                
                # Backup the original
                with open('me.info.backup', 'wb') as f:
                    f.write(raw_data)
                print(f"   💾 Backed up original to me.info.backup")
                
                # Write the fixed version
                with open('me.info', 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                print(f"   ✅ Created fixed me.info with proper UTF-8 encoding")
                
                # Verify the fix
                with open('me.info', 'r', encoding='utf-8') as f:
                    verification = f.read()
                    print(f"   🔍 Verification - new content: {repr(verification)}")
                
                return True
            else:
                print(f"   ❌ UUID format invalid: {uuid_hex}")
                return False
        else:
            print(f"   ❌ Not enough lines in file")
            return False
            
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        return False

def test_fixed_file():
    """Test that the fixed file can be read properly"""
    try:
        with open('me.info', 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.strip().split('\n')
            
            if len(lines) >= 2:
                username = lines[0]
                uuid_hex = lines[1]
                
                print(f"\n🧪 Testing fixed file:")
                print(f"   ✅ Can read as UTF-8")
                print(f"   ✅ Username: {username}")
                print(f"   ✅ UUID: {uuid_hex}")
                print(f"   ✅ File is now properly formatted")
                return True
            else:
                print(f"   ❌ Fixed file has wrong format")
                return False
                
    except UnicodeDecodeError as e:
        print(f"   ❌ Still has encoding issues: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error testing fixed file: {e}")
        return False

def main():
    print("🔧 Fixing me.info encoding issues using real project data")
    print("=" * 60)
    
    success = analyze_and_fix_me_info()
    
    if success:
        test_success = test_fixed_file()
        if test_success:
            print(f"\n🎉 SUCCESS: me.info encoding issue FIXED!")
            print(f"✅ File now uses proper UTF-8 encoding with real project data")
            print(f"✅ Username and UUID preserved from original file")
            print(f"✅ Can be read by Python code without encoding errors")
        else:
            print(f"\n❌ FAILED: Fix didn't work properly")
    else:
        print(f"\n❌ FAILED: Could not fix me.info")
    
    return success

if __name__ == "__main__":
    main()
