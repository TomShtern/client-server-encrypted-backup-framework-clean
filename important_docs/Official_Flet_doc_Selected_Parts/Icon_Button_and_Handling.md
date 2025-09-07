Title: IconButton - Flet

URL Source: http://docs.flet.dev/controls/iconbutton/?h=click+han

Markdown Content:
[](https://github.com/flet-dev/flet/edit/main/sdk/python/packages/flet/docs/controls/iconbutton.md "Edit this page")[](https://github.com/flet-dev/flet/raw/main/sdk/python/packages/flet/docs/controls/iconbutton.md "View source of this page")
Examples[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#examples "Permanent link")
---------------------------------------------------------------------------------------------

[Live example](https://flet-controls-gallery.fly.dev/buttons/iconbutton)

### Handling clicks[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#handling-clicks "Permanent link")

```
import flet as ft

def main(page: ft.Page):
    page.title = "IconButton Example"

    def button_clicked(e: ft.Event[ft.IconButton]):
        button.data += 1
        message.value = f"Button clicked {button.data} time(s)"
        page.update()

    page.add(
        button := ft.IconButton(
            icon=ft.Icons.PLAY_CIRCLE_FILL_OUTLINED,
            data=0,
            on_click=button_clicked,
        ),
        message := ft.Text(),
    )

ft.run(main)
```

[![Image 1: handling-clicks](https://docs.flet.dev/examples/controls/icon_button/media/handling_clicks.gif)](https://docs.flet.dev/examples/controls/icon_button/media/handling_clicks.gif)

### Selected icon[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#selected-icon "Permanent link")

```
import flet as ft

def main(page: ft.Page):
    page.title = "IconButton Example"
    page.padding = 10
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def handle_click(e: ft.Event[ft.IconButton]):
        e.control.selected = not e.control.selected
        e.control.update()

    page.add(
        ft.IconButton(
            icon=ft.Icons.BATTERY_1_BAR,
            selected_icon=ft.Icons.BATTERY_FULL,
            scale=5,
            on_click=handle_click,
            selected=False,
            style=ft.ButtonStyle(
                color={
                    ft.ControlState.SELECTED: ft.Colors.GREEN,
                    ft.ControlState.DEFAULT: ft.Colors.RED,
                }
            ),
        )
    )

ft.run(main)
```

IconButton[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton "Permanent link")
------------------------------------------------------------------------------------------------------

Bases: `LayoutControl`, `AdaptiveControl`

An icon button is a round button with an icon in the middle that reacts to touches by filling with color (ink).

Icon buttons are commonly used in the toolbars, but they can be used in many other places as well.

### adaptive[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.adaptive "Permanent link")

```
adaptive: bool | None = None
```

Enables platform-specific rendering or inheritance of adaptiveness from parent controls.

### align[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.align "Permanent link")

Alignment of the control within its parent.

### alignment[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.alignment "Permanent link")

Defines how the icon is positioned within the IconButton. Alignment is an instance of [`Alignment`](https://docs.flet.dev/types/alignment/#flet.Alignment "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">Alignment</span>") class.

Defaults to [`Alignment.CENTER`](https://docs.flet.dev/types/alignment/#flet.Alignment.CENTER "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">CENTER</span>").

### animate_align[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.animate_align "Permanent link")

Enables implicit animation of the [`align`](https://docs.flet.dev/controls/layoutcontrol/#flet.LayoutControl.align "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">align</span>") property.

More information [here](https://docs.flet-docs.pages.dev/cookbook/cookbook/animations).

### animate_margin[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.animate_margin "Permanent link")

Enables implicit animation of the [`margin`](https://docs.flet.dev/controls/layoutcontrol/#flet.LayoutControl.margin "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">margin</span>") property.

More information [here](https://docs.flet-docs.pages.dev/cookbook/cookbook/animations).

### animate_offset[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.animate_offset "Permanent link")

Enables implicit animation of the [`offset`](https://docs.flet.dev/controls/layoutcontrol/#flet.LayoutControl.offset "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">offset</span>") property.

More information [here](https://docs.flet-docs.pages.dev/cookbook/cookbook/animations).

### animate_opacity[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.animate_opacity "Permanent link")

Enables implicit animation of the [`opacity`](https://docs.flet.dev/controls/layoutcontrol/#flet.LayoutControl.opacity "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">opacity</span>") property.

More information [here](https://docs.flet-docs.pages.dev/cookbook/cookbook/animations).

### animate_position[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.animate_position "Permanent link")

Enables implicit animation of the positioning properties ([`left`](https://docs.flet.dev/controls/layoutcontrol/#flet.LayoutControl.left "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">left</span>"), [`right`](https://docs.flet.dev/controls/layoutcontrol/#flet.LayoutControl.right "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">right</span>"), [`top`](https://docs.flet.dev/controls/layoutcontrol/#flet.LayoutControl.top "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">top</span>") and [`bottom`](https://docs.flet.dev/controls/layoutcontrol/#flet.LayoutControl.bottom "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">bottom</span>")).

More information [here](https://docs.flet-docs.pages.dev/cookbook/cookbook/animations).

### animate_rotation[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.animate_rotation "Permanent link")

Enables implicit animation of the [`rotate`](https://docs.flet.dev/controls/layoutcontrol/#flet.LayoutControl.rotate "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">rotate</span>") property.

More information [here](https://docs.flet-docs.pages.dev/cookbook/cookbook/animations).

### animate_scale[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.animate_scale "Permanent link")

Enables implicit animation of the [`scale`](https://docs.flet.dev/controls/layoutcontrol/#flet.LayoutControl.scale "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">scale</span>") property.

More information [here](https://docs.flet-docs.pages.dev/cookbook/cookbook/animations).

### aspect_ratio[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.aspect_ratio "Permanent link")

```
aspect_ratio: Number | None = None
```

TBD

### autofocus[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.autofocus "Permanent link")

Whether this control will be provided initial focus. If there is more than one control on a page with autofocus set, then the first one added to the page will get focus.

### badge[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.badge "Permanent link")

A badge to show on top of this control.

### bgcolor[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.bgcolor "Permanent link")

```
bgcolor: ColorValue | None = field(
    default=None, metadata={"skip": True}
)
```

The button's background color.

### bottom[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.bottom "Permanent link")

The distance that the child's bottom edge is inset from the bottom of the stack.

Note
Effective only if this control is a descendant of one of the following: [`Stack`](https://docs.flet.dev/controls/stack/#flet.Stack "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">Stack</span>") control, [`Page.overlay`](https://docs.flet.dev/controls/page/#flet.Page.overlay "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">overlay</span>") list.

### col[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.col "Permanent link")

If a parent of this control is a [`ResponsiveRow`](https://docs.flet.dev/controls/responsiverow/#flet.ResponsiveRow "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">ResponsiveRow</span>"), this property is used to determine how many virtual columns of a screen this control will span.

Can be a number or a dictionary configured to have a different value for specific breakpoints, for example `col={"sm": 6}`.

This control spans the 12 virtual columns by default.

Dimensions
| Breakpoint | Dimension |
| --- | --- |
| xs | <576px |
| sm | ≥576px |
| md | ≥768px |
| lg | ≥992px |
| xl | ≥1200px |
| xxl | ≥1400px |

### data[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.data "Permanent link")

Arbitrary data of any type.

### disabled[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.disabled "Permanent link")

Every control has `disabled` property which is `False` by default - control and all its children are enabled.

Note
The value of this property will be propagated down to all children controls recursively.

Example
For example, if you have a form with multiple entry controls you can disable them all together by disabling container:

```
ft.Column(
    disabled = True,
    controls=[
        ft.TextField(),
        ft.TextField()
    ]
)
```

### disabled_color[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.disabled_color "Permanent link")

The color to use for the icon inside the button when disabled.

### enable_feedback[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.enable_feedback "Permanent link")

```
enable_feedback: bool | None = None
```

Whether detected gestures should provide acoustic and/or haptic feedback. On Android, for example, setting this to `True` produce a click sound and a long-press will produce a short vibration.

### expand[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.expand "Permanent link")

Specifies whether/how this control should expand to fill available space in its parent layout.

More information [here](https://docs.flet-docs.pages.dev/cookbook/expanding-controls/#expand).

Note
Has effect only if the direct parent of this control is one of the following controls, or their subclasses: [`Column`](https://docs.flet.dev/controls/column/#flet.Column "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">Column</span>"), [`Row`](https://docs.flet.dev/controls/row/#flet.Row "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">Row</span>"), [`View`](https://docs.flet.dev/controls/view/#flet.View "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">View</span>"), [`Page`](https://docs.flet.dev/controls/page/#flet.Page "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">Page</span>").

### expand_loose[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.expand_loose "Permanent link")

```
expand_loose: bool = False
```

Allows the control to expand along the main axis if space is available, but does not require it to fill all available space.

More information [here](https://docs.flet-docs.pages.dev/cookbook/expanding-controls/#expand_loose).

Note
If `expand_loose` is `True`, it will have effect only if:

*   `expand` is not `None` and
*   the direct parent of this control is one of the following controls, or their subclasses: [`Column`](https://docs.flet.dev/controls/column/#flet.Column "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">Column</span>"), [`Row`](https://docs.flet.dev/controls/row/#flet.Row "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">Row</span>"), [`View`](https://docs.flet.dev/controls/view/#flet.View "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">View</span>"), [`Page`](https://docs.flet.dev/controls/page/#flet.Page "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">Page</span>").

### focus_color[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.focus_color "Permanent link")

The color of this button when in focus.

### height[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.height "Permanent link")

Imposed Control height in virtual pixels.

### highlight_color[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.highlight_color "Permanent link")

The button's color when the button is pressed. The highlight fades in quickly as the button is held down.

### hover_color[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.hover_color "Permanent link")

The color of this button when hovered.

### icon[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.icon "Permanent link")

Icon shown in the button.

### icon_color[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.icon_color "Permanent link")

The foreground color of the icon.

### icon_size[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.icon_size "Permanent link")

```
icon_size: Number | None = None
```

The [`icon`](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.icon "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">icon</span>")'s size in virtual pixels.

Defaults to `24`.

### key[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.key "Permanent link")

### left[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.left "Permanent link")

The distance that the child's left edge is inset from the left of the stack.

Note
Effective only if this control is a descendant of one of the following: [`Stack`](https://docs.flet.dev/controls/stack/#flet.Stack "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">Stack</span>") control, [`Page.overlay`](https://docs.flet.dev/controls/page/#flet.Page.overlay "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">overlay</span>") list.

### margin[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.margin "Permanent link")

Sets the margin of the control.

### mouse_cursor[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.mouse_cursor "Permanent link")

```
mouse_cursor: MouseCursor | None = field(
    default=None, metadata={"skip": True}
)
```

The cursor to be displayed when a mouse pointer enters or is hovering over this control.

### offset[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.offset "Permanent link")

Applies a translation transformation before painting the control.

The translation is expressed as an `Offset` scaled to the control's size. So, `Offset(x=0.25, y=0)`, for example, will result in a horizontal translation of one quarter the width of this control.

Example
The following example displays container at `0, 0` top left corner of a stack as transform applies `-1 * 100, -1 * 100` (`offset * control's size`) horizontal and vertical translations to the control:

```
import flet as ft

def main(page: ft.Page):
    page.add(
        ft.Stack(
            width=1000,
            height=1000,
            controls=[
                ft.Container(
                    bgcolor="red",
                    width=100,
                    height=100,
                    left=100,
                    top=100,
                    offset=ft.Offset(-1, -1),
                )
            ],
        )
    )

ft.run(main)
```

### on_animation_end[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.on_animation_end "Permanent link")

Called when animation completes.

Can be used to chain multiple animations.

The `data` property of the event handler argument contains the name of the animation.

More information [here](https://docs.flet-docs.pages.dev/cookbook/cookbook/animations).

### on_blur[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.on_blur "Permanent link")

Called when the control has lost focus.

### on_click[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.on_click "Permanent link")

Called when a user clicks this button.

### on_focus[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.on_focus "Permanent link")

Called when the control has received focus.

### opacity[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.opacity "Permanent link")

Defines the transparency of the control.

Value ranges from `0.0` (completely transparent) to `1.0` (completely opaque without any transparency).

### padding[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.padding "Permanent link")

Defines the padding around this button. The entire padded icon will react to input gestures.

Defaults to `Padding.all(8)`.

### page[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.page "Permanent link")

The page to which this control belongs to.

### parent[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.parent "Permanent link")

The direct ancestor(parent) of this control.

It defaults to `None` and will only have a value when this control is mounted (added to the page tree).

The `Page` control (which is the root of the tree) is an exception - it always has `parent=None`.

### right[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.right "Permanent link")

The distance that the child's right edge is inset from the right of the stack.

Note
Effective only if this control is a descendant of one of the following: [`Stack`](https://docs.flet.dev/controls/stack/#flet.Stack "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">Stack</span>") control, [`Page.overlay`](https://docs.flet.dev/controls/page/#flet.Page.overlay "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">overlay</span>") list.

### rotate[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.rotate "Permanent link")

Transforms this control using a rotation around its center.

The value of `rotate` property could be one of the following types:

*   `number` - a rotation in clockwise radians. Full circle `360°` is `math.pi * 2` radians, `90°` is `pi / 2`, `45°` is `pi / 4`, etc.
*   `Rotate` - allows to specify rotation `angle` as well as `alignment` - the location of rotation center.

Example
For example:

```
ft.Image(
    src="https://picsum.photos/100/100",
    width=100,
    height=100,
    border_radius=5,
    rotate=Rotate(angle=0.25 * pi, alignment=ft.Alignment.CENTER_LEFT)
)
```

### rtl[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.rtl "Permanent link")

Whether the text direction of the control should be right-to-left (RTL).

### scale[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.scale "Permanent link")

Scales this control along the 2D plane. Default scale factor is `1.0`, meaning no-scale.

Setting this property to `0.5`, for example, makes this control twice smaller, while `2.0` makes it twice larger.

Different scale multipliers can be specified for `x` and `y` axis, by setting `Control.scale` property to an instance of `Scale` class. Either `scale` or `scale_x` and `scale_y` could be specified, but not all of them.

Example

```
ft.Image(
    src="https://picsum.photos/100/100",
    width=100,
    height=100,
    border_radius=5,
    scale=ft.Scale(scale_x=2, scale_y=0.5)
)
```

### selected[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.selected "Permanent link")

```
selected: bool | None = None
```

The optional selection state of the icon button.

If this property is not set, the button will behave as a normal push button, otherwise, the button will toggle between showing [`icon`](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.icon "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">icon</span>") (when `False`), and [`selected_icon`](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.selected_icon "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">selected_icon</span>") (when `True`).

### selected_icon[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.selected_icon "Permanent link")

The icon to be shown in this button for the 'selected' state.

### selected_icon_color[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.selected_icon_color "Permanent link")

The icon color for the 'selected' state of this button.

An example of icon toggle button:

[![Image 2](https://docs.flet.dev/img/blog/gradients/toggle-icon-button.gif)](https://docs.flet.dev/img/blog/gradients/toggle-icon-button.gif)

```
import flet as ft

def main(page: ft.Page):

    def toggle_icon_button(e):
        e.control.selected = not e.control.selected

    page.add(
        ft.IconButton(
            icon=ft.Icons.BATTERY_1_BAR,
            selected_icon=ft.Icons.BATTERY_FULL,
            on_click=toggle_icon_button,
            selected=False,
            style=ft.ButtonStyle(
                color={
                    ft.ControlState.SELECTED: ft.Colors.GREEN,
                    ft.ControlState.DEFAULT: ft.Colors.RED
                },
            ),
        )
    )

ft.run(main)
```

### size_constraints[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.size_constraints "Permanent link")

Size constraints for this button.

### splash_color[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.splash_color "Permanent link")

The primary color of the button when the button is in the down (pressed) state.

### splash_radius[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.splash_radius "Permanent link")

```
splash_radius: Number | None = None
```

The splash radius.

Note
This value is honoured only when in Material 2 ([`Theme.use_material3`](https://docs.flet.dev/types/theme/#flet.Theme.use_material3 "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">use_material3</span>") is `False`).

### tooltip[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.tooltip "Permanent link")

The tooltip ot show when this control is hovered over.

### top[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.top "Permanent link")

The distance that the child's top edge is inset from the top of the stack.

Note
Effective only if this control is a descendant of one of the following: [`Stack`](https://docs.flet.dev/controls/stack/#flet.Stack "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">Stack</span>") control, [`Page.overlay`](https://docs.flet.dev/controls/page/#flet.Page.overlay "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">overlay</span>") list.

### url[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.url "Permanent link")

The URL to open when this button is clicked.

Additionally, if [`on_click`](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.on_click "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">on_click</span>") event callback is provided, it is fired after that.

### visible[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.visible "Permanent link")

Every control has `visible` property which is `True` by default - control is rendered on the page. Setting `visible` to `False` completely prevents control (and all its children if any) from rendering on a page canvas. Hidden controls cannot be focused or selected with a keyboard or mouse and they do not emit any events.

### visual_density[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.visual_density "Permanent link")

Defines how compact the control's layout will be.

### width[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.width "Permanent link")

Imposed Control width in virtual pixels.

### before_event[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.before_event "Permanent link")

### before_update[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.before_update "Permanent link")

```
before_update()
```

### build[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.build "Permanent link")

```
build()
```

Called once during control initialization to define its child controls. self.page is available in this method.

### focus[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.focus "Permanent link")

```
focus()
```

Moves focus to this button.

### is_isolated[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.is_isolated "Permanent link")

```
is_isolated()
```

### update[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.update "Permanent link")

```
update() -> None
```

### will_unmount[#](https://docs.flet.dev/controls/iconbutton/?h=click+han#flet.IconButton.will_unmount "Permanent link")

```
will_unmount()