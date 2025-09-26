#!/usr/bin/env python3
"""
Scope Issue Test - Test function reference capture in different scopes
"""

import flet as ft


def main(page: ft.Page):
    page.title = "Scope Issue Test"

    # Test 1: Direct scope (SHOULD WORK - like original test)
    def direct_handler(e):
        print("DIRECT HANDLER CLICKED!")
        page.snack_bar = ft.SnackBar(ft.Text("Direct handler worked!"))
        page.snack_bar.open = True
        page.update()

    direct_table = ft.DataTable(
        columns=[ft.DataColumn(ft.Text("Test")), ft.DataColumn(ft.Text("Actions"))],
        rows=[ft.DataRow(cells=[
            ft.DataCell(ft.Text("Direct")),
            ft.DataCell(ft.IconButton(icon=ft.Icons.STAR, on_click=direct_handler))
        ])]
    )

    # Test 2: Helper function scope (MIGHT FAIL - like production fix)
    def create_helper_table():
        def helper_handler(e):
            print("HELPER HANDLER CLICKED!")
            page.snack_bar = ft.SnackBar(ft.Text("Helper handler worked!"))
            page.snack_bar.open = True
            page.update()

        return ft.DataTable(
            columns=[ft.DataColumn(ft.Text("Test")), ft.DataColumn(ft.Text("Actions"))],
            rows=[ft.DataRow(cells=[
                ft.DataCell(ft.Text("Helper")),
                ft.DataCell(ft.IconButton(icon=ft.Icons.FAVORITE, on_click=helper_handler))
            ])]
        )

    helper_table = create_helper_table()

    # Test 3: Closure capture (MIGHT FAIL)
    def create_closure_table():
        # This creates a closure that might not serialize properly
        table_name = "Closure"

        def closure_handler(e):
            print(f"CLOSURE HANDLER CLICKED for {table_name}!")
            page.snack_bar = ft.SnackBar(ft.Text(f"Closure handler worked for {table_name}!"))
            page.snack_bar.open = True
            page.update()

        return ft.DataTable(
            columns=[ft.DataColumn(ft.Text("Test")), ft.DataColumn(ft.Text("Actions"))],
            rows=[ft.DataRow(cells=[
                ft.DataCell(ft.Text(table_name)),
                ft.DataCell(ft.IconButton(icon=ft.Icons.INFO, on_click=closure_handler))
            ])]
        )

    closure_table = create_closure_table()

    page.add(
        ft.Text("Scope Issue Test", size=20, weight=ft.FontWeight.BOLD),

        ft.Text("Test 1: Direct Scope (should work)"),
        direct_table,
        ft.Divider(),

        ft.Text("Test 2: Helper Function Scope (might fail)"),
        helper_table,
        ft.Divider(),

        ft.Text("Test 3: Closure Scope (might fail)"),
        closure_table
    )

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
