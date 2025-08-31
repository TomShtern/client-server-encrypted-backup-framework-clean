"""
Purpose: Export/import functionality
Logic: Data export and import operations
No UI: Pure business logic for data export/import
"""

import csv
import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Callable
from dataclasses import dataclass
import zipfile
import tempfile

# Enable UTF-8 support for file operations
try:
    import Shared.utils.utf8_solution
except ImportError:
    pass


@dataclass
class ExportResult:
    """Result of an export operation"""
    success: bool
    file_path: Optional[str] = None
    records_exported: int = 0
    error_message: Optional[str] = None
    export_format: str = "unknown"
    file_size_bytes: int = 0


@dataclass
class ImportResult:
    """Result of an import operation"""
    success: bool
    records_imported: int = 0
    records_skipped: int = 0
    errors: List[str] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class DataExportService:
    """Service for exporting and importing data in various formats"""
    
    def __init__(self, database_path: Optional[str] = None, log_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize data export service
        
        Args:
            database_path: Path to SQLite database (optional)
            log_callback: Optional callback for logging messages
        """
        self.database_path = database_path
        self.log_callback = log_callback or print
        self.supported_formats = ['csv', 'json', 'sqlite']
        
        # Default export directory
        self.default_export_dir = Path("exports")
        self.default_export_dir.mkdir(exist_ok=True)
        
        self.log_callback(f"[EXPORT] Data export service initialized (formats: {', '.join(self.supported_formats)})")
    
    def set_database_path(self, database_path: str) -> bool:
        """
        Set or update the database path
        
        Args:
            database_path: Path to SQLite database
            
        Returns:
            bool: True if database is accessible
        """
        try:
            if os.path.exists(database_path):
                self.database_path = database_path
                self.log_callback(f"[EXPORT] Database path set to: {database_path}")
                return True
            else:
                self.log_callback(f"[EXPORT] Database not found: {database_path}")
                return False
        except Exception as e:
            self.log_callback(f"[EXPORT] Error setting database path: {e}")
            return False
    
    def export_table_to_csv(self, table_name: str, output_path: Optional[str] = None, include_headers: bool = True) -> ExportResult:
        """
        Export a database table to CSV format
        
        Args:
            table_name: Name of the database table to export
            output_path: Optional custom output file path
            include_headers: Whether to include column headers
            
        Returns:
            ExportResult with export operation details
        """
        if not self.database_path or not os.path.exists(self.database_path):
            return ExportResult(
                success=False,
                error_message="Database not available or path not set",
                export_format="csv"
            )
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.default_export_dir / f"{table_name}_{timestamp}.csv"
        
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Check if table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                if not cursor.fetchone():
                    return ExportResult(
                        success=False,
                        error_message=f"Table '{table_name}' not found in database",
                        export_format="csv"
                    )
                
                # Get data
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # Get column names
                column_names = [description[0] for description in cursor.description]
                
                # Write to CSV file
                with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    
                    if include_headers:
                        csv_writer.writerow(column_names)
                    
                    csv_writer.writerows(rows)
                
                file_size = os.path.getsize(output_path)
                self.log_callback(f"[EXPORT] Successfully exported {len(rows)} records from '{table_name}' to CSV")
                
                return ExportResult(
                    success=True,
                    file_path=str(output_path),
                    records_exported=len(rows),
                    export_format="csv",
                    file_size_bytes=file_size
                )
        
        except Exception as e:
            error_msg = f"Error exporting table '{table_name}' to CSV: {str(e)}"
            self.log_callback(f"[EXPORT] {error_msg}")
            return ExportResult(
                success=False,
                error_message=error_msg,
                export_format="csv"
            )
    
    def export_table_to_json(self, table_name: str, output_path: Optional[str] = None, pretty_format: bool = True) -> ExportResult:
        """
        Export a database table to JSON format
        
        Args:
            table_name: Name of the database table to export
            output_path: Optional custom output file path
            pretty_format: Whether to format JSON with indentation
            
        Returns:
            ExportResult with export operation details
        """
        if not self.database_path or not os.path.exists(self.database_path):
            return ExportResult(
                success=False,
                error_message="Database not available or path not set",
                export_format="json"
            )
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.default_export_dir / f"{table_name}_{timestamp}.json"
        
        try:
            with sqlite3.connect(self.database_path) as conn:
                conn.row_factory = sqlite3.Row  # This enables column access by name
                cursor = conn.cursor()
                
                # Check if table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                if not cursor.fetchone():
                    return ExportResult(
                        success=False,
                        error_message=f"Table '{table_name}' not found in database",
                        export_format="json"
                    )
                
                # Get data
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # Convert rows to dictionaries
                data = [dict(row) for row in rows]
                
                # Write to JSON file
                with open(output_path, 'w', encoding='utf-8') as jsonfile:
                    if pretty_format:
                        json.dump(data, jsonfile, indent=2, ensure_ascii=False, default=str)
                    else:
                        json.dump(data, jsonfile, ensure_ascii=False, default=str)
                
                file_size = os.path.getsize(output_path)
                self.log_callback(f"[EXPORT] Successfully exported {len(rows)} records from '{table_name}' to JSON")
                
                return ExportResult(
                    success=True,
                    file_path=str(output_path),
                    records_exported=len(rows),
                    export_format="json",
                    file_size_bytes=file_size
                )
        
        except Exception as e:
            error_msg = f"Error exporting table '{table_name}' to JSON: {str(e)}"
            self.log_callback(f"[EXPORT] {error_msg}")
            return ExportResult(
                success=False,
                error_message=error_msg,
                export_format="json"
            )
    
    def export_full_database(self, output_path: Optional[str] = None, format_type: str = "sqlite") -> ExportResult:
        """
        Export the entire database to a single file
        
        Args:
            output_path: Optional custom output file path
            format_type: Export format ('sqlite', 'zip')
            
        Returns:
            ExportResult with export operation details
        """
        if not self.database_path or not os.path.exists(self.database_path):
            return ExportResult(
                success=False,
                error_message="Database not available or path not set",
                export_format=format_type
            )
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if format_type == "sqlite":
                output_path = self.default_export_dir / f"backup_database_{timestamp}.db"
            else:
                output_path = self.default_export_dir / f"database_export_{timestamp}.zip"
        
        try:
            if format_type == "sqlite":
                # Direct database copy
                import shutil
                shutil.copy2(self.database_path, output_path)
                
                file_size = os.path.getsize(output_path)
                self.log_callback(f"[EXPORT] Database backup created at: {output_path}")
                
                return ExportResult(
                    success=True,
                    file_path=str(output_path),
                    records_exported=-1,  # Entire database
                    export_format="sqlite",
                    file_size_bytes=file_size
                )
            
            elif format_type == "zip":
                # Export all tables to temporary files, then zip
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    tables_exported = 0
                    total_records = 0
                    
                    # Get all table names
                    with sqlite3.connect(self.database_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                        tables = [row[0] for row in cursor.fetchall()]
                    
                    # Export each table to CSV
                    for table_name in tables:
                        csv_path = temp_path / f"{table_name}.csv"
                        result = self.export_table_to_csv(table_name, str(csv_path))
                        if result.success:
                            tables_exported += 1
                            total_records += result.records_exported
                    
                    # Create zip file
                    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for csv_file in temp_path.glob("*.csv"):
                            zipf.write(csv_file, csv_file.name)
                    
                    file_size = os.path.getsize(output_path)
                    self.log_callback(f"[EXPORT] Database exported to ZIP: {tables_exported} tables, {total_records} total records")
                    
                    return ExportResult(
                        success=True,
                        file_path=str(output_path),
                        records_exported=total_records,
                        export_format="zip",
                        file_size_bytes=file_size
                    )
            
            else:
                return ExportResult(
                    success=False,
                    error_message=f"Unsupported export format: {format_type}",
                    export_format=format_type
                )
        
        except Exception as e:
            error_msg = f"Error exporting full database: {str(e)}"
            self.log_callback(f"[EXPORT] {error_msg}")
            return ExportResult(
                success=False,
                error_message=error_msg,
                export_format=format_type
            )
    
    def import_csv_to_table(self, csv_path: str, table_name: str, create_table: bool = True, has_headers: bool = True) -> ImportResult:
        """
        Import CSV data to a database table
        
        Args:
            csv_path: Path to CSV file
            table_name: Target table name
            create_table: Whether to create table if it doesn't exist
            has_headers: Whether CSV has header row
            
        Returns:
            ImportResult with import operation details
        """
        if not self.database_path:
            return ImportResult(
                success=False,
                error_message="Database path not set"
            )
        
        if not os.path.exists(csv_path):
            return ImportResult(
                success=False,
                error_message=f"CSV file not found: {csv_path}"
            )
        
        try:
            records_imported = 0
            records_skipped = 0
            errors = []
            
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                with open(csv_path, 'r', encoding='utf-8') as csvfile:
                    csv_reader = csv.reader(csvfile)
                    
                    # Read first row (headers or data)
                    first_row = next(csv_reader, None)
                    if not first_row:
                        return ImportResult(
                            success=False,
                            error_message="CSV file is empty"
                        )
                    
                    headers = first_row if has_headers else [f"column_{i+1}" for i in range(len(first_row))]
                    
                    # Create table if requested
                    if create_table:
                        column_definitions = [f"{header} TEXT" for header in headers]
                        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_definitions)})"
                        cursor.execute(create_sql)
                        self.log_callback(f"[IMPORT] Table '{table_name}' created/verified")
                    
                    # Prepare insert statement
                    placeholders = ', '.join(['?' for _ in headers])
                    insert_sql = f"INSERT INTO {table_name} ({', '.join(headers)}) VALUES ({placeholders})"
                    
                    # Import data
                    for row_num, row in enumerate(csv_reader if has_headers else [first_row] + list(csv_reader), 1):
                        try:
                            if len(row) == len(headers):
                                cursor.execute(insert_sql, row)
                                records_imported += 1
                            else:
                                records_skipped += 1
                                errors.append(f"Row {row_num}: column count mismatch")
                        except sqlite3.Error as e:
                            records_skipped += 1
                            errors.append(f"Row {row_num}: {str(e)}")
                
                conn.commit()
            
            self.log_callback(f"[IMPORT] CSV import completed: {records_imported} imported, {records_skipped} skipped")
            
            return ImportResult(
                success=records_imported > 0,
                records_imported=records_imported,
                records_skipped=records_skipped,
                errors=errors[:10]  # Limit error list
            )
        
        except Exception as e:
            error_msg = f"Error importing CSV '{csv_path}': {str(e)}"
            self.log_callback(f"[IMPORT] {error_msg}")
            return ImportResult(
                success=False,
                error_message=error_msg
            )
    
    def get_available_tables(self) -> List[str]:
        """
        Get list of available tables in the database
        
        Returns:
            List of table names
        """
        if not self.database_path or not os.path.exists(self.database_path):
            return []
        
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                tables = [row[0] for row in cursor.fetchall()]
                return tables
        except Exception as e:
            self.log_callback(f"[EXPORT] Error getting table list: {e}")
            return []
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get information about a specific table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with table information
        """
        if not self.database_path or not os.path.exists(self.database_path):
            return {"error": "Database not available"}
        
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Get table schema
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                
                return {
                    "table_name": table_name,
                    "columns": [{"name": col[1], "type": col[2], "not_null": bool(col[3])} for col in columns],
                    "row_count": row_count,
                    "column_count": len(columns)
                }
        
        except Exception as e:
            return {"error": str(e)}
    
    def cleanup_old_exports(self, days_threshold: int = 30) -> Dict[str, Any]:
        """
        Clean up old export files
        
        Args:
            days_threshold: Files older than this many days will be deleted
            
        Returns:
            Cleanup operation summary
        """
        try:
            import time
            
            threshold_time = time.time() - (days_threshold * 24 * 3600)
            files_deleted = 0
            space_freed = 0
            
            if self.default_export_dir.exists():
                for file_path in self.default_export_dir.iterdir():
                    if file_path.is_file() and file_path.stat().st_mtime < threshold_time:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        files_deleted += 1
                        space_freed += file_size
            
            self.log_callback(f"[EXPORT] Cleanup: {files_deleted} files deleted, {space_freed/1024/1024:.1f} MB freed")
            
            return {
                "files_deleted": files_deleted,
                "space_freed_mb": round(space_freed / 1024 / 1024, 1),
                "threshold_days": days_threshold
            }
        
        except Exception as e:
            self.log_callback(f"[EXPORT] Cleanup error: {e}")
            return {"error": str(e)}