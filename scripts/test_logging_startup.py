#!/usr/bin/env python3
import logging
import time

# Small test to exercise setup_dual_logging startup messages (CODE-MAP)
from Shared.logging_utils import setup_dual_logging

logger, log_file = setup_dual_logging(
    logger_name="test_startup",
    server_type="backup-server-test",
    console_level=logging.INFO,
    file_level=logging.DEBUG,
)

print('\n[TEST] Log file created at:', log_file)
logger.info('This is a test INFO message after startup banner')
logger.warning('This is a test WARNING message after startup banner')
logger.error('This is a test ERROR message after startup banner')

# Allow log handlers to flush
time.sleep(0.2)

# Show tail of file for quick verification
try:
    with open(log_file, encoding='utf-8') as f:
        lines = f.readlines()
    print('\n[TEST] Last 10 lines from log file:')
    for line in lines[-10:]:
        print(line.rstrip())
except Exception as e:
    print('[TEST] Could not read log file:', e)
