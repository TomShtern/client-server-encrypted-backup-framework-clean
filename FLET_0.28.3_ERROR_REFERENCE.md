# Flet 0.28.3 Common Errors and Solutions Reference

**Last Updated**: January 13, 2025
**Version**: Flet 0.28.3
**Purpose**: Comprehensive error reference for Flet code generation and debugging

---

## Table of Contents

1. [Control Initialization Errors](#1-control-initialization-errors)
2. [Layout and Positioning Errors](#2-layout-and-positioning-errors)
3. [Theme and Styling Errors](#3-theme-and-styling-errors)
4. [Event Handler Errors](#4-event-handler-errors)
5. [State Management and Update Errors](#5-state-management-and-update-errors)
6. [Navigation and Routing Errors](#6-navigation-and-routing-errors)
7. [Async/Await Integration Errors](#7-asyncawait-integration-errors)
8. [DataTable and Complex Controls Errors](#8-datatable-and-complex-controls-errors)
9. [TextField and Form Control Errors](#9-textfield-and-form-control-errors)
10. [Import and Module Errors](#10-import-and-module-errors)

---

## 1. Control Initialization Errors

### Error 1.1: Incorrect Container Border Syntax

❌ **WRONG**:
```python
container = ft.Container(
    border="1px solid black",  # String syntax not supported
    content=ft.Text("Hello")
)
```

✅ **CORRECT**:
```python
container = ft.Container(
    border=ft.border.all(1, ft.colors.BLACK),
    content=ft.Text("Hello")
)
```

📝 **Notes**:
- Flet uses `ft.border.all()`, `ft.border.only()`, `ft.border.symmetric()` methods
- Border color must be from `ft.colors` enum or valid color string

---

### Error 1.2: Incorrect Shadow Syntax

❌ **WRONG**:
```python
container = ft.Container(
    shadow="0px 4px 8px rgba(0,0,0,0.2)",  # CSS-style string not supported
    content=ft.Text("Card")
)
```

✅ **CORRECT**:
```python
container = ft.Container(
    shadow=ft.BoxShadow(
        spread_radius=1,
        blur_radius=15,
        color=ft.colors.BLUE_GREY_300,
        offset=ft.Offset(0, 4),
        blur_style=ft.ShadowBlurStyle.NORMAL
    ),
    content=ft.Text("Card")
)
```

📝 **Notes**:
- `BoxShadow` object required for custom shadows
- Can also use `elevation` parameter for Material Design elevation
- Multiple shadows: pass list of `BoxShadow` objects

---

### Error 1.3: Incorrect Padding/Margin Syntax

❌ **WRONG**:
```python
container = ft.Container(
    padding="10px 20px",  # CSS-style string not supported
    margin="10",
    content=ft.Text("Content")
)
```

✅ **CORRECT**:
```python
# Option 1: Uniform padding/margin
container = ft.Container(
    padding=10,  # All sides
    margin=10,   # All sides
    content=ft.Text("Content")
)

# Option 2: Specific sides
container = ft.Container(
    padding=ft.padding.only(left=10, right=20, top=5, bottom=5),
    margin=ft.margin.symmetric(horizontal=10, vertical=5),
    content=ft.Text("Content")
)

# Option 3: All sides explicitly
container = ft.Container(
    padding=ft.padding.all(10),
    margin=ft.margin.all(10),
    content=ft.Text("Content")
)
```

📝 **Notes**:
- Single number applies to all sides
- Use `ft.padding.only()`, `ft.padding.symmetric()`, `ft.padding.all()` for specific control
- Same applies to `ft.margin`

---

### Error 1.4: Incorrect Border Radius Syntax

❌ **WRONG**:
```python
container = ft.Container(
    border_radius="10px",  # String not supported
    content=ft.Text("Rounded")
)
```

✅ **CORRECT**:
```python
# Option 1: Uniform radius
container = ft.Container(
    border_radius=10,
    content=ft.Text("Rounded")
)

# Option 2: Specific corners
container = ft.Container(
    border_radius=ft.border_radius.only(
        top_left=10,
        top_right=10,
        bottom_left=0,
        bottom_right=0
    ),
    content=ft.Text("Rounded top only")
)
```

📝 **Notes**:
- Single number for uniform radius
- Use `ft.border_radius.only()` for specific corners
- Use `ft.border_radius.all()` explicitly if needed

---

## 2. Layout and Positioning Errors

### Error 2.1: Incorrect Expand Usage

❌ **WRONG**:
```python
# Using expand without expandable parent
page.add(
    ft.Container(
        expand=True,  # Parent (page) doesn't support expand
        content=ft.Text("Fill space")
    )
)
```

✅ **CORRECT**:
```python
# Use within Column/Row
page.add(
    ft.Column([
        ft.Container(
            expand=True,  # Expands within Column
            bgcolor=ft.colors.BLUE_100,
            content=ft.Text("Fills available vertical space")
        )
    ])
)

# Proportional expansion
page.add(
    ft.Row([
        ft.Container(expand=1, bgcolor=ft.colors.RED_100),  # 25%
        ft.Container(expand=3, bgcolor=ft.colors.BLUE_100),  # 75%
    ])
)
```

📝 **Notes**:
- `expand` only works in `Column`, `Row`, `ResponsiveRow`
- Boolean `expand=True` fills all available space
- Numeric values (1, 2, 3) create proportional expansion
- Formula: `expand_value / sum(all_expands) * 100%`

---

### Error 2.2: Incorrect Alignment Enum Values

❌ **WRONG**:
```python
column = ft.Column(
    alignment="center",  # String not supported
    horizontal_alignment="start",  # String not supported
    controls=[ft.Text("Item 1"), ft.Text("Item 2")]
)
```

✅ **CORRECT**:
```python
column = ft.Column(
    alignment=ft.MainAxisAlignment.CENTER,
    horizontal_alignment=ft.CrossAxisAlignment.START,
    controls=[ft.Text("Item 1"), ft.Text("Item 2")]
)
```

📝 **Notes**:
- **MainAxisAlignment** (main axis - vertical for Column, horizontal for Row):
  - `START`, `CENTER`, `END`
  - `SPACE_BETWEEN`, `SPACE_AROUND`, `SPACE_EVENLY`
- **CrossAxisAlignment** (cross axis):
  - `START`, `CENTER`, `END`, `STRETCH`, `BASELINE`

---

### Error 2.3: Incorrect ScrollMode Values

❌ **WRONG**:
```python
column = ft.Column(
    scroll="auto",  # String not supported
    controls=[...]
)
```

✅ **CORRECT**:
```python
column = ft.Column(
    scroll=ft.ScrollMode.AUTO,  # Use enum
    controls=[...]
)

# Available scroll modes:
# ft.ScrollMode.NONE - No scrolling
# ft.ScrollMode.AUTO - Scroll when content overflows
# ft.ScrollMode.ADAPTIVE - Platform-specific scrolling
# ft.ScrollMode.ALWAYS - Always show scrollbar
# ft.ScrollMode.HIDDEN - Scrolling enabled, scrollbar hidden
```

📝 **Notes**:
- Always use `ft.ScrollMode` enum
- `AUTO` is most common for overflow handling
- `HIDDEN` useful for custom scrollbar styling

---

### Error 2.4: ResponsiveRow Column Syntax

❌ **WRONG**:
```python
page.add(
    ft.ResponsiveRow([
        ft.Container(
            columns={"sm": 6, "md": 4},  # Wrong property name
            content=ft.Text("Responsive")
        )
    ])
)
```

✅ **CORRECT**:
```python
page.add(
    ft.ResponsiveRow([
        ft.Container(
            col={"xs": 12, "sm": 6, "md": 4, "lg": 3},  # Correct: 'col' not 'columns'
            content=ft.Text("Responsive")
        )
    ])
)
```

📝 **Notes**:
- Property is `col`, not `columns` or `column`
- Breakpoints: `xs`, `sm`, `md`, `lg`, `xl`
- Default is 12-column grid system
- Omitted breakpoints inherit from smaller sizes

---

## 3. Theme and Styling Errors

### Error 3.1: Incorrect Color Specification

❌ **WRONG**:
```python
# Using string directly for seed color
page.theme = ft.Theme(
    color_scheme_seed="blue",  # String not supported
)

# Wrong color property
container = ft.Container(
    background_color="red",  # Wrong property name
)
```

✅ **CORRECT**:
```python
# Correct seed color
page.theme = ft.Theme(
    color_scheme_seed=ft.colors.BLUE,  # Use ft.colors enum
)

# Correct color property
container = ft.Container(
    bgcolor=ft.colors.RED,  # Correct: 'bgcolor' not 'background_color'
)

# Valid color formats:
# 1. ft.colors enum: ft.colors.BLUE_500
# 2. Hex string: "#FF5722"
# 3. RGB string: "rgb(255, 87, 34)"
# 4. Named color: "red"
```

📝 **Notes**:
- Always use `ft.colors` enum for type safety
- Property is `bgcolor`, not `background_color` or `background`
- `color_scheme_seed` generates Material 3 color palette automatically

---

### Error 3.2: Incorrect Theme Structure

❌ **WRONG**:
```python
page.theme = ft.Theme(
    primary_color=ft.colors.BLUE,  # Wrong property name
    seed_color=ft.colors.GREEN,    # Wrong property name
)
```

✅ **CORRECT**:
```python
# Option 1: Use color_scheme_seed (Recommended for Material 3)
page.theme = ft.Theme(
    use_material3=True,
    color_scheme_seed=ft.colors.BLUE,
)

# Option 2: Manual ColorScheme
page.theme = ft.Theme(
    color_scheme=ft.ColorScheme(
        primary=ft.colors.BLUE,
        secondary=ft.colors.GREEN,
        surface=ft.colors.WHITE,
        background=ft.colors.GREY_50,
        error=ft.colors.RED,
    )
)
```

📝 **Notes**:
- Use `color_scheme_seed` for automatic palette generation
- For manual control, use `color_scheme` with `ColorScheme` object
- `use_material3=True` is recommended for modern apps

---

### Error 3.3: Text Theme Property Names

❌ **WRONG**:
```python
page.theme = ft.Theme(
    text_theme=ft.TextTheme(
        heading1=ft.TextStyle(size=32),  # Wrong property name
        body1=ft.TextStyle(size=16),      # Wrong property name
    )
)
```

✅ **CORRECT**:
```python
page.theme = ft.Theme(
    text_theme=ft.TextTheme(
        headline_large=ft.TextStyle(size=32, weight=ft.FontWeight.BOLD),
        headline_medium=ft.TextStyle(size=28),
        headline_small=ft.TextStyle(size=24),

        title_large=ft.TextStyle(size=22),
        title_medium=ft.TextStyle(size=16),
        title_small=ft.TextStyle(size=14),

        body_large=ft.TextStyle(size=16),
        body_medium=ft.TextStyle(size=14),
        body_small=ft.TextStyle(size=12),

        label_large=ft.TextStyle(size=14),
        label_medium=ft.TextStyle(size=12),
        label_small=ft.TextStyle(size=11),
    )
)
```

📝 **Notes**:
- Use Material 3 naming: `headline_large`, `body_medium`, etc.
- Old Material 2 names (`heading1`, `body1`) are deprecated
- Underscore notation: `headline_large` not `headlineLarge`

---

### Error 3.4: Font Weight Specification

❌ **WRONG**:
```python
text = ft.Text(
    "Bold text",
    weight="bold",  # String not supported
)

# Or
text = ft.Text(
    "Bold text",
    weight=700,  # Direct number not supported
)
```

✅ **CORRECT**:
```python
text = ft.Text(
    "Bold text",
    weight=ft.FontWeight.BOLD,
)

# Available font weights:
# ft.FontWeight.W_100 (Thin)
# ft.FontWeight.W_200 (Extra Light)
# ft.FontWeight.W_300 (Light)
# ft.FontWeight.W_400 (Normal)
# ft.FontWeight.W_500 (Medium)
# ft.FontWeight.W_600 (Semi Bold)
# ft.FontWeight.W_700 (Bold)
# ft.FontWeight.W_800 (Extra Bold)
# ft.FontWeight.W_900 (Black)

# Convenience aliases:
# ft.FontWeight.NORMAL = W_400
# ft.FontWeight.BOLD = W_700
```

📝 **Notes**:
- Always use `ft.FontWeight` enum
- Can use `W_100` through `W_900` or aliases like `BOLD`

---

## 4. Event Handler Errors

### Error 4.1: Missing Event Parameter

❌ **WRONG**:
```python
def button_clicked():  # Missing event parameter
    print("Clicked!")

button = ft.ElevatedButton(
    "Click me",
    on_click=button_clicked
)
```

✅ **CORRECT**:
```python
def button_clicked(e):  # Event parameter required
    print(f"Clicked! Control: {e.control}")

button = ft.ElevatedButton(
    "Click me",
    on_click=button_clicked
)
```

📝 **Notes**:
- ALL event handlers must accept an event parameter (commonly `e`)
- Event object contains: `e.control`, `e.data`, `e.page`
- Lambda handlers also need parameter: `on_click=lambda e: print("Clicked")`

---

### Error 4.2: Incorrect Event Handler Signature for Specific Events

❌ **WRONG**:
```python
def on_change_handler():  # Missing event parameter
    pass

textfield = ft.TextField(on_change=on_change_handler)
```

✅ **CORRECT**:
```python
def on_change_handler(e):
    new_value = e.control.value  # Access changed value
    print(f"Value changed to: {new_value}")

textfield = ft.TextField(on_change=on_change_handler)
```

📝 **Notes**:
- Common event handlers:
  - `on_click(e)` - Button clicks
  - `on_change(e)` - Value changes (TextField, Dropdown, etc.)
  - `on_submit(e)` - Form submission (TextField with enter key)
  - `on_hover(e)` - Mouse hover
  - `on_long_press(e)` - Long press gestures

---

### Error 4.3: Async Event Handler Issues

❌ **WRONG**:
```python
def async_handler(e):  # Not marked as async
    await asyncio.sleep(1)  # Can't await in non-async function
    e.control.text = "Done"
    page.update()
```

✅ **CORRECT**:
```python
async def async_handler(e):  # Properly marked as async
    await asyncio.sleep(1)  # Can now await
    e.control.text = "Done"
    page.update()

button = ft.ElevatedButton("Async Click", on_click=async_handler)
```

📝 **Notes**:
- Flet supports both sync and async event handlers
- If you need to `await`, mark function as `async`
- NEVER use `time.sleep()` in async handlers - use `asyncio.sleep()`

---

## 5. State Management and Update Errors

### Error 5.1: Forgetting to Call Update

❌ **WRONG**:
```python
def button_clicked(e):
    text.value = "Updated!"
    # Missing page.update() or text.update()
```

✅ **CORRECT**:
```python
def button_clicked(e):
    text.value = "Updated!"
    text.update()  # Update specific control

# OR

def button_clicked(e):
    text.value = "Updated!"
    container.visible = False
    page.update()  # Update entire page (when multiple controls change)
```

📝 **Notes**:
- **ALWAYS** call `update()` after changing control properties
- `control.update()` - Updates only that control (more efficient)
- `page.update()` - Updates entire page (use when multiple controls change)
- Forgetting `update()` is the #1 cause of "nothing happens" bugs

---

### Error 5.2: Using time.sleep() in Flet

❌ **WRONG**:
```python
import time

def show_loading(e):
    loading_text.visible = True
    page.update()
    time.sleep(2)  # BLOCKS THE ENTIRE APP!
    loading_text.visible = False
    page.update()
```

✅ **CORRECT**:
```python
import asyncio

async def show_loading(e):
    loading_text.visible = True
    page.update()
    await asyncio.sleep(2)  # Non-blocking sleep
    loading_text.visible = False
    page.update()
```

📝 **Notes**:
- **NEVER** use `time.sleep()` in Flet - it freezes the UI
- Use `asyncio.sleep()` with async functions
- For server calls, use `run_in_executor`:
  ```python
  loop = asyncio.get_running_loop()
  result = await loop.run_in_executor(None, blocking_function)
  ```

---

### Error 5.3: Modifying Control List While Iterating

❌ **WRONG**:
```python
def remove_all_buttons(e):
    for control in page.controls:
        if isinstance(control, ft.Button):
            page.controls.remove(control)  # Modifying while iterating!
    page.update()
```

✅ **CORRECT**:
```python
def remove_all_buttons(e):
    # Create a list of controls to remove
    to_remove = [c for c in page.controls if isinstance(c, ft.Button)]

    # Remove them
    for control in to_remove:
        page.controls.remove(control)

    page.update()

# OR use list comprehension to rebuild
def remove_all_buttons(e):
    page.controls = [c for c in page.controls if not isinstance(c, ft.Button)]
    page.update()
```

📝 **Notes**:
- Never modify a list while iterating over it
- Create separate list of items to remove or use list comprehension

---

## 6. Navigation and Routing Errors

### Error 6.1: Forgetting page.update() After Route Change

❌ **WRONG**:
```python
def go_to_store(e):
    page.route = "/store"
    # Missing page.update()
```

✅ **CORRECT**:
```python
def go_to_store(e):
    page.route = "/store"
    page.update()  # Required to trigger route change

# OR better: use page.go()
def go_to_store(e):
    page.go("/store")  # Automatically updates
```

📝 **Notes**:
- Always call `page.update()` after setting `page.route`
- Better: use `page.go(route)` which updates automatically
- Forgetting update is a common cause of "navigation doesn't work"

---

### Error 6.2: Incorrect Route Parameter Access

❌ **WRONG**:
```python
def route_change(e):
    # Trying to access route parameters incorrectly
    if page.route.startswith("/product/"):
        product_id = page.route.split("/")[2]  # Fragile parsing
```

✅ **CORRECT**:
```python
def route_change(e):
    troute = ft.TemplateRoute(page.route)

    if troute.match("/product/:id"):
        product_id = troute.id  # Access parameter by name
        print(f"Product ID: {product_id}")

    elif troute.match("/user/:user_id/orders/:order_id"):
        user_id = troute.user_id
        order_id = troute.order_id
        print(f"User: {user_id}, Order: {order_id}")

    page.update()
```

📝 **Notes**:
- Use `ft.TemplateRoute` for route parameter parsing
- Parameters defined with `:parameter_name` syntax
- Access via `troute.parameter_name`

---

### Error 6.3: Not Implementing on_view_pop Handler

❌ **WRONG**:
```python
def route_change(e):
    page.views.clear()
    page.views.append(ft.View("/", [ft.Text("Home")]))

    if page.route == "/store":
        page.views.append(ft.View("/store", [ft.Text("Store")]))

    page.update()

# Back button doesn't work!
```

✅ **CORRECT**:
```python
def route_change(e):
    page.views.clear()
    page.views.append(ft.View("/", [ft.Text("Home")]))

    if page.route == "/store":
        page.views.append(ft.View("/store", [ft.Text("Store")]))

    page.update()

def view_pop(view):
    page.views.pop()
    top_view = page.views[-1]
    page.go(top_view.route)

page.on_route_change = route_change
page.on_view_pop = view_pop  # Required for back button!
page.go(page.route)
```

📝 **Notes**:
- `on_view_pop` handles back button navigation
- Pop the view, get the top view, navigate to it
- Without this, back button won't work properly

---

## 7. Async/Await Integration Errors

### Error 7.1: Awaiting Synchronous Functions

❌ **WRONG**:
```python
async def load_data(e):
    # Assuming this function is synchronous but awaiting it
    result = await get_database_info()  # If get_database_info() is sync, this FREEZES!
```

✅ **CORRECT**:
```python
import asyncio

async def load_data(e):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, get_database_info)
    # Now works with synchronous get_database_info()
    page.update()
```

📝 **Notes**:
- **CRITICAL**: Don't await synchronous functions - causes permanent freeze
- Use `run_in_executor` to run sync code in async context
- Applies to all database/server calls in this project (ServerBridge methods are sync)

---

### Error 7.2: Using asyncio.run() Inside Flet

❌ **WRONG**:
```python
def button_clicked(e):
    result = asyncio.run(async_operation())  # Event loop already running!
```

✅ **CORRECT**:
```python
async def button_clicked(e):
    result = await async_operation()  # Use existing event loop
    page.update()
```

📝 **Notes**:
- Flet already has an event loop running
- NEVER call `asyncio.run()` inside Flet
- Make your handler async and use `await`

---

### Error 7.3: Not Handling Executor Exceptions

❌ **WRONG**:
```python
async def load_data(e):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, risky_database_call)
    # No error handling - if risky_database_call fails, app crashes
```

✅ **CORRECT**:
```python
async def load_data(e):
    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(None, risky_database_call)
        text.value = f"Success: {result}"
    except Exception as ex:
        text.value = f"Error: {str(ex)}"
        print(f"Database error: {ex}")
    finally:
        page.update()
```

📝 **Notes**:
- Always wrap `run_in_executor` in try-except
- Exceptions in executor threads propagate to async code
- Provide user-friendly error messages

---

## 8. DataTable and Complex Controls Errors

### Error 8.1: Incorrect DataTable Structure

❌ **WRONG**:
```python
table = ft.DataTable(
    columns=["Name", "Age", "City"],  # Wrong: strings not allowed
    rows=[
        ["Alice", "30", "NYC"],  # Wrong: raw lists not allowed
    ]
)
```

✅ **CORRECT**:
```python
table = ft.DataTable(
    columns=[
        ft.DataColumn(ft.Text("Name")),
        ft.DataColumn(ft.Text("Age")),
        ft.DataColumn(ft.Text("City")),
    ],
    rows=[
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text("Alice")),
                ft.DataCell(ft.Text("30")),
                ft.DataCell(ft.Text("NYC")),
            ]
        ),
    ]
)
```

📝 **Notes**:
- Columns must be `ft.DataColumn` objects containing controls
- Rows must be `ft.DataRow` objects
- Cells must be `ft.DataCell` objects containing controls
- All must wrap actual Flet controls (usually `ft.Text`)

---

### Error 8.2: DataTable Column Sorting Setup

❌ **WRONG**:
```python
table = ft.DataTable(
    columns=[
        ft.DataColumn(ft.Text("Name"), sortable=True),  # Wrong property name
    ],
    on_sort=handle_sort,  # Wrong event name
)
```

✅ **CORRECT**:
```python
def handle_column_sort(e):
    # e.column_index - index of clicked column
    # e.ascending - True if sorting ascending
    print(f"Sort column {e.column_index}, ascending: {e.ascending}")

table = ft.DataTable(
    columns=[
        ft.DataColumn(ft.Text("Name"), on_sort=handle_column_sort),
    ],
    sort_column_index=0,  # Currently sorted column
    sort_ascending=True,   # Sort direction
)
```

📝 **Notes**:
- Each `DataColumn` has its own `on_sort` handler
- Track sort state with `sort_column_index` and `sort_ascending`
- Sorting logic must be implemented manually

---

### Error 8.3: DataTable Row Selection

❌ **WRONG**:
```python
row = ft.DataRow(
    cells=[...],
    selected=True,  # Wrong - can't set directly
)
```

✅ **CORRECT**:
```python
def handle_row_select(e):
    # e.control is the DataRow
    e.control.selected = not e.control.selected
    page.update()

row = ft.DataRow(
    cells=[
        ft.DataCell(ft.Text("Data")),
    ],
    on_select_changed=handle_row_select,  # Correct event handler
)
```

📝 **Notes**:
- Use `on_select_changed` event handler
- Toggle `e.control.selected` in handler
- Must call `page.update()` or `table.update()` after changing

---

## 9. TextField and Form Control Errors

### Error 9.1: Password Field Reveal Button

❌ **WRONG**:
```python
password_field = ft.TextField(
    label="Password",
    password=True,
    show_password_toggle=True,  # Wrong property name
)
```

✅ **CORRECT**:
```python
password_field = ft.TextField(
    label="Password",
    password=True,
    can_reveal_password=True,  # Correct property
)
```

📝 **Notes**:
- Property is `can_reveal_password`, not `show_password_toggle`
- Adds eye icon to toggle password visibility
- Only works when `password=True`

---

### Error 9.2: TextField Validation and Error Text

❌ **WRONG**:
```python
def validate(e):
    if len(e.control.value) < 3:
        e.control.error = "Too short"  # Wrong property name
    page.update()

textfield = ft.TextField(on_change=validate)
```

✅ **CORRECT**:
```python
def validate(e):
    if len(e.control.value) < 3:
        e.control.error_text = "Too short"  # Correct property
    else:
        e.control.error_text = None  # Clear error
    page.update()

textfield = ft.TextField(
    label="Username",
    on_change=validate,
    helper_text="At least 3 characters"
)
```

📝 **Notes**:
- Property is `error_text`, not `error` or `error_message`
- Set to `None` to clear error
- `helper_text` shows persistent help message below field

---

### Error 9.3: Dropdown Options Structure

❌ **WRONG**:
```python
dropdown = ft.Dropdown(
    options=["Option 1", "Option 2", "Option 3"],  # Wrong: strings not allowed
)
```

✅ **CORRECT**:
```python
dropdown = ft.Dropdown(
    label="Choose option",
    options=[
        ft.dropdown.Option("opt1", "Option 1"),  # (key, text)
        ft.dropdown.Option("opt2", "Option 2"),
        ft.dropdown.Option("opt3", "Option 3"),
    ],
    on_change=lambda e: print(f"Selected: {e.control.value}")
)

# OR with just text (text becomes key)
dropdown = ft.Dropdown(
    options=[
        ft.dropdown.Option("Option 1"),
        ft.dropdown.Option("Option 2"),
    ]
)
```

📝 **Notes**:
- Must use `ft.dropdown.Option` objects
- Option takes `(key, text)` or just `(text)`
- Access selected value via `dropdown.value` (returns key)

---

### Error 9.4: Keyboard Type for TextField

❌ **WRONG**:
```python
textfield = ft.TextField(
    keyboard_type="email",  # String not supported
)
```

✅ **CORRECT**:
```python
textfield = ft.TextField(
    label="Email",
    keyboard_type=ft.KeyboardType.EMAIL,
)

# Available keyboard types:
# ft.KeyboardType.TEXT - Default text keyboard
# ft.KeyboardType.MULTILINE - Multiline text
# ft.KeyboardType.NUMBER - Numeric keyboard
# ft.KeyboardType.PHONE - Phone number keyboard
# ft.KeyboardType.DATETIME - Date/time keyboard
# ft.KeyboardType.EMAIL - Email keyboard with @ symbol
# ft.KeyboardType.URL - URL keyboard with / and .com
# ft.KeyboardType.VISIBLE_PASSWORD - Password keyboard showing text
```

📝 **Notes**:
- Use `ft.KeyboardType` enum
- Affects mobile keyboard layout
- Doesn't restrict input - use `input_filter` for validation

---

## 10. Import and Module Errors

### Error 10.1: Incorrect Module Imports

❌ **WRONG**:
```python
# Old imports from pre-0.28.3
from flet import *
import flet.controls as fc
```

✅ **CORRECT**:
```python
# Recommended import style for 0.28.3
import flet as ft

# Everything accessed via ft.
button = ft.Button("Click")
text = ft.Text("Hello")
page_obj = ft.Page()
```

📝 **Notes**:
- Import as `ft` is the recommended pattern
- All controls, enums, and functions under `ft` namespace
- Clearer code and avoids namespace pollution

---

### Error 10.2: Incorrect Enum Imports

❌ **WRONG**:
```python
from flet.alignment import MainAxisAlignment  # Wrong path
from flet.enums import MainAxisAlignment      # Wrong path
```

✅ **CORRECT**:
```python
import flet as ft

# Access enums through ft
alignment = ft.MainAxisAlignment.CENTER
color = ft.colors.BLUE_500
scroll_mode = ft.ScrollMode.AUTO
```

📝 **Notes**:
- All enums accessible via `ft` namespace
- Common enums: `MainAxisAlignment`, `CrossAxisAlignment`, `FontWeight`, `ScrollMode`, `KeyboardType`

---

### Error 10.3: Dialog/AlertDialog Import Confusion

❌ **WRONG**:
```python
dialog = ft.Dialog(  # Wrong - generic Dialog doesn't exist
    title="Confirm",
    content=ft.Text("Are you sure?"),
)
```

✅ **CORRECT**:
```python
dialog = ft.AlertDialog(  # Correct - use AlertDialog
    modal=True,
    title=ft.Text("Confirm"),
    content=ft.Text("Are you sure?"),
    actions=[
        ft.TextButton("Cancel"),
        ft.TextButton("OK"),
    ],
)

page.dialog = dialog
dialog.open = True
page.update()
```

📝 **Notes**:
- Use `ft.AlertDialog`, not `ft.Dialog`
- Set `page.dialog` property
- Set `dialog.open = True` to show
- Must call `page.update()` to display

---

## Quick Reference: Common Property Names

| Control | WRONG ❌ | CORRECT ✅ |
|---------|----------|------------|
| Container | `background_color` | `bgcolor` |
| Container | `border="1px solid"` | `border=ft.border.all(1, color)` |
| Container | `padding="10px"` | `padding=10` or `padding=ft.padding.all(10)` |
| Column/Row | `alignment="center"` | `alignment=ft.MainAxisAlignment.CENTER` |
| Column | `scroll="auto"` | `scroll=ft.ScrollMode.AUTO` |
| Text | `weight="bold"` | `weight=ft.FontWeight.BOLD` |
| TextField | `error` | `error_text` |
| TextField | `show_password_toggle` | `can_reveal_password` |
| DataTable | columns as strings | `ft.DataColumn(ft.Text("Name"))` |
| Dropdown | options as strings | `ft.dropdown.Option("text")` |
| Theme | `primary_color` | `color_scheme_seed` or `color_scheme` |
| Theme | `seed_color` | `color_scheme_seed` |

---

## Quick Reference: Common Method Names

| Operation | WRONG ❌ | CORRECT ✅ |
|-----------|----------|------------|
| Navigate | `page.route = "/new"; # only` | `page.go("/new")` or `page.route = "/new"; page.update()` |
| Show dialog | `dialog.show()` | `page.dialog = dialog; dialog.open = True; page.update()` |
| Update UI | Change property only | Change property + call `control.update()` or `page.update()` |
| Sleep | `time.sleep(1)` | `await asyncio.sleep(1)` |
| Run sync code | `await sync_function()` | `await loop.run_in_executor(None, sync_function)` |

---

## Debugging Checklist

When your Flet code doesn't work, check:

1. ✅ Did you call `page.update()` or `control.update()` after changing properties?
2. ✅ Are you using correct property names (`bgcolor` not `background_color`)?
3. ✅ Are you using enums instead of strings (`ft.MainAxisAlignment.CENTER` not `"center"`)?
4. ✅ Did you provide event parameter to handlers (`def handler(e):` not `def handler():`)?
5. ✅ Are you using `asyncio.sleep()` instead of `time.sleep()`?
6. ✅ Are you using `run_in_executor` for synchronous server/database calls?
7. ✅ For DataTable: Are you using `DataColumn`, `DataRow`, `DataCell` objects?
8. ✅ For Dropdown: Are you using `ft.dropdown.Option` objects?
9. ✅ For routing: Did you implement both `on_route_change` and `on_view_pop`?
10. ✅ For themes: Are you using `color_scheme_seed` or `color_scheme` (not `primary_color`)?

---

## Version-Specific Notes for Flet 0.28.3

### Material 3 is Default
- Set `use_material3=True` in Theme for full Material 3 experience
- Use `color_scheme_seed` for automatic color palette generation
- Text theme uses Material 3 naming (`headline_large` vs old `heading1`)

### Async Support Enhanced
- Event handlers can be async functions
- Use `await asyncio.sleep()` for delays
- Use `run_in_executor` for blocking operations

### Improved Responsive Layout
- `ResponsiveRow` with breakpoint-based `col` property
- Better expand behavior with numeric values

### Performance Improvements
- `control.update()` is more efficient than `page.update()`
- Use targeted updates when possible

---

## Additional Resources

- **Official Flet Documentation**: https://flet.dev/docs/
- **Flet Controls Reference**: https://flet.dev/docs/controls/
- **Flet GitHub**: https://github.com/flet-dev/flet
- **Project-Specific Guides**:
  - [FLET_INTEGRATION_GUIDE.md](FLET_INTEGRATION_GUIDE.md) - Async/sync patterns
  - [FLET_QUICK_FIX_GUIDE.md](FLET_QUICK_FIX_GUIDE.md) - Quick fixes for freezes
  - [architecture_guide.md](FletV2/architecture_guide.md) - 5-Section Pattern

---

---

## 11. PROJECT-SPECIFIC ERRORS

### ⚠️ CRITICAL: This Section is Specific to This Project

The following errors are unique to the Client-Server Encrypted Backup Framework (FletV2 GUI) and its architecture patterns.

---

## 11.1: ServerBridge Async Integration Errors

### Error 11.1.1: Awaiting ServerBridge Synchronous Methods

❌ **WRONG**:
```python
# ServerBridge methods are synchronous, NOT async!
async def load_clients():
    result = await bridge.get_clients()  # PERMANENT FREEZE!
```

✅ **CORRECT**:
```python
# ALWAYS use run_in_executor for ALL ServerBridge calls
async def load_clients():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, bridge.get_clients)

# OR use the project's async helper
from FletV2.utils.async_helpers import run_sync_in_executor, safe_server_call

async def load_clients():
    result = await run_sync_in_executor(safe_server_call, bridge, "get_clients")
```

📝 **Notes**:
- **ALL ServerBridge methods are synchronous** - they delegate to `BackupServer` methods
- The ServerBridge does NOT have async methods (no `_async` suffix methods work)
- **Pattern for EVERY server call**: `await run_in_executor(None, bridge.method_name, arg1, arg2)`
- Common methods: `get_clients()`, `get_database_info()`, `get_table_data()`, `get_logs()`, `get_analytics_data()`

---

### Error 11.1.2: Forgetting run_in_executor for Server Operations

❌ **WRONG**:
```python
async def fetch_dashboard_data():
    # Direct call blocks event loop
    summary = bridge.get_dashboard_summary()
    status = bridge.get_system_status()
    # UI freezes during these calls
```

✅ **CORRECT**:
```python
async def fetch_dashboard_data():
    loop = asyncio.get_running_loop()

    # Run all server calls in executor
    summary = await loop.run_in_executor(None, bridge.get_dashboard_summary)
    status = await loop.run_in_executor(None, bridge.get_system_status)

    # OR use project helper for cleaner code
    summary = await run_sync_in_executor(safe_server_call, bridge, "get_dashboard_summary")
    status = await run_sync_in_executor(safe_server_call, bridge, "get_system_status")
```

📝 **Notes**:
- **EVERY server/database call must use `run_in_executor`**
- Project provides helpers: `run_sync_in_executor()` and `safe_server_call()`
- See `FletV2/utils/async_helpers.py` for helper implementations
- See `FLET_INTEGRATION_GUIDE.md` for comprehensive async patterns

---

## 11.2: Import Path Resolution Errors

### Error 11.2.1: Mixed Relative/Absolute Imports

❌ **WRONG**:
```python
# Relative imports fail when server modifies sys.path
from utils.debug_setup import get_logger  # ModuleNotFoundError
from ..utils.server_bridge import ServerBridge  # Breaks in some contexts
```

✅ **CORRECT**:
```python
# Use try/except pattern for robust imports
try:
    from ..utils.debug_setup import get_logger  # Relative import (preferred)
    from ..utils.server_bridge import ServerBridge
except ImportError:
    # Fallback to absolute FletV2-prefixed imports
    from FletV2.utils.debug_setup import get_logger
    from FletV2.utils.server_bridge import ServerBridge
```

📝 **Notes**:
- BackupServer initialization modifies `sys.path`, breaking relative imports
- Always use try/except pattern with both relative and absolute imports
- Absolute imports must use `FletV2.` prefix (not just `utils.`)
- This pattern is in all view files - see `views/dashboard.py:26-36` for reference

---

### Error 11.2.2: Incorrect UTF-8 Subprocess Import

❌ **WRONG**:
```python
# Missing UTF-8 solution import
import subprocess
result = subprocess.run(["cmd", "/c", "dir"])  # Encoding errors on Windows
```

✅ **CORRECT**:
```python
# ALWAYS import UTF-8 solution for subprocess operations
import Shared.utils.utf8_solution as _  # noqa: F401
import subprocess
result = subprocess.run(["cmd", "/c", "dir"])  # Now handles UTF-8 correctly
```

📝 **Notes**:
- **Required import** at top of files using subprocess/console I/O
- Patches subprocess for correct UTF-8 handling on Windows
- The `as _` and `# noqa: F401` are intentional (side-effect import)
- See `Shared/utils/utf8_solution.py` for implementation

---

## 11.3: Tri-Style Theme System Errors

### Error 11.3.1: Incorrect Theme Constants Usage

❌ **WRONG**:
```python
# Using non-existent theme constants
container = ft.Container(
    shadow="neomorphic",  # String not supported
    blur=15,  # Wrong property for glassmorphism
)
```

✅ **CORRECT**:
```python
# Import pre-computed theme constants
from FletV2.theme import (
    PRONOUNCED_NEUMORPHIC_SHADOWS,
    MODERATE_NEUMORPHIC_SHADOWS,
    GLASS_SUBTLE,
)

# Use neumorphic shadows
container = ft.Container(
    content=ft.Text("Neumorphic Card"),
    shadow=PRONOUNCED_NEUMORPHIC_SHADOWS,  # Pre-computed list[ft.BoxShadow]
    border_radius=16,
    padding=20,
)

# Use glassmorphic effect
glass_container = ft.Container(
    content=ft.Text("Glass Card"),
    border_radius=16,
    padding=20,
    bgcolor=ft.Colors.with_opacity(GLASS_SUBTLE["bg_opacity"], ft.Colors.SURFACE),
    border=ft.border.all(1, ft.Colors.with_opacity(GLASS_SUBTLE["border_opacity"], ft.Colors.OUTLINE)),
    blur=ft.Blur(sigma_x=GLASS_SUBTLE["blur"], sigma_y=GLASS_SUBTLE["blur"])
)
```

📝 **Notes**:
- Tri-style system: **Material 3** + **Neumorphism** + **Glassmorphism**
- Neumorphic shadows: `PRONOUNCED_NEUMORPHIC_SHADOWS` (40-45%), `MODERATE_NEUMORPHIC_SHADOWS` (30%), `SUBTLE_NEUMORPHIC_SHADOWS` (20%)
- Glassmorphic configs: `GLASS_STRONG`, `GLASS_MODERATE`, `GLASS_SUBTLE` (dictionaries with blur, bg_opacity, border_opacity)
- See `FletV2/theme.py` for full API

---

### Error 11.3.2: Incorrect Theme Helper Usage

❌ **WRONG**:
```python
# Using non-existent theme helpers
card = create_card(content, style="neomorphic")  # Wrong function
```

✅ **CORRECT**:
```python
# Use correct theme helper functions
from FletV2.theme import (
    create_neumorphic_container,
    create_glassmorphic_container,
    create_hybrid_gauge_container,
)

# Neumorphic container
neumorphic_card = create_neumorphic_container(
    content=ft.Text("Metric Value"),
    intensity="pronounced",  # "pronounced", "moderate", or "subtle"
    hover_effect=True
)

# Glassmorphic container
glass_card = create_glassmorphic_container(
    content=ft.Column([...]),
    intensity="moderate"  # "subtle", "moderate", or "strong"
)

# Hybrid (neomorphic base + glass overlay)
hybrid_gauge = create_hybrid_gauge_container(
    content=gauge_chart
)
```

📝 **Notes**:
- Neumorphic helper: `create_neumorphic_container(content, effect_type, hover_effect, intensity)`
- Glassmorphic helper: `create_glassmorphic_container(content, intensity)`
- Hybrid helper: `create_hybrid_gauge_container(content)` - for dashboards
- All helpers return `ft.Container` with pre-configured styling

---

## 11.4: View Pattern Errors

### Error 11.4.1: Incorrect View Function Signature

❌ **WRONG**:
```python
# Wrong return type - must return 3-tuple
def create_my_view(bridge, page):
    return ft.Container(...)  # Missing dispose and setup!
```

✅ **CORRECT**:
```python
# Correct 3-tuple return: (control, dispose, setup)
def create_my_view(
    server_bridge: ServerBridge | None,
    page: ft.Page,
    state_manager: StateManager | None = None
) -> tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]]:

    # Build UI
    content = ft.Container(...)

    # Cleanup function
    def dispose() -> None:
        # Clean up resources, subscriptions, etc.
        pass

    # Async setup function
    async def setup() -> None:
        # Load initial data
        await load_data()

    return content, dispose, setup
```

📝 **Notes**:
- **REQUIRED**: All views must return `(control, dispose, setup)` tuple
- `control`: ft.Control - the view's root UI element
- `dispose`: sync function - cleanup (subscriptions, timers, etc.)
- `setup`: async function - initial data loading
- See `FletV2/architecture_guide.md` for 5-Section Pattern details

---

### Error 11.4.2: Not Following 5-Section Pattern

❌ **WRONG**:
```python
# Mixing concerns - business logic, UI, and data fetching all mixed
def create_view(bridge, page):
    clients = bridge.get_clients()  # Section 1: Data fetching in wrong place
    filtered = [c for c in clients if c["status"] == "active"]  # Section 2: Business logic
    table = ft.DataTable(...)  # Section 3: UI - all in wrong order
```

✅ **CORRECT**:
```python
# Section 1: Data Fetching (async wrappers for ServerBridge)
async def fetch_clients(bridge):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, bridge.get_clients)
    return result.get("data", [])

# Section 2: Business Logic (pure functions - testable)
def filter_active_clients(clients):
    return [c for c in clients if c.get("status") == "active"]

# Section 3: UI Components (Flet control builders)
def create_clients_table(clients):
    return ft.DataTable(
        columns=[...],
        rows=[create_row(c) for c in clients]
    )

# Section 4: Event Handlers (user interactions)
async def on_refresh(e):
    clients = await fetch_clients(bridge)
    filtered = filter_active_clients(clients)
    update_ui(filtered)

# Section 5: Main View (composition and lifecycle)
def create_view(bridge, page, state_manager):
    # Compose UI, wire handlers, return (control, dispose, setup)
    ...
```

📝 **Notes**:
- **5-Section Pattern** is MANDATORY for all views
- Section 1: Data Fetching - async wrappers
- Section 2: Business Logic - pure functions (most testable)
- Section 3: UI Components - Flet control builders
- Section 4: Event Handlers - wire user actions
- Section 5: Main View - compose and return tuple
- See `FletV2/architecture_guide.md` for full pattern documentation

---

## 11.5: Data Format Conversion Errors

### Error 11.5.1: Not Converting BLOB UUIDs

❌ **WRONG**:
```python
# Using raw BLOB UUIDs from BackupServer
client_data = bridge.get_clients()
for client in client_data:
    client_id = client["id"]  # This is BYTES! Not string!
    print(f"Client: {client_id}")  # Displays as b'\x12\x34...'
```

✅ **CORRECT**:
```python
# ServerBridge automatically converts BLOB → string
client_data = bridge.get_clients()
if client_data.get("success"):
    for client in client_data["data"]:
        client_id = client["id"]  # Already converted to hex string
        print(f"Client: {client_id}")  # Displays as '12345678abcd...'

# Manual conversion if needed (advanced)
from FletV2.utils.server_bridge import blob_to_uuid_string, uuid_string_to_blob

hex_id = blob_to_uuid_string(blob_bytes)  # bytes → string
blob_bytes = uuid_string_to_blob(hex_string)  # string → bytes
```

📝 **Notes**:
- BackupServer stores UUIDs as BLOB (16 bytes)
- FletV2 GUI needs string IDs (hex representation)
- **ServerBridge auto-converts** in both directions
- Conversion happens in `convert_backupserver_client_to_fletv2()` and similar functions
- Only use manual conversion for custom data handling

---

### Error 11.5.2: Not Using Structured Response Format

❌ **WRONG**:
```python
# Expecting direct data return
async def load_data():
    clients = await run_sync_in_executor(None, bridge.get_clients)
    for client in clients:  # WRONG! clients is a dict, not list
        print(client)
```

✅ **CORRECT**:
```python
# ALL ServerBridge methods return: {'success': bool, 'data': Any, 'error': str}
async def load_data():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, bridge.get_clients)

    if result.get("success"):
        clients = result.get("data", [])  # Extract data from response
        for client in clients:
            print(client)
    else:
        error_msg = result.get("error", "Unknown error")
        show_error_message(page, f"Failed to load clients: {error_msg}")
```

📝 **Notes**:
- **EVERY** ServerBridge method returns structured format: `{'success': bool, 'data': Any, 'error': str}`
- Always check `result.get("success")` before accessing data
- Use `.get("data", default)` for safe access
- Error messages in `result.get("error", "Unknown error")`
- See `FletV2/utils/server_bridge.py` for implementation

---

## 11.6: UserControl Lifecycle Errors

### Error 11.6.1: Not Implementing build() Method

❌ **WRONG**:
```python
class MyCustomControl(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.content = ft.Text("Hello")  # Wrong - no build()
```

✅ **CORRECT**:
```python
class MyCustomControl(ft.UserControl):
    def __init__(self, initial_value):
        super().__init__()
        self.value = initial_value

    def build(self):  # REQUIRED method
        return ft.Container(
            content=ft.Text(self.value),
            padding=10,
            border_radius=8
        )
```

📝 **Notes**:
- **`build()` method is REQUIRED** for all `ft.UserControl` subclasses
- `build()` must return a single `ft.Control`
- Called automatically when control is added to page
- See `FletV2/components/data_table.py` for reference implementation

---

### Error 11.6.2: Incorrect Update Pattern in UserControl

❌ **WRONG**:
```python
class CounterControl(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.counter = 0

    def increment(self, e):
        self.counter += 1
        # No update call - changes not reflected!

    def build(self):
        return ft.ElevatedButton(f"Count: {self.counter}", on_click=self.increment)
```

✅ **CORRECT**:
```python
class CounterControl(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.button = None  # Store reference

    def increment(self, e):
        self.counter += 1
        if self.button:
            self.button.text = f"Count: {self.counter}"
        self.update()  # REQUIRED: Update this UserControl

    def build(self):
        self.button = ft.ElevatedButton(
            f"Count: {self.counter}",
            on_click=self.increment
        )
        return self.button
```

📝 **Notes**:
- Call `self.update()` (not `page.update()`) inside UserControl methods
- Store references to controls you need to modify
- `self.update()` updates only this UserControl (more efficient)
- Use `page.update()` only when changing controls outside the UserControl

---

## 11.7: Settings and State Management Errors

### Error 11.7.1: Incorrect Settings Dirty Tracking

❌ **WRONG**:
```python
# Not tracking which settings changed
def on_change(e):
    current_settings["server"]["port"] = e.control.value
    # No dirty tracking - autosave doesn't know what changed!
```

✅ **CORRECT**:
```python
# Track dirty state per setting
dirty_tracker: dict[str, set[str]] = {
    "server": set(),
    "gui": set(),
    # ... other categories
}

def on_change(e):
    category = "server"
    key = "port"
    current_settings[category][key] = e.control.value

    # Mark as dirty
    dirty_tracker[category].add(key)

    # Schedule autosave (debounced)
    schedule_autosave()
```

📝 **Notes**:
- Settings view uses **dirty tracking** for autosave
- `dirty_tracker` is dict of sets: `{category: {key1, key2, ...}}`
- Mark settings dirty when changed, clear when saved
- Autosave uses `@debounce` decorator (2-second delay)
- See `FletV2/views/settings.py:199-203` for implementation

---

### Error 11.7.2: Not Using StateManager for Cross-View Updates

❌ **WRONG**:
```python
# Direct update without StateManager - other views don't know!
def update_theme(e):
    page.theme_mode = ft.ThemeMode.DARK
    page.update()
    # Settings changed but other views not notified!
```

✅ **CORRECT**:
```python
# Use StateManager to broadcast changes
def update_theme(e):
    page.theme_mode = ft.ThemeMode.DARK
    page.update()

    if state_manager:
        # Update state (other views can subscribe)
        state_manager.update(
            "theme_mode",
            "dark",
            source="settings_view"
        )
        # Broadcast event (other views can listen)
        state_manager.broadcast_settings_event(
            "theme_change",
            {"theme_mode": "dark"}
        )
```

📝 **Notes**:
- **StateManager** coordinates state across views
- Use `state_manager.update(key, value, source)` for state changes
- Use `state_manager.broadcast_settings_event(event_name, data)` for events
- Views subscribe with `state_manager.subscribe_to_settings_async(callback)`
- See `FletV2/utils/state_manager.py` for full API

---

## 11.8: Environment Variable Configuration Errors

### Error 11.8.1: Not Setting Integration Environment Variables

❌ **WRONG**:
```python
# Launching with BackupServer without disabling embedded GUI
from python_server.server.server import BackupServer

server = BackupServer()  # Dual GUI conflict! App hangs!
```

✅ **CORRECT**:
```python
# ALWAYS set environment variables BEFORE importing BackupServer
import os

# Disable BackupServer's embedded GUI
os.environ["CYBERBACKUP_DISABLE_INTEGRATED_GUI"] = "1"
os.environ["CYBERBACKUP_DISABLE_GUI"] = "1"

# Set database path (optional)
os.environ["BACKUP_DATABASE_PATH"] = "/path/to/defensive.db"

# NOW safe to import and instantiate
from python_server.server.server import BackupServer

server = BackupServer()  # No GUI conflict
```

📝 **Notes**:
- **CRITICAL**: Set env vars BEFORE importing `BackupServer`
- `CYBERBACKUP_DISABLE_INTEGRATED_GUI="1"` - Disables embedded GUI
- `CYBERBACKUP_DISABLE_GUI="1"` - Double-ensures GUI disabled
- `BACKUP_DATABASE_PATH` - Custom database location (optional)
- See `FletV2/start_with_server.py` for reference implementation
- See project CLAUDE.md for full integration details

---

### Error 11.8.2: Incorrect Database Path Resolution

❌ **WRONG**:
```python
# Using os.getcwd() - unreliable across execution contexts
import os
db_path = os.path.join(os.getcwd(), "defensive.db")  # Breaks!
```

✅ **CORRECT**:
```python
# Use __file__ for reliable path resolution
import os

fletv2_root = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(fletv2_root)
db_path = os.path.join(project_root, "defensive.db")

# Set environment variable before BackupServer import
os.environ["BACKUP_DATABASE_PATH"] = db_path
```

📝 **Notes**:
- **NEVER** use `os.getcwd()` for database path - context-dependent
- **ALWAYS** use `__file__` for reliable path resolution
- Set `BACKUP_DATABASE_PATH` env var before importing BackupServer
- Project structure: `project_root/FletV2/*.py` and `project_root/defensive.db`
- See `FletV2/start_with_server.py:24-29` for reference

---

## 11.9: Loading States Pattern Errors

### Error 11.9.1: Not Using Project Loading State Helpers

❌ **WRONG**:
```python
# Custom loading implementation - inconsistent UX
loading = ft.ProgressRing()
error = ft.Text("", color="red")
empty = ft.Text("No data")
# Repeated in every view!
```

✅ **CORRECT**:
```python
# Use project loading state helpers
from FletV2.utils.loading_states import (
    create_loading_indicator,
    create_error_display,
    create_empty_state,
    show_error_snackbar,
    show_success_snackbar,
)

# Loading state
loading = create_loading_indicator("Fetching clients...")

# Error state
error = create_error_display("Failed to load data")

# Empty state
empty = create_empty_state("No clients found", "Add clients to get started")

# User feedback
show_success_snackbar(page, "Clients loaded successfully")
show_error_snackbar(page, "Failed to load clients")
```

📝 **Notes**:
- **ALWAYS use project helpers** for consistent UX
- `create_loading_indicator(message)` - Loading spinner + message
- `create_error_display(error_text)` - Error icon + message
- `create_empty_state(title, subtitle)` - Empty state illustration
- `show_success_snackbar(page, message)` - Success notification
- `show_error_snackbar(page, message)` - Error notification
- See `FletV2/utils/loading_states.py` for full API

---

### Error 11.9.2: Incorrect Loading Overlay Pattern

❌ **WRONG**:
```python
# Loading state blocks all interaction
async def load_data(e):
    page.add(ft.ProgressRing())  # Blocks entire UI!
    page.update()
    await fetch_data()
    page.controls.pop()  # Remove progress ring
    page.update()
```

✅ **CORRECT**:
```python
# Use Stack with overlay pattern
loading_overlay = create_loading_indicator("Loading...")

# UI structure
stack = ft.Stack([
    main_content,  # Main UI
    ft.Container(
        content=loading_overlay,
        alignment=ft.alignment.center,
        expand=True,
        visible=False,  # Hidden by default
    )
], expand=True)
overlay_container = stack.controls[1]

# Show/hide loading
async def load_data(e):
    overlay_container.visible = True
    overlay_container.update()

    try:
        data = await fetch_data()
        update_ui(data)
    finally:
        overlay_container.visible = False
        overlay_container.update()
```

📝 **Notes**:
- Use `ft.Stack` with overlay for non-blocking loading states
- Store reference to overlay container for show/hide
- Toggle `visible` property, not add/remove from page
- Always use try/finally to ensure overlay is hidden
- See `FletV2/views/dashboard.py:392-408` for reference

---

## 11.10: Component Reusability Errors

### Error 11.10.1: Not Using AppCard for Consistent Styling

❌ **WRONG**:
```python
# Custom card implementation - inconsistent styling
card = ft.Container(
    content=data_table,
    padding=16,
    border_radius=12,
    bgcolor=ft.Colors.SURFACE,
    shadow=ft.BoxShadow(...)  # Repeated everywhere!
)
```

✅ **CORRECT**:
```python
# Use AppCard for consistent styling
from FletV2.utils.ui_components import AppCard

card = AppCard(
    content=data_table,
    title="Clients",  # Optional title
    expand_content=True  # Optional: expand content to fill card
)
```

📝 **Notes**:
- **ALWAYS use `AppCard`** for card-style containers
- Provides consistent padding, radius, shadows, and styling
- Optional title with consistent typography
- `expand_content=True` for full-height content
- See `FletV2/utils/ui_components.py` for full API

---

### Error 11.10.2: Not Using UI Builder Helpers

❌ **WRONG**:
```python
# Manually building common UI patterns
button = ft.ElevatedButton(
    "Refresh",
    icon=ft.Icons.REFRESH,
    on_click=on_refresh,
    style=ft.ButtonStyle(...)  # Repeated everywhere!
)

header = ft.Row([
    ft.Icon(ft.Icons.DASHBOARD),
    ft.Column([
        ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Live system overview", size=14, color=ft.Colors.ON_SURFACE_VARIANT)
    ])
])  # Complex structure repeated!
```

✅ **CORRECT**:
```python
# Use UI builder helpers
from FletV2.utils.ui_builders import create_action_button, create_view_header

# Action button with consistent styling
button = create_action_button(
    "Refresh",
    on_refresh,
    icon=ft.Icons.REFRESH,
    primary=True  # or False for secondary button
)

# View header with icon, title, description, and actions
header = create_view_header(
    "Dashboard",
    icon=ft.Icons.DASHBOARD,
    description="Live system overview",
    actions=[refresh_button, export_button]  # Optional action buttons
)
```

📝 **Notes**:
- **Use `create_action_button()`** for all buttons (consistent styling)
- **Use `create_view_header()`** for all view headers (consistent layout)
- `create_action_button(text, on_click, icon, primary=True/False)`
- `create_view_header(title, icon, description, actions=[])`
- See `FletV2/utils/ui_builders.py` for full API

---

## PROJECT-SPECIFIC QUICK REFERENCE

### ServerBridge Pattern
```python
# CRITICAL: ALL ServerBridge calls use run_in_executor
async def call_server():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, bridge.method_name, arg1, arg2)
    # OR
    result = await run_sync_in_executor(safe_server_call, bridge, "method_name", arg1, arg2)
```

### View Pattern
```python
def create_my_view(
    server_bridge: ServerBridge | None,
    page: ft.Page,
    state_manager: StateManager | None = None
) -> tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]]:
    # Section 1: Data Fetching
    # Section 2: Business Logic
    # Section 3: UI Components
    # Section 4: Event Handlers
    # Section 5: Main View
    return control, dispose, setup
```

### Import Pattern
```python
try:
    from ..utils.server_bridge import ServerBridge
except ImportError:
    from FletV2.utils.server_bridge import ServerBridge
```

### Theme Pattern
```python
from FletV2.theme import (
    PRONOUNCED_NEUMORPHIC_SHADOWS,
    GLASS_SUBTLE,
    create_neumorphic_container,
)
```

### Loading States Pattern
```python
from FletV2.utils.loading_states import (
    create_loading_indicator,
    create_error_display,
    create_empty_state,
)
```

### Environment Variables (Integration)
```python
import os
os.environ["CYBERBACKUP_DISABLE_INTEGRATED_GUI"] = "1"
os.environ["CYBERBACKUP_DISABLE_GUI"] = "1"
os.environ["BACKUP_DATABASE_PATH"] = db_path
```

---

**End of Error Reference**

This document should be consulted BEFORE generating Flet code to avoid common mistakes. When errors occur, search this document for the specific control or pattern causing issues.

**For project-specific patterns, always check**:
- `FLET_INTEGRATION_GUIDE.md` - Async/sync integration patterns
- `FLET_QUICK_FIX_GUIDE.md` - Quick fixes for freezes
- `FletV2/architecture_guide.md` - 5-Section Pattern
- `FletV2/CLAUDE.md` - Project conventions and guidelines
