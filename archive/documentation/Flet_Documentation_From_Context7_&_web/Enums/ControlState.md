# ControlState

The `ControlState` enum in Flet represents the various visual and interactive states that a control can be in. These states are used to provide visual feedback to the user and to manage the control's behavior based on user interaction or internal conditions. The `ControlState` enum has the following values:

*   **DEFAULT**: Represents the baseline state of a control when no other states are active. It serves as a fallback and has the lowest priority in the state hierarchy.
*   **DISABLED**: Indicates that the control is disabled, non-interactive, and visually subdued.
*   **DRAGGED**: Represents a state where the user is actively dragging the control.
*   **ERROR**: Indicates that the control has encountered an error or a validation issue.
*   **FOCUSED**: Denotes that the control has received keyboard or touch focus.
*   **HOVERED**: Used when the user is hovering over the control with a pointer device. This state is typically used to provide visual feedback, such as a color change or shadow effect.
*   **PRESSED**: Represents the state when the control is actively being pressed or clicked.
*   **SELECTED**: Indicates that the control is currently selected.
*   **SCROLLED_UNDER**: Used when the control has been partially or fully scrolled under another element. This state is useful for elements like sticky headers that change appearance when scrolled.

For more detailed information on each state, the Material Design specification can be consulted.
