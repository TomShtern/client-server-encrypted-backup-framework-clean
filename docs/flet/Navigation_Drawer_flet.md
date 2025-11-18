Title: NavigationDrawer | Flet

URL Source: http://flet.dev/docs/controls/navigationdrawer

Markdown Content:
Material Design Navigation Drawer component.

Navigation Drawer is a panel that slides in horizontally from the left or right edge of a page to show primary destinations in an app. To add NavigationDrawer to the page, use [`page.drawer`](https://flet.dev/docs/controls/page#drawer) and [`page.end_drawer`](https://flet.dev/docs/controls/page#end_drawer) properties. Similarly, the NavigationDrawer can be added to a [`View`](https://flet.dev/docs/controls/view#drawer). To display the drawer, set its `open` property to `True`.

To open this control, simply call the [`page.open()`](https://flet.dev/docs/controls/page#opencontrol) helper-method.

[Live example](https://flet-controls-gallery.fly.dev/navigation/navigationdrawer)

### NavigationDrawer sliding from the left edge of a page[​](http://flet.dev/docs/controls/navigationdrawer#navigationdrawer-sliding-from-the-left-edge-of-a-page "Direct link to NavigationDrawer sliding from the left edge of a page")

![Image 1](https://flet.dev/img/docs/controls/navigationdrawer/navigation-drawer-start.gif)

python/controls/navigation/navigation-drawer/nav-drawer-example.py

`import flet as ftdef main(page: ft.Page):    def handle_dismissal(e):        print(f"Drawer dismissed!")    def handle_change(e):        print(f"Selected Index changed: {e.control.selected_index}")        page.close(drawer)    drawer = ft.NavigationDrawer(        on_dismiss=handle_dismissal,        on_change=handle_change,        controls=[            ft.Container(height=12),            ft.NavigationDrawerDestination(                label="Item 1",                icon=ft.Icons.DOOR_BACK_DOOR_OUTLINED,                selected_icon=ft.Icon(ft.Icons.DOOR_BACK_DOOR),            ),            ft.Divider(thickness=2),            ft.NavigationDrawerDestination(                icon=ft.Icon(ft.Icons.MAIL_OUTLINED),                label="Item 2",                selected_icon=ft.Icons.MAIL,            ),            ft.NavigationDrawerDestination(                icon=ft.Icon(ft.Icons.PHONE_OUTLINED),                label="Item 3",                selected_icon=ft.Icons.PHONE,            ),        ],    )    page.add(ft.ElevatedButton("Show drawer", on_click=lambda e: page.open(drawer)))ft.app(main)`

### NavigationDrawer sliding from the right edge of a page[​](http://flet.dev/docs/controls/navigationdrawer#navigationdrawer-sliding-from-the-right-edge-of-a-page "Direct link to NavigationDrawer sliding from the right edge of a page")

![Image 2](https://flet.dev/img/docs/controls/navigationdrawer/navigation-drawer-end.gif)

python/controls/navigation/navigation-drawer/nav-drawer-end.py

`import flet as ftdef main(page: ft.Page):    def handle_dismissal(e):        print("End drawer dismissed")    def handle_change(e):        print(f"Selected Index changed: {e.control.selected_index}")        page.close(end_drawer)    end_drawer = ft.NavigationDrawer(        position=ft.NavigationDrawerPosition.END,        on_dismiss=handle_dismissal,        on_change=handle_change,        controls=[            ft.NavigationDrawerDestination(                icon=ft.Icons.ADD_TO_HOME_SCREEN_SHARP, label="Item 1"            ),            ft.NavigationDrawerDestination(                icon=ft.Icon(ft.Icons.ADD_COMMENT), label="Item 2"            ),        ],    )    page.add(        ft.ElevatedButton("Show end drawer", on_click=lambda e: page.open(end_drawer))    )ft.app(main)`

### `bgcolor`[​](http://flet.dev/docs/controls/navigationdrawer#bgcolor "Direct link to bgcolor")

The [color](https://flet.dev/docs/reference/colors) of the navigation drawer itself.

### `controls`[​](http://flet.dev/docs/controls/navigationdrawer#controls "Direct link to controls")

Defines the appearance of the items within the navigation drawer.

The list contains `NavigationDrawerDestination` items and/or other controls such as headlines and dividers.

### `elevation`[​](http://flet.dev/docs/controls/navigationdrawer#elevation "Direct link to elevation")

The elevation of the navigation drawer itself.

### `indicator_color`[​](http://flet.dev/docs/controls/navigationdrawer#indicator_color "Direct link to indicator_color")

The [color](https://flet.dev/docs/reference/colors) of the selected destination indicator.

### `indicator_shape`[​](http://flet.dev/docs/controls/navigationdrawer#indicator_shape "Direct link to indicator_shape")

The shape of the selected destination indicator.

Value is of type [`OutlinedBorder`](https://flet.dev/docs/reference/types/outlinedborder).

### `position`[​](http://flet.dev/docs/controls/navigationdrawer#position "Direct link to position")

The position of this drawer.

Value is of type [`NavigationDrawerPosition`](https://flet.dev/docs/reference/types/navigationdrawerposition) and defaults to `NavigationDrawerPosition.START`.

### `selected_index`[​](http://flet.dev/docs/controls/navigationdrawer#selected_index "Direct link to selected_index")

The index for the current selected `NavigationDrawerDestination` or null if no destination is selected.

A valid selected_index is an integer between 0 and number of destinations - `1`. For an invalid `selected_index`, for example, `-1`, all destinations will appear unselected.

### `shadow_color`[​](http://flet.dev/docs/controls/navigationdrawer#shadow_color "Direct link to shadow_color")

The [color](https://flet.dev/docs/reference/colors) used for the drop shadow to indicate `elevation`.

### `surface_tint_color`[​](http://flet.dev/docs/controls/navigationdrawer#surface_tint_color "Direct link to surface_tint_color")

The surface tint of the Material that holds the NavigationDrawer's contents.

### `tile_padding`[​](http://flet.dev/docs/controls/navigationdrawer#tile_padding "Direct link to tile_padding")

Defines the padding for `NavigationDrawerDestination` controls.

### `on_change`[​](http://flet.dev/docs/controls/navigationdrawer#on_change "Direct link to on_change")

Fires when selected destination changed.

### `on_dismiss`[​](http://flet.dev/docs/controls/navigationdrawer#on_dismiss "Direct link to on_dismiss")

Fires when drawer is dismissed by clicking outside of the panel or [programmatically](https://flet.dev/docs/controls/page#closecontrol).

### `bgcolor`[​](http://flet.dev/docs/controls/navigationdrawer#bgcolor-1 "Direct link to bgcolor-1")

The [color](https://flet.dev/docs/reference/colors) of this destination.

### `icon`[​](http://flet.dev/docs/controls/navigationdrawer#icon "Direct link to icon")

The [name of the icon](https://flet.dev/docs/reference/icons) or `Control` of the destination.

Example with icon name:

`icon=ft.Icons.BOOKMARK`

Example with Control:

`icon=ft.Icon(ft.Icons.BOOKMARK)`

If `selected_icon` is provided, this will only be displayed when the destination is not selected.

### ~~`icon_content`~~[​](http://flet.dev/docs/controls/navigationdrawer#icon_content "Direct link to icon_content")

The icon `Control` of the destination. Typically the icon is an [`Icon`](https://flet.dev/docs/controls/icon) control. Used instead of `icon` property.

**Deprecated in v0.25.0 and will be removed in v0.28.0. Use [`icon`](http://flet.dev/docs/controls/navigationdrawer#icon) instead.**

### `label`[​](http://flet.dev/docs/controls/navigationdrawer#label "Direct link to label")

The text label that appears below the icon of this `NavigationDrawerDestination`.

### `selected_icon`[​](http://flet.dev/docs/controls/navigationdrawer#selected_icon "Direct link to selected_icon")

The [name](https://flet.dev/docs/reference/icons) of alternative icon or `Control` displayed when this destination is selected.

Example with icon name:

`selected_icon=ft.Icons.BOOKMARK`

Example with Control:

`selected_icon=ft.Icon(ft.Icons.BOOKMARK)`

If this icon is not provided, the NavigationDrawer will display `icon` in either state.

### ~~`selected_icon_content`~~[​](http://flet.dev/docs/controls/navigationdrawer#selected_icon_content "Direct link to selected_icon_content")

An alternative icon `Control` displayed when this destination is selected.

**Deprecated in v0.25.0 and will be removed in v0.28.0. Use [`selected_icon`](http://flet.dev/docs/controls/navigationdrawer#selected_icon) instead.**