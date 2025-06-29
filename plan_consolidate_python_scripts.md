
# Plan: Consolidate Python Scripts

**Objective:** Refactor the numerous Python scripts in the `scripts` directory into a single, well-structured command-line interface (CLI) using Python's `argparse` module. This will improve usability, reduce code duplication, and make the project easier to manage.

**Strategy:** The current project has a large number of single-purpose Python scripts. This plan will create a new, unified script called `manage.py` that will act as a central entry point for all project-related tasks. Each of the existing scripts will be converted into a subcommand of `manage.py`.

**Pre-computation/Analysis:**

*   **Files to Consolidate:** `config_manager.py`, `cyberbackup_api_server.py`, `deep_error_analysis.py`, `find_gui_errors.py`, `generate_rsa_keys.py`, `integration_web_server.py`, `master_test_suite.py`, `quick_validation.py`, `targeted_error_finder.py`, `validate_null_check_fixes.py`, `validate_server_gui.py`.
*   **File to Create:** `manage.py`
*   **Tool to Use:** `write_file`, `replace`, `run_shell_command` (for deleting old files).

**Step-by-Step Plan:**

1.  **Create the `manage.py` CLI Framework:**
    *   **Action:** Create a new `manage.py` file in the root directory.
    *   **Action:** Use the `argparse` module to create a main parser and a subparser for commands.
    *   **Example `manage.py` structure:**
        ```python
        import argparse

        def main():
            parser = argparse.ArgumentParser(description="Project Management CLI")
            subparsers = parser.add_subparsers(dest="command", required=True)

            # Add subparsers for each command here

            args = parser.parse_args()
            if hasattr(args, 'func'):
                args.func(args)

        if __name__ == "__main__":
            main()
        ```

2.  **Migrate `generate_rsa_keys.py`:**
    *   **Action:** Create a new function in `manage.py` that encapsulates the logic from `generate_rsa_keys.py`.
    *   **Action:** Add a new subcommand to `manage.py` called `genkeys` that calls this new function.
    *   **Example:**
        ```python
        def setup_genkeys_parser(subparsers):
            parser = subparsers.add_parser("genkeys", help="Generate RSA keys.")
            parser.set_defaults(func=run_genkeys)

        def run_genkeys(args):
            # ... logic from generate_rsa_keys.py ...
        ```

3.  **Migrate the Test and Validation Scripts:**
    *   **Action:** For each of the test and validation scripts, create a new function in `manage.py` that encapsulates its logic.
    *   **Action:** Add a new subcommand to `manage.py` for each script (e.g., `test`, `validate`).
    *   **Example:**
        ```python
        def setup_test_parser(subparsers):
            parser = subparsers.add_parser("test", help="Run project tests.")
            # Add arguments for specific tests
            parser.set_defaults(func=run_tests)

        def run_tests(args):
            # ... logic from master_test_suite.py ...
        ```

4.  **Migrate the Server Scripts:**
    *   **Action:** Create a new subcommand in `manage.py` called `server` that can be used to start the various server instances (e.g., `manage.py server start --api`, `manage.py server start --web`).
    *   **Action:** Move the logic from `cyberbackup_api_server.py` and `integration_web_server.py` into functions that can be called by the `server` subcommand.

5.  **Remove the Old Scripts:**
    *   **Action:** Once all the scripts have been migrated to `manage.py`, delete the old script files from the `scripts` directory.
    *   **Verification:** The project should now be managed entirely through the `manage.py` CLI.
