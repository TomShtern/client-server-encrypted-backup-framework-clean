#!/usr/bin/env python3
"""
Unit tests for the debug setup module.
"""

import os
import sys
import unittest

# Add the FletV2 directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.debug_setup import get_logger, setup_terminal_debugging


class TestDebugSetup(unittest.TestCase):
    """Test cases for the debug setup module."""

    def test_setup_terminal_debugging(self):
        """Test setting up terminal debugging."""
        # Test that the function returns a logger
        logger = setup_terminal_debugging(logger_name="test_logger")
        self.assertIsNotNone(logger)

    def test_get_logger(self):
        """Test getting a logger."""
        # Test that the function returns a logger
        logger = get_logger("test_logger")
        self.assertIsNotNone(logger)

    def test_logger_has_correct_name(self):
        """Test that the logger has the correct name."""
        logger = get_logger("test_logger")
        self.assertEqual(logger.name, "test_logger")


if __name__ == '__main__':
    unittest.main()
