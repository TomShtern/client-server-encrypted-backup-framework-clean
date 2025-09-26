"""
safe_date_entry.py - Safe DateEntry wrapper with fallback support.

This module provides a robust DateEntry implementation that handles tkcalendar
compatibility issues and provides graceful fallbacks when the library has problems.
"""

from __future__ import annotations

import contextlib
import tkinter as tk
from collections.abc import Callable
from datetime import date, datetime
from tkinter import ttk
from typing import Any, Protocol

# Try to import tkcalendar with comprehensive error handling
_TKCALENDAR_AVAILABLE = False
_DateEntryClass = None

try:
    from tkcalendar import DateEntry as _TkcalendarDateEntry
    _DateEntryClass = _TkcalendarDateEntry
    _TKCALENDAR_AVAILABLE = True
except ImportError:
    _TKCALENDAR_AVAILABLE = False


class DateEntryLike(Protocol):
    """Protocol for DateEntry-like widgets."""
    def pack(self, **kwargs: Any) -> None: ...
    def grid(self, **kwargs: Any) -> None: ...
    def place(self, **kwargs: Any) -> None: ...
    def bind(self, event: str, callback: Callable[..., Any]) -> None: ...
    def get_date(self) -> date: ...
    def set_date(self, new_date: date) -> None: ...
    def destroy(self) -> None: ...


class SafeDateEntry:
    """
    A safe wrapper around tkcalendar.DateEntry that handles compatibility issues
    and provides fallbacks when the library has problems.
    """

    def __init__(self, parent: tk.Widget, date_pattern: str = 'yyyy-mm-dd',
                 firstweekday: str = 'sunday', startdate: date | None = None, **kwargs):
        self.parent = parent
        self.date_pattern = date_pattern
        self._current_date = startdate or date.today()
        self._callbacks: list[Callable[..., Any]] = []
        self._widget: tk.Widget | None = None
        self._is_fallback = True  # Initialize as True until proven otherwise

        # Skip tkcalendar DateEntry due to compatibility issues - always use fallback
        # The current tkcalendar version has cleanup issues that cause AttributeError
        # when destroying widgets. Use fallback implementation for reliability.
        if False and _TKCALENDAR_AVAILABLE and _DateEntryClass:
            try:
                # Create the real widget directly - avoid test creation that can cause issues
                self._widget = _DateEntryClass(parent, date_pattern=date_pattern,
                                             firstweekday=firstweekday, **kwargs)
                if startdate:
                    with contextlib.suppress(Exception):
                        self._widget.set_date(startdate)  # type: ignore

                self._is_fallback = False
                return

            except Exception as e:
                print(f"[WARNING] tkcalendar DateEntry failed: {e}, using fallback")
                # Clean up any partial widgets
                with contextlib.suppress(Exception):
                    if hasattr(self, '_widget') and self._widget:
                        self._widget.destroy()
                        self._widget = None

        # Create fallback widget
        self._create_fallback_widget(kwargs)
        self._is_fallback = True

    def _create_fallback_widget(self, kwargs: dict[str, Any]) -> None:
        """Create a simple Entry widget as fallback."""
        frame = ttk.Frame(self.parent)

        self._entry = ttk.Entry(frame, width=12)
        self._entry.pack(side=tk.LEFT)
        self._entry.insert(0, self._current_date.strftime('%Y-%m-%d'))
        self._entry.bind('<FocusOut>', self._on_entry_change)
        self._entry.bind('<Return>', self._on_entry_change)

        # Add a calendar button for better UX
        cal_btn = ttk.Button(frame, text="📅", width=3,
                           command=self._show_simple_calendar)
        cal_btn.pack(side=tk.LEFT, padx=(2, 0))

        self._widget = frame

    def _on_entry_change(self, event: tk.Event | None = None) -> None:
        """Handle entry change in fallback mode."""
        if not hasattr(self, '_entry'):
            return

        try:
            date_str = self._entry.get()
            # Try to parse the date
            if len(date_str) == 10 and date_str.count('-') == 2:
                parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                self._current_date = parsed_date
                self._trigger_callbacks()
        except ValueError:
            # Reset to current date if invalid
            self._entry.delete(0, tk.END)
            self._entry.insert(0, self._current_date.strftime('%Y-%m-%d'))

    def _show_simple_calendar(self) -> None:
        """Show a simple calendar picker."""
        # For now, just focus the entry - could be enhanced with a popup calendar
        if hasattr(self, '_entry'):
            self._entry.focus()

    def _trigger_callbacks(self) -> None:
        """Trigger registered callbacks."""
        for callback in self._callbacks:
            try:
                callback()
            except Exception as e:
                print(f"[WARNING] DateEntry callback error: {e}")

    def pack(self, **kwargs: Any) -> None:
        """Pack the widget."""
        if self._widget:
            self._widget.pack(**kwargs)

    def grid(self, **kwargs: Any) -> None:
        """Grid the widget."""
        if self._widget:
            self._widget.grid(**kwargs)

    def place(self, **kwargs: Any) -> None:
        """Place the widget."""
        if self._widget:
            self._widget.place(**kwargs)

    def get_date(self) -> date:
        """Get the current date."""
        if self._is_fallback:
            return self._current_date
        else:
            try:
                return self._widget.get_date()  # type: ignore
            except Exception:
                return self._current_date

    def set_date(self, new_date: date) -> None:
        """Set the date."""
        self._current_date = new_date
        if self._is_fallback:
            if hasattr(self, '_entry'):
                self._entry.delete(0, tk.END)
                self._entry.insert(0, new_date.strftime('%Y-%m-%d'))
        else:
            try:
                self._widget.set_date(new_date)  # type: ignore
            except Exception:
                pass

    def bind(self, event: str, callback: Callable[..., Any]) -> None:
        """Bind an event callback."""
        if self._is_fallback:
            if event == "<<DateEntrySelected>>":
                self._callbacks.append(lambda: callback(None))
            elif hasattr(self, '_entry'):
                # Map other events to entry widget
                self._entry.bind(event, callback)
        else:
            try:
                self._widget.bind(event, callback)  # type: ignore
            except Exception:
                pass

    def destroy(self) -> None:
        """Safely destroy the widget."""
        try:
            if self._widget:
                # Handle tkcalendar cleanup issues
                if not self._is_fallback:
                    # For tkcalendar DateEntry, be extra careful with cleanup
                    with contextlib.suppress(Exception):
                        # Try to cancel the problematic after_id that causes the error
                        problematic_attrs = [
                            '_determine_downarrow_name_after_id',
                            '_determine_uparrow_name_after_id',
                            'after_id',
                            '_after_id'
                        ]

                        for attr_name in problematic_attrs:
                            if hasattr(self._widget, attr_name):
                                after_id = getattr(self._widget, attr_name, None)
                                if after_id and isinstance(after_id, (int, str)):
                                    try:
                                        self._widget.after_cancel(after_id)  # type: ignore
                                        # Clear the attribute to prevent double-cancel
                                        setattr(self._widget, attr_name, None)
                                    except Exception:
                                        pass

                self._widget.destroy()
                self._widget = None
        except Exception:
            # Don't print the error as it's expected with tkcalendar issues
            pass


def create_safe_date_entry(parent: tk.Widget, **kwargs: Any) -> DateEntryLike:
    """
    Factory function to create a safe DateEntry.
    
    This function attempts to create a working DateEntry and falls back to
    a simple implementation if tkcalendar has compatibility issues.
    """
    return SafeDateEntry(parent, **kwargs)
