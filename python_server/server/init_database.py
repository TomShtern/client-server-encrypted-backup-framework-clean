#!/usr/bin/env python3
"""
Database Initialization Script
Creates and initializes the database schema for the encrypted backup server.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database schema."""
    try:
        # Import database manager
        from python_server.server.database import DatabaseManager
        
        logger.info("Initializing database schema...")
        
        # Create database manager instance
        db_manager = DatabaseManager()
        
        # Initialize database schema
        db_manager.init_database()
        
        # Validate that tables were created by querying them directly
        try:
            # Try to query the clients table
            clients_result = db_manager.execute("SELECT COUNT(*) FROM clients", fetchone=True)
            clients_count = clients_result[0] if clients_result else 0
            logger.info(f"Clients table exists with {clients_count} records")
            
            # Try to query the files table
            files_result = db_manager.execute("SELECT COUNT(*) FROM files", fetchone=True)
            files_count = files_result[0] if files_result else 0
            logger.info(f"Files table exists with {files_count} records")
            
            logger.info("✅ Database schema initialized successfully!")
            logger.info("✅ Required tables 'clients' and 'files' are present")
            return True
            
        except Exception as table_error:
            logger.error(f"Error validating database tables: {table_error}")
            # List all tables to see what's available
            try:
                tables_result = db_manager.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'database_migrations'", 
                    fetchall=True
                )
                tables = [row[0] for row in tables_result] if tables_result else []
                logger.info(f"Available tables: {tables}")
                
                if 'clients' in tables and 'files' in tables:
                    logger.info("✅ Required tables 'clients' and 'files' are present")
                    return True
                else:
                    logger.error("❌ Required tables are missing!")
                    return False
            except Exception as list_error:
                logger.error(f"Error listing database tables: {list_error}")
                return False
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def create_sample_data():
    """Create sample data for testing."""
    try:
        from python_server.server.database import DatabaseManager
        import uuid
        from datetime import datetime, timezone
        
        logger.info("Creating sample data...")
        
        db_manager = DatabaseManager()
        
        # Create a sample client
        client_id = uuid.uuid4().bytes
        client_name = "sample_client"
        public_key = b"sample_public_key_160_bytes_x509_format____________________________"
        aes_key = b"sample_aes_key_32_bytes________________________________"
        
        db_manager.save_client_to_db(client_id, client_name, public_key, aes_key)
        logger.info(f"Created sample client: {client_name}")
        
        # Create a sample file
        file_name = "sample_file.txt"
        path_name = "received_files/sample_file.txt"
        verified = True
        file_size = 1024
        mod_date = datetime.now(timezone.utc).isoformat()
        crc = 1234567890
        
        db_manager.save_file_info_to_db(client_id, file_name, path_name, verified, file_size, mod_date, crc)
        logger.info(f"Created sample file: {file_name}")
        
        logger.info("✅ Sample data created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create sample data: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Main function to initialize the database."""
    logger.info("=== Database Initialization Script ===")
    
    # Ensure storage directory exists
    storage_dir = "received_files"
    os.makedirs(storage_dir, exist_ok=True)
    logger.info(f"Storage directory '{storage_dir}' ready")
    
    # Initialize database
    if not init_database():
        logger.error("Database initialization failed!")
        return 1
    
    # Create sample data
    if not create_sample_data():
        logger.error("Sample data creation failed!")
        return 1
    
    logger.info("=== Database initialization completed successfully! ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())