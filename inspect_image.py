import inspect

import flet as ft

print("Inspect ft.Image constructor:")
try:
    sig = inspect.signature(ft.Image.__init__)
    print(sig)
except Exception as e:
    print(f"Error inspecting Image: {e}")

print("\nInspect ft.Image properties (dir):")
print([p for p in dir(ft.Image) if not p.startswith("_")])
