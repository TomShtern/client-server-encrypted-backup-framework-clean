Title: AppBar | Flet

URL Source: http://flet.dev/docs/controls/appbar

Markdown Content:
A material design app bar.

[Live example](https://flet-controls-gallery.fly.dev/navigation/appbar)

### AppBar[​](http://flet.dev/docs/controls/appbar#appbar "Direct link to AppBar")

python/controls/navigation/app-bar/appbar-simple.py

`import flet as ftdef main(page: ft.Page):    page.title = "AppBar Example"    def check_item_clicked(e):        e.control.checked = not e.control.checked        page.update()    page.appbar = ft.AppBar(        leading=ft.Icon(ft.Icons.PALETTE),        leading_width=40,        title=ft.Text("AppBar Example"),        center_title=False,        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,        actions=[            ft.IconButton(ft.Icons.WB_SUNNY_OUTLINED),            ft.IconButton(ft.Icons.FILTER_3),            ft.PopupMenuButton(                items=[                    ft.PopupMenuItem(text="Item 1"),                    ft.PopupMenuItem(),  # divider                    ft.PopupMenuItem(                        text="Checked item", checked=False, on_click=check_item_clicked                    ),                ]            ),        ],    )    page.add(ft.Text("Body!"))ft.app(target=main)`

![Image 1](https://flet.dev/img/docs/controls/app-bar/app-bar.gif)

### `actions`[​](http://flet.dev/docs/controls/appbar#actions "Direct link to actions")

A list of `Control`s to display in a row after the title control.

Typically these controls are [`IconButtons`](https://flet.dev/docs/controls/iconbutton) representing common operations. For less common operations, consider using a [`PopupMenuButton`](https://flet.dev/docs/controls/popupmenubutton) as the last action.

**Note** that, if `AppBar.adaptive=True` and the app is opened on an iOS or macOS device, only the first element of this list will be used. This is because the `CupertinoAppBar`(which will be used on those two platforms) only accepts one - trailing - action control.

### `adaptive`[​](http://flet.dev/docs/controls/appbar#adaptive "Direct link to adaptive")

If the value is `True`, an adaptive AppBar is created based on whether the target platform is iOS/macOS.

On iOS and macOS, a [`CupertinoAppBar`](https://flet.dev/docs/controls/cupertinoappbar) is created, which has matching functionality and presentation as `AppBar`, and the graphics as expected on iOS. On other platforms, a Material AppBar is created.

Value is of type `bool` and defaults to `False`.

### `automatically_imply_leading`[​](http://flet.dev/docs/controls/appbar#automatically_imply_leading "Direct link to automatically_imply_leading")

Controls whether we should try to imply the leading widget if null.

If `True` and `leading` is null, automatically try to deduce what the leading widget should be. If `False` and `leading` is null, leading space is given to title. If leading widget is not null, this parameter has no effect.

Value is of type `bool`.

### `bgcolor`[​](http://flet.dev/docs/controls/appbar#bgcolor "Direct link to bgcolor")

The fill [color](https://flet.dev/docs/reference/colors) to use for an AppBar. Default color is defined by current theme.

### `center_title`[​](http://flet.dev/docs/controls/appbar#center_title "Direct link to center_title")

Whether the title should be centered.

Value is of type `bool` and defaults to `False`.

### `clip_behavior`[​](http://flet.dev/docs/controls/appbar#clip_behavior "Direct link to clip_behavior")

The content will be clipped (or not) according to this option.

Value is of type [`ClipBehavior`](https://flet.dev/docs/reference/types/clipbehavior).

### `color`[​](http://flet.dev/docs/controls/appbar#color "Direct link to color")

The default [color](https://flet.dev/docs/reference/colors) for `Text` and `Icon` controls within the app bar. Default color is defined by current theme.

### `elevation`[​](http://flet.dev/docs/controls/appbar#elevation "Direct link to elevation")

The app bar's elevation.

Note: This effect is only visible when using the Material 2 design (`Theme.use_material3=False`).

Value is of type [`OptionalNumber`](https://flet.dev/docs/reference/types/aliases#optionalnumber) and defaults to `4`.

### `elevation_on_scroll`[​](http://flet.dev/docs/controls/appbar#elevation_on_scroll "Direct link to elevation_on_scroll")

The elevation to be used if this app bar has something scrolled underneath it.

Value is of type [`OptionalNumber`](https://flet.dev/docs/reference/types/aliases#optionalnumber).

Whether the `title` should be wrapped with header [`Semantics`](https://flet.dev/docs/controls/semantics).

Value is of type `bool` and defaults to `False`.

### `force_material_transparency`[​](http://flet.dev/docs/controls/appbar#force_material_transparency "Direct link to force_material_transparency")

Forces the app bar to be transparent (instead of Material's default type).

This will also remove the visual display of `bgcolor` and `elevation`, and affect other characteristics of this app bar.

Value is of type `bool`.

### `is_secondary`[​](http://flet.dev/docs/controls/appbar#is_secondary "Direct link to is_secondary")

Whether this app bar is not being displayed at the top of the screen.

Value is of type `bool` and defaults to `False`.

### `leading`[​](http://flet.dev/docs/controls/appbar#leading "Direct link to leading")

A `Control` to display before the toolbar's title.

Typically the leading control is an [`Icon`](https://flet.dev/docs/controls/icon) or an [`IconButton`](https://flet.dev/docs/controls/iconbutton).

Value is of type `Control`.

### `leading_width`[​](http://flet.dev/docs/controls/appbar#leading_width "Direct link to leading_width")

Defines the width of leading control.

Value is of type [`OptionalNumber`](https://flet.dev/docs/reference/types/aliases#optionalnumber) and defaults to `56.0`.

### `shadow_color`[​](http://flet.dev/docs/controls/appbar#shadow_color "Direct link to shadow_color")

The [color](https://flet.dev/docs/reference/colors) of the shadow below the app bar.

A shadow is only visible and displayed if the `elevation` is greater than zero.

### `shape`[​](http://flet.dev/docs/controls/appbar#shape "Direct link to shape")

The shape of the app bar's Material as well as its shadow.

Value is of type [`OutlinedBorder`](https://flet.dev/docs/reference/types/outlinedborder).

### `surface_tint_color`[​](http://flet.dev/docs/controls/appbar#surface_tint_color "Direct link to surface_tint_color")

The color of the surface tint overlay applied to the app bar's `bgcolor` to indicate elevation.

By default, no overlay will be applied.

### `title`[​](http://flet.dev/docs/controls/appbar#title "Direct link to title")

The primary `Control` displayed in the app bar. Typically a [`Text`](https://flet.dev/docs/controls/text) control that contains a description of the current contents of the app.

**Note** that, if `AppBar.adaptive=True` and the app is opened on an iOS or macOS device, this control will be automatically centered.

Value is of type `Control`.

### `title_spacing`[​](http://flet.dev/docs/controls/appbar#title_spacing "Direct link to title_spacing")

The spacing around `title` on the horizontal axis. It is applied even if there are no `leading` or `actions` controls.

If you want `title` to take all the space available, set this value to `0.0`.

Value is of type [`OptionalNumber`](https://flet.dev/docs/reference/types/aliases#optionalnumber).

### `title_text_style`[​](http://flet.dev/docs/controls/appbar#title_text_style "Direct link to title_text_style")

The style to be used for the `Text` controls in the `title`.

Value is of type [`TextStyle`](https://flet.dev/docs/reference/types/textstyle).

### `toolbar_height`[​](http://flet.dev/docs/controls/appbar#toolbar_height "Direct link to toolbar_height")

Defines the height of the toolbar component of an AppBar.

Value is of tye [`OptionalNumber`](https://flet.dev/docs/reference/types/aliases#optionalnumber) and defaults to `56.0`.

### `toolbar_opacity`[​](http://flet.dev/docs/controls/appbar#toolbar_opacity "Direct link to toolbar_opacity")

The opacity of the toolbar. Value ranges from `0.0` (transparent) to `1.0` (fully opaque).

Value is of type [`OptionalNumber`](https://flet.dev/docs/reference/types/aliases#optionalnumber) and defaults to `1.0`.

### `toolbar_text_style`[​](http://flet.dev/docs/controls/appbar#toolbar_text_style "Direct link to toolbar_text_style")

The style to be used for the `Text` controls in the app bar's `leading` and `actions` (but not `title`).

Value is of type [`TextStyle`](https://flet.dev/docs/reference/types/textstyle).