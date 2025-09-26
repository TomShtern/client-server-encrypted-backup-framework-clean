"""Lightweight Flet shim for headless test environment.
Only implements minimal symbols referenced by components to allow import without real flet.
If real flet is installed, tests can import it instead. This shim is NOT a functional UI layer.
"""

class _Colors:
    GREY = "#888888"

class _FontWeight:
    BOLD = "bold"

class _ScrollMode:
    AUTO = "auto"

class Text:
    def __init__(self, value="", **kwargs):
        self.value = value

class TextField:
    def __init__(self, label="", value="", multiline=False, min_lines=1, max_lines=5, hint_text="", width=400, **kwargs):
        self.label = label
        self.value = value

class Row(list):
    def __init__(self, controls=None):
        super().__init__(controls or [])

class Column(list):
    def __init__(self, controls=None, **kwargs):
        super().__init__(controls or [])

class TextButton:
    def __init__(self, text, on_click=None, **kwargs):
        self.text = text
        self.on_click = on_click

class ElevatedButton(TextButton):
    pass

class Page:
    def __init__(self):
        self.update_calls = 0
    def update(self):
        self.update_calls += 1
    def run_task(self, coro):
        # In tests we just return the coroutine; caller can schedule if desired.
        return coro

# Namespace exports roughly mimicking flet symbols used
Colors = _Colors()
FontWeight = _FontWeight()
ScrollMode = _ScrollMode()

# Provide a minimal placeholder for ft.* attribute access patterns
__all__ = [
    'Colors',
    'Column',
    'ElevatedButton',
    'FontWeight',
    'Page',
    'Row',
    'ScrollMode',
    'Text',
    'TextButton',
    'TextField'
]
