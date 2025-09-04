# MarkdownSelectionChangeEvent

`Flet MarkdownSelectionChangeEvent` is an event type in the Flet framework that is associated with the `ft.Markdown` control.

Here's a breakdown:
*   **Purpose**: This event fires when the text selection changes within a `ft.Markdown` control. This means if a user selects a different portion of the text, or changes the cursor's position, this event will be triggered.
*   **Usage**: You can attach an event handler to the `on_selection_change` property of an `ft.Markdown` control. The event handler function will receive an argument of type `MarkdownSelectionChangeEvent`.
*   **Related Enum**: The `MarkdownSelectionChangeCause` enum provides information about *why* the selection change occurred (e.g., `TAP`, `DOUBLE_TAP`, `TOOLBAR`). However, it's important to note that `MarkdownSelectionChangeCause` is deprecated as of Flet v0.25.0 and is scheduled for removal in v0.28.0. The documentation suggests using `TextSelectionChangeCause` instead.

**Example of how to use it (conceptual):**

```python
import flet as ft

def main(page: ft.Page):
    def on_markdown_selection_changed(e: ft.MarkdownSelectionChangeEvent):
        # 'e' will be an instance of MarkdownSelectionChangeEvent
        # You can access properties of the event object here,
        # such as the selected text or the cause of the selection change.
        # Note: Specific properties of MarkdownSelectionChangeEvent are not detailed in the search results,
        # but typically include information about the selection.
        print(f"Markdown selection changed. Cause: {e.cause}")
        # If you need the selected text, you might need to access it from the Markdown control itself
        # or if the event object provides it.

    markdown_content = """
    # Welcome to Flet Markdown
    This is some **sample** text.
    You can select parts of this text to trigger the event.
    """

    md_control = ft.Markdown(
        markdown_content,
        on_selection_change=on_markdown_selection_changed,
        expand=True,
    )

    page.add(md_control)

ft.app(target=main)
```
