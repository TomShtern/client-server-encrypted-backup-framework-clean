# Create a new Flet app

To create a new Flet app, you first need to create a new directory and switch into it.

Then, run the following command:
`flet create`

If you are using a virtual environment with `uv` or `poetry`, you would use `uv run flet create` or `poetry run flet create` respectively.

This command will generate a new project structure for your Flet app, which includes:
*   `README.md`
*   `pyproject.toml`
*   `src/assets/icon.png`
*   `src/main.py` (This is where your main application code goes)
*   `storage/` directory

The main entry point of your application is the `main()` function within `src/main.py`, where you add UI controls to the page. The application is started by calling `ft.app()`.

Please note that you need to have Git installed for the `flet create` command to work. After creating the app, the next step is to run it.
