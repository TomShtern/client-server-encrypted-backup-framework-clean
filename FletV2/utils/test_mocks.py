#!/usr/bin/env python3
"""
Mock Classes for FletV2
Utility mock classes for simulating Flet events and controls during testing and initialization.
"""

class MockEvent:
    """
    Simulate a Flet event for testing and initialization purposes.
    
    Args:
        value: The value to assign to the mock control
    """
    def __init__(self, value):
        self.control = MockControl(value)


class MockControl:
    """
    Simulate a Flet control with a value attribute.
    
    Args:
        value: The value for the mock control
    """
    def __init__(self, value):
        self.value = value