To get started with Flet, you need Python 3.9 or above and the `flet` package. It's recommended to install Flet in a virtual environment.

**Operating System Support:**
*   macOS: 11 (Big Sur) or later
*   Windows: 64-bit Windows 10 or later
*   Linux: Debian 11 or later, Ubuntu 20.04 LTS or later (with additional prerequisites)

**Virtual Environment Setup Options:**

1.  **Using `venv` (recommended for most users):**
    *   Create a project directory: `mkdir first-flet-app && cd first-flet-app`
    *   Create and activate a virtual environment: `python3 -m venv .venv && source .venv/bin/activate` (or `.\.venv\Scripts\activate` on Windows)
    *   Install Flet: `pip install 'flet[all]'`
    *   Verify installation: `flet --version`

2.  **Using Poetry:**
    *   Install Poetry (if not already installed).
    *   Create a project: `mkdir my-app && cd my-app`
    *   Initialize Poetry with Flet: `poetry init --dev-dependency='flet[all]' --python='>=3.9' --no-interaction`
    *   Install dependencies: `poetry install --no-root`
    *   Verify installation: `poetry run flet --version`
    *   *Note: When running Flet apps with Poetry, use `poetry run` before each command.*

3.  **Using `uv`:**
    *   Install `uv`.
    *   Create a project: `mkdir my-app && cd my-app`
    *   Initialize `uv`: `uv init`
    *   Add Flet as a dependency: `uv add 'flet[all]' --dev`
    *   Verify installation: `uv run flet --version`
    *   *Note: When running Flet apps with `uv`, use `uv run` before each command.*

After setting up, you are ready to create your first Flet app.