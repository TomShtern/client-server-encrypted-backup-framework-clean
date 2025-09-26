#!/usr/bin/env python3
"""
DataTable Button Fix Test - Testing Static vs Dynamic Row Creation
This tests whether DataTable buttons work when created statically vs dynamically.
"""

import flet as ft


def main(page: ft.Page):
    page.title = "DataTable Button Fix Test"

    # Counter to track clicks visually
    click_counter = {"count": 0}
    counter_text = ft.Text("No clicks yet", size=16)

    def button_clicked(e):
        click_counter["count"] += 1
        button_type = e.control.data if hasattr(e.control, 'data') and e.control.data else "Unknown"
        print(f"BUTTON CLICKED! Type: {button_type}, Count: {click_counter['count']}")
        counter_text.value = f"{button_type} button clicked {click_counter['count']} times total"
        counter_text.update()
        page.snack_bar = ft.SnackBar(ft.Text(f"{button_type} button worked!"))
        page.snack_bar.open = True
        page.update()

    # Test 1: Static DataTable (buttons created at init - SHOULD WORK)
    static_datatable = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Actions"))
        ],
        rows=[
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("static_001")),
                ft.DataCell(ft.IconButton(
                    icon=ft.Icons.INFO,
                    tooltip="Static DataTable Button",
                    data="Static",
                    on_click=button_clicked
                ))
            ])
        ]
    )

    # Test 2: Dynamic DataTable (buttons added after creation - MIGHT FAIL)
    dynamic_datatable = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Actions"))
        ],
        rows=[]  # Empty initially, like our complex app
    )

    # Add dynamic row (simulating our complex app pattern)
    dynamic_row = ft.DataRow(cells=[
        ft.DataCell(ft.Text("dynamic_001")),
        ft.DataCell(ft.IconButton(
            icon=ft.Icons.STAR,
            tooltip="Dynamic DataTable Button",
            data="Dynamic",
            on_click=button_clicked
        ))
    ])
    dynamic_datatable.rows.append(dynamic_row)

    # Test 3: Dynamic DataTable with update() call
    dynamic_updated_datatable = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Actions"))
        ],
        rows=[]
    )

    # Add dynamic row and call update()
    updated_row = ft.DataRow(cells=[
        ft.DataCell(ft.Text("updated_001")),
        ft.DataCell(ft.IconButton(
            icon=ft.Icons.FAVORITE,
            tooltip="Updated DataTable Button",
            data="Updated",
            on_click=button_clicked
        ))
    ])
    dynamic_updated_datatable.rows.append(updated_row)

    page.add(
        ft.Text("DataTable Button Fix Test", size=20, weight=ft.FontWeight.BOLD),
        counter_text,
        ft.Divider(),

        ft.Text("Test 1: Static DataTable (buttons at init)"),
        static_datatable,

        ft.Divider(),
        ft.Text("Test 2: Dynamic DataTable (buttons added after)"),
        dynamic_datatable,

        ft.Divider(),
        ft.Text("Test 3: Dynamic with update()"),
        dynamic_updated_datatable
    )

    # Update the dynamic datatable after adding to page
    dynamic_updated_datatable.update()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
