# ThemeMode

The `ThemeMode` enum in Flet is used to specify the theme mode for an application or a specific control. It has the following values:

*   **`SYSTEM`**: Uses the theme mode (light or dark) that is currently set by the operating system.
*   **`LIGHT`**: Forces the application or control to use the light theme, regardless of the system settings.
*   **`DARK`**: Forces the application or control to use the dark theme, regardless of the system settings.

The `Page` control, which is the uppermost control in the Flet application, has a `theme_mode` property that defaults to `ThemeMode.SYSTEM`. You can configure the appearance for light and dark theme modes using the `page.theme` and `page.dark_theme` properties, respectively. Some container-like controls also have `theme_mode` properties, allowing for nested themes where a part of the app can use a different theme or override some theme styles.
