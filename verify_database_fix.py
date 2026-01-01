import os
import sys
import traceback

# Force add paths
sys.path.insert(0, os.getcwd())

print("Attempting to import database_pro...")
try:
    import FletV2.views.database_pro as db_pro

    print("Import SUCCESS")

    if hasattr(db_pro, "create_neumorphic_metric_card"):
        print(
            "Function create_neumorphic_metric_card FOUND in database_pro (local definition)"
        )
    else:
        print("Function create_neumorphic_metric_card MISSING")

except Exception:
    print("Import FAILED")
    traceback.print_exc()
