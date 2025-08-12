import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Shared.utils.unified_config import UnifiedConfigurationManager

if __name__ == "__main__":
    print("Starting configuration migration...")
    config_manager = UnifiedConfigurationManager(base_path=".")
    migrations = config_manager.migrate_legacy_configurations()
    print(f"Migration complete. {len(migrations)} items migrated.")
    for m in migrations:
        print(f"- Migrated {m.source_file} to {m.target_key} = {m.value}")
