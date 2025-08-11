#!/usr/bin/env python3
"""
Database Monitoring Script for Encrypted Backup Framework
Provides automated monitoring, alerting, and maintenance scheduling.
"""

import sys
import os
import time
import json
import logging
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    schedule = None
from datetime import datetime, timedelta
from typing import Dict, Any

# Setup standardized import paths
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from Shared.path_utils import setup_imports
setup_imports()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseMonitor:
    """Database monitoring and maintenance automation."""
    
    def __init__(self, db_path: str = "defensive.db"):
        self.db_path = db_path
        self.alert_thresholds = {
            'max_db_size_mb': 100,
            'max_storage_size_mb': 1000,
            'min_verification_rate': 80,
            'max_days_since_seen': 7,
            'max_failed_clients': 10
        }
        self.maintenance_log = "maintenance.log"
        
    def check_database_health(self) -> Dict[str, Any]:
        """Perform comprehensive database health check."""
        try:
            from database import DatabaseManager
            
            db = DatabaseManager(self.db_path, use_pool=True)
            
            # Get health status
            health = db.get_database_health()
            stats = db.get_storage_statistics()
            
            # Build health report
            report = {
                'timestamp': datetime.now().isoformat(),
                'database_healthy': health['integrity_check'],
                'connection_pool_healthy': health['connection_pool_healthy'],
                'tables': health['table_count'],
                'indexes': health['index_count'],
                'issues': health['issues']
            }
            
            # Add storage metrics
            if 'database_info' in stats:
                db_info = stats['database_info']
                report['database_size_mb'] = db_info['file_size_mb']
                report['connection_pool_enabled'] = db_info['connection_pool_enabled']
                
            if 'storage_info' in stats:
                storage_info = stats['storage_info']
                report['storage_files'] = storage_info['total_files']
                report['storage_size_mb'] = storage_info['total_size_mb']
                
            if 'client_stats' in stats:
                client_stats = stats['client_stats']
                report['total_clients'] = client_stats['total_clients']
                report['clients_with_keys'] = client_stats['clients_with_keys']
                report['avg_days_since_seen'] = client_stats['average_days_since_seen']
                
            if 'file_stats' in stats:
                file_stats = stats['file_stats']
                report['total_files'] = file_stats['total_files']
                report['verification_rate'] = file_stats['verification_rate']
                report['total_storage_gb'] = file_stats['total_size_gb']
            
            return report
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'database_healthy': False
            }
    
    def check_alerts(self, health_report: Dict[str, Any]) -> list:
        """Check health report against alert thresholds."""
        alerts = []
        
        # Database integrity alerts
        if not health_report.get('database_healthy', False):
            alerts.append({
                'level': 'CRITICAL',
                'message': 'Database integrity check failed',
                'details': health_report.get('issues', [])
            })
            
        # Connection pool alerts
        if not health_report.get('connection_pool_healthy', False):
            alerts.append({
                'level': 'WARNING',
                'message': 'Connection pool health issues detected'
            })
        
        # Size alerts
        db_size = health_report.get('database_size_mb', 0)
        if db_size > self.alert_thresholds['max_db_size_mb']:
            alerts.append({
                'level': 'WARNING',
                'message': f'Database size ({db_size} MB) exceeds threshold ({self.alert_thresholds["max_db_size_mb"]} MB)'
            })
            
        storage_size = health_report.get('storage_size_mb', 0)
        if storage_size > self.alert_thresholds['max_storage_size_mb']:
            alerts.append({
                'level': 'WARNING',
                'message': f'Storage size ({storage_size} MB) exceeds threshold ({self.alert_thresholds["max_storage_size_mb"]} MB)'
            })
        
        # Verification rate alerts
        verification_rate = health_report.get('verification_rate', 100)
        if verification_rate < self.alert_thresholds['min_verification_rate']:
            alerts.append({
                'level': 'WARNING',
                'message': f'File verification rate ({verification_rate}%) below threshold ({self.alert_thresholds["min_verification_rate"]}%)'
            })
        
        # Client activity alerts
        avg_days = health_report.get('avg_days_since_seen', 0)
        if avg_days > self.alert_thresholds['max_days_since_seen']:
            alerts.append({
                'level': 'INFO',
                'message': f'Average client inactivity ({avg_days:.1f} days) exceeds threshold ({self.alert_thresholds["max_days_since_seen"]} days)'
            })
        
        return alerts
    
    def send_alerts(self, alerts: list):
        """Send alerts via configured channels."""
        if not alerts:
            return
            
        logger.info(f"Sending {len(alerts)} alerts")
        
        for alert in alerts:
            level = alert['level']
            message = alert['message']
            details = alert.get('details', [])
            
            log_func = logger.info
            if level == 'WARNING':
                log_func = logger.warning
            elif level == 'CRITICAL':
                log_func = logger.critical
                
            log_func(f"ALERT [{level}]: {message}")
            if details:
                for detail in details:
                    log_func(f"  - {detail}")
        
        # Here you could add email, Slack, or other notification integrations
        # Example:
        # self.send_email_alerts(alerts)
        # self.send_slack_alerts(alerts)
    
    def perform_maintenance(self) -> Dict[str, Any]:
        """Perform automated database maintenance."""
        logger.info("Starting automated database maintenance")
        
        try:
            from database import DatabaseManager
            
            db = DatabaseManager(self.db_path, use_pool=True)
            
            # Optimization
            logger.info("Performing database optimization...")
            optimization_results = db.optimize_database()
            
            # Backup
            logger.info("Creating database backup...")
            backup_path = db.backup_database_to_file()
            
            # Health check after maintenance
            health = db.get_database_health()
            
            results = {
                'timestamp': datetime.now().isoformat(),
                'optimization': optimization_results,
                'backup_path': backup_path,
                'post_maintenance_health': health,
                'success': True
            }
            
            logger.info("Database maintenance completed successfully")
            logger.info(f"Space saved: {optimization_results.get('space_saved_mb', 0)} MB")
            logger.info(f"Backup created: {backup_path}")
            
            # Log maintenance results
            self.log_maintenance(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Database maintenance failed: {e}")
            results = {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'success': False
            }
            self.log_maintenance(results)
            return results
    
    def log_maintenance(self, results: Dict[str, Any]):
        """Log maintenance results to file."""
        try:
            with open(self.maintenance_log, 'a') as f:
                f.write(json.dumps(results) + '\n')
        except Exception as e:
            logger.error(f"Failed to log maintenance results: {e}")
    
    def run_monitoring_cycle(self):
        """Run a single monitoring cycle."""
        logger.info("Running database monitoring cycle")
        
        # Health check
        health_report = self.check_database_health()
        
        # Check for alerts
        alerts = self.check_alerts(health_report)
        
        # Send alerts if any
        if alerts:
            self.send_alerts(alerts)
        else:
            logger.info("No alerts detected")
        
        # Log health report
        logger.info(f"Database health: {'OK' if health_report.get('database_healthy') else 'ISSUES'}")
        logger.info(f"Total clients: {health_report.get('total_clients', 0)}")
        logger.info(f"Total files: {health_report.get('total_files', 0)}")
        logger.info(f"Database size: {health_report.get('database_size_mb', 0)} MB")
        
        return health_report, alerts
    
    def setup_scheduler(self):
        """Setup automated monitoring and maintenance schedule."""
        if not SCHEDULE_AVAILABLE:
            logger.error("Schedule module not available. Install with: pip install schedule")
            return False
            
        logger.info("Setting up monitoring scheduler")
        
        # Health checks every 15 minutes
        schedule.every(15).minutes.do(self.run_monitoring_cycle)
        
        # Daily maintenance at 2 AM
        schedule.every().day.at("02:00").do(self.perform_maintenance)
        
        # Weekly detailed health report on Sunday at 1 AM
        schedule.every().sunday.at("01:00").do(self.generate_weekly_report)
        
        logger.info("Monitoring scheduler configured:")
        logger.info("  - Health checks: Every 15 minutes")
        logger.info("  - Maintenance: Daily at 2:00 AM")
        logger.info("  - Weekly reports: Sunday at 1:00 AM")
        return True
    
    def generate_weekly_report(self):
        """Generate weekly database health report."""
        logger.info("Generating weekly database report")
        
        try:
            health_report = self.check_database_health()
            
            report = {
                'report_type': 'weekly',
                'timestamp': datetime.now().isoformat(),
                'health_summary': health_report,
                'recommendations': self.generate_recommendations(health_report)
            }
            
            # Save report
            report_filename = f"weekly_report_{datetime.now().strftime('%Y%m%d')}.json"
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Weekly report saved: {report_filename}")
            
        except Exception as e:
            logger.error(f"Failed to generate weekly report: {e}")
    
    def generate_recommendations(self, health_report: Dict[str, Any]) -> list:
        """Generate maintenance and optimization recommendations."""
        recommendations = []
        
        db_size = health_report.get('database_size_mb', 0)
        verification_rate = health_report.get('verification_rate', 100)
        total_files = health_report.get('total_files', 0)
        
        if db_size > 50:
            recommendations.append("Consider database optimization to reclaim space")
            
        if verification_rate < 90:
            recommendations.append("Review file verification process - low verification rate detected")
            
        if total_files > 1000:
            recommendations.append("Consider implementing file archiving for old files")
        
        if not health_report.get('connection_pool_enabled', True):
            recommendations.append("Enable connection pooling for better performance")
            
        if health_report.get('avg_days_since_seen', 0) > 30:
            recommendations.append("Review client activity - many inactive clients detected")
            
        return recommendations
    
    def run_daemon(self):
        """Run monitoring daemon."""
        logger.info("Starting database monitoring daemon")
        
        if not self.setup_scheduler():
            logger.error("Cannot start daemon without schedule module")
            return
        
        # Run initial health check
        logger.info("Performing initial health check")
        self.run_monitoring_cycle()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Monitoring daemon stopped by user")
        except Exception as e:
            logger.error(f"Monitoring daemon error: {e}")


def main():
    """Main entry point for database monitoring."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Monitoring for Encrypted Backup Framework")
    parser.add_argument("--database", "-d", default="defensive.db", help="Database file path")
    parser.add_argument("--daemon", action="store_true", help="Run as monitoring daemon")
    parser.add_argument("--check", action="store_true", help="Run single health check")
    parser.add_argument("--maintenance", action="store_true", help="Run maintenance tasks")
    parser.add_argument("--weekly-report", action="store_true", help="Generate weekly report")
    
    args = parser.parse_args()
    
    monitor = DatabaseMonitor(args.database)
    
    try:
        if args.daemon:
            monitor.run_daemon()
        elif args.check:
            health_report, alerts = monitor.run_monitoring_cycle()
            print(json.dumps(health_report, indent=2))
        elif args.maintenance:
            results = monitor.perform_maintenance()
            print(json.dumps(results, indent=2))
        elif args.weekly_report:
            monitor.generate_weekly_report()
        else:
            # Default: single monitoring cycle
            health_report, alerts = monitor.run_monitoring_cycle()
            if alerts:
                print(f"\n{len(alerts)} alerts detected:")
                for alert in alerts:
                    print(f"  [{alert['level']}] {alert['message']}")
            else:
                print("Database health: OK")
                
    except Exception as e:
        logger.error(f"Monitoring error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())