import os
import pkgutil

import flet as ft

print("Flet location:", ft.__file__)
try:
    print("Flet version:", ft.version.version)
except:
    print("Flet version attribute missing")

print("\n--- Top Level Attributes ---")
attrs = dir(ft)
charts = [
    a
    for a in attrs
    if "chart" in a.lower() or "graph" in a.lower() or "plot" in a.lower()
]
print("Chart related attributes:", charts)

print("\n--- Submodules ---")
try:
    path = os.path.dirname(ft.__file__)
    modules = [name for _, name, _ in pkgutil.iter_modules([path])]
    print("Available submodules:", modules)
except Exception as e:
    print(f"Error listing submodules: {e}")

print("\n--- Checking flet.charts ---")
try:
    import flet.charts

    print("flet.charts imported successfully")
    print(dir(flet.charts))
except ImportError:
    print("flet.charts import failed")

print("\n--- Checking flet.plotting ---")
try:
    import flet.plotting

    print("flet.plotting imported successfully")
except ImportError:
    print("flet.plotting import failed")
