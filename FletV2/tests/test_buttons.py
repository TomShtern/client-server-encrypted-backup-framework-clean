#!/usr/bin/env python3
"""
Minimal Button Test - Isolating DataTable Button Issues
This will test different button creation patterns to identify the root cause.
"""

import flet as ft


def main(page: ft.Page):
    page.title = "Button Test - Isolating DataTable Issues"

    # Counter to track clicks visually
    click_counter = {"count": 0}
    counter_text = ft.Text("No clicks yet", size=16)

    # Test 1: Static button (like official docs)
    def static_button_clicked(e):
        click_counter["count"] += 1
        print(f"STATIC BUTTON CLICKED! Count: {click_counter['count']}")
        counter_text.value = f"STATIC button clicked {click_counter['count']} times"
        counter_text.update()
        page.snack_bar = ft.SnackBar(ft.Text("Static button worked!"))
        page.snack_bar.open = True
        page.update()

    # Test 2: Dynamic button outside DataTable
    def dynamic_button_clicked(e):
        click_counter["count"] += 1
        print(f"DYNAMIC BUTTON CLICKED! Count: {click_counter['count']}")
        counter_text.value = f"DYNAMIC button clicked {click_counter['count']} times"
        counter_text.update()
        page.snack_bar = ft.SnackBar(ft.Text("Dynamic button worked!"))
        page.snack_bar.open = True
        page.update()

    # Test 3: Button inside DataTable (our problematic case)
    def datatable_button_clicked(e):
        click_counter["count"] += 1
        print(f"DATATABLE BUTTON CLICKED! Count: {click_counter['count']}")
        counter_text.value = f"DATATABLE button clicked {click_counter['count']} times"
        counter_text.update()
        page.snack_bar = ft.SnackBar(ft.Text("DataTable button worked!"))
        page.snack_bar.open = True
        page.update()

    # Create static button (should work)
    static_button = ft.IconButton(
        icon=ft.Icons.STAR,
        tooltip="Static Button Test",
        on_click=static_button_clicked
    )

    # Create dynamic button outside table (test dynamic creation)
    dynamic_button = ft.IconButton(
        icon=ft.Icons.FAVORITE,
        tooltip="Dynamic Button Test",
        on_click=dynamic_button_clicked
    )

    # Create DataTable with button (problematic case)
    datatable = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Actions"))
        ],
        rows=[
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("test_001")),
                ft.DataCell(ft.IconButton(
                    icon=ft.Icons.INFO,
                    tooltip="DataTable Button Test",
                    on_click=datatable_button_clicked
                ))
            ])
        ]
    )

    page.add(
        ft.Text("Button Serialization Test", size=20, weight=ft.FontWeight.BOLD),
        counter_text,  # Show click counter
        ft.Divider(),

        ft.Text("Test 1: Static Button (should work)"),
        static_button,

        ft.Divider(),
        ft.Text("Test 2: Dynamic Button (should work)"),
        dynamic_button,

        ft.Divider(),
        ft.Text("Test 3: DataTable Button (problematic)"),
        datatable
    )

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
