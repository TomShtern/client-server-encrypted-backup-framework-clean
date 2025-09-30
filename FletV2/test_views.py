"""Test script to verify analytics and logs views can be imported."""
import sys
sys.path.insert(0, '.')

try:
    from views import analytics
    print("✅ analytics.py imported successfully")
except Exception as e:
    print(f"❌ analytics.py import failed: {e}")
    sys.exit(1)

try:
    from views import logs
    print("✅ logs.py imported successfully")
except Exception as e:
    print(f"❌ logs.py import failed: {e}")
    sys.exit(1)

print("\n✅ ALL VIEWS IMPORTED SUCCESSFULLY")
print(f"analytics.py: {len(open('views/analytics.py').read())} chars")
print(f"logs.py: {len(open('views/logs.py').read())} chars")
