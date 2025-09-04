# CrossAxisAlignment

The `CrossAxisAlignment` enum in Flet defines how children should be placed along the cross axis within a flex layout, such as `Column` or `Row`.

It has the following values:
*   **`START`**: Places the children with their start edge aligned with the start side of the cross axis. For example, in a `Column` (vertical axis), this aligns children to the left.
*   **`CENTER`**: Places the children so that their centers align with the middle of the cross axis. This is often the default alignment.
*   **`END`**: Places the children as close to the end of the cross axis as possible. For example, in a `Column`, this aligns children to the right.
*   **`STRETCH`**: Requires the children to fill the cross axis, causing the constraints passed to the children to be tight in the cross axis.
*   **`BASELINE`**: Places the children along the cross axis such that their baselines match. This is particularly useful for horizontal main axes (like in a `Row`) when children primarily contain text.
