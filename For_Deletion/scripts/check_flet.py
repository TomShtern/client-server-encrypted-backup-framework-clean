import flet as ft

print(f"Flet version: {ft.version}")
try:
    print(f"ft.alignment.center: {ft.alignment.center}")
except AttributeError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Other Error: {e}")
