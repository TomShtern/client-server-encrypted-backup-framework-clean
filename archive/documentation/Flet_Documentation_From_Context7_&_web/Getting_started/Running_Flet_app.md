# Running Flet app

A Flet application can be run as a desktop application.

**To run as a desktop app:**
Use the `flet run` command. This will execute the `main.py` file in the current directory.
```bash
flet run
```
To run a different script or a script in another directory, you can provide a path:
```bash
flet run /path/to/your/app_directory
# or
flet run your_script.py
```

**Hot Reload:**
Flet automatically reloads the app when the main script file is changed. To watch for changes in all files within the script's directory, use the `-d` flag. For recursive watching, add the `-r` flag.
```bash
# Watch directory
flet run -d your_script.py

# Watch directory and subdirectories
flet run -d -r your_script.py
```
