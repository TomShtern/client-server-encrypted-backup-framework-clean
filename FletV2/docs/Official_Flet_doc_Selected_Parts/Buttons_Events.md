Title: Button - Flet

URL Source: http://docs.flet.dev/controls/button/?h=on_cli

Markdown Content:
[](https://github.com/flet-dev/flet/edit/main/sdk/python/packages/flet/docs/controls/button.md "Edit this page")[](https://github.com/flet-dev/flet/raw/main/sdk/python/packages/flet/docs/controls/button.md "View source of this page")
Examples[#](https://docs.flet.dev/controls/button/?h=on_cli#examples "Permanent link")
--------------------------------------------------------------------------------------

[Live example](https://flet-controls-gallery.fly.dev/buttons/elevatedbutton)

### Basic Example[#](https://docs.flet.dev/controls/button/?h=on_cli#basic-example "Permanent link")

```
import flet as ft

def main(page: ft.Page):
    page.title = "Button Example"

    page.add(
        ft.Button(content="Elevated button"),
        ft.Button(content="Disabled button", disabled=True),
    )

ft.run(main)
```

[![Image 1: basic](https://docs.flet.dev/examples/controls/button/media/basic.png)](https://docs.flet.dev/examples/controls/button/media/basic.png)

### Icons[#](https://docs.flet.dev/controls/button/?h=on_cli#icons "Permanent link")

```
import flet as ft

def main(page: ft.Page):
    page.title = "Button Example"

    page.add(
        ft.Button(content="Button with icon", icon=ft.Icons.WAVES_ROUNDED),
        ft.Button(
            content="Button with colorful icon",
            icon=ft.Icons.PARK_ROUNDED,
            icon_color=ft.Colors.GREEN_400,
        ),
    )

ft.run(main)
```

[![Image 2: icons](https://docs.flet.dev/examples/controls/button/media/icons.png)](https://docs.flet.dev/examples/controls/button/media/icons.png)

### Handling clicks[#](https://docs.flet.dev/controls/button/?h=on_cli#handling-clicks "Permanent link")

```
import flet as ft

def main(page: ft.Page):
    page.title = "Button Example"
    page.theme_mode = ft.ThemeMode.LIGHT

    def button_clicked(e: ft.Event[ft.Button]):
        button.data += 1
        message.value = f"Button clicked {button.data} time(s)"
        page.update()

    page.add(
        button := ft.Button(
            content="Button with 'click' event",
            data=0,
            on_click=button_clicked,
        ),
        message := ft.Text(),
    )

ft.run(main)
```

[![Image 3: handling-clicks](https://docs.flet.dev/examples/controls/button/media/handling_clicks.gif)](https://docs.flet.dev/examples/controls/button/media/handling_clicks.gif)

### Custom content[#](https://docs.flet.dev/controls/button/?h=on_cli#custom-content "Permanent link")

```
import flet as ft

def main(page: ft.Page):
    page.title = "Button Example"

    page.add(
        ft.Button(
            width=150,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                controls=[
                    ft.Icon(ft.Icons.FAVORITE, color=ft.Colors.PINK),
                    ft.Icon(ft.Icons.AUDIOTRACK, color=ft.Colors.GREEN),
                    ft.Icon(ft.Icons.BEACH_ACCESS, color=ft.Colors.BLUE),
                ],
            ),
        ),
        ft.Button(
            content=ft.Container(
                padding=ft.Padding.all(10),
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=5,
                    controls=[
                        ft.Text(value="Compound button", size=20),
                        ft.Text(value="This is secondary text"),
                    ],
                ),
            ),
        ),
    )

ft.run(main)
```

[![Image 4: custom-content](https://docs.flet.dev/examples/controls/button/media/custom_content.png)](https://docs.flet.dev/examples/controls/button/media/custom_content.png)

### Shapes[#](https://docs.flet.dev/controls/button/?h=on_cli#shapes "Permanent link")

### Styling[#](https://docs.flet.dev/controls/button/?h=on_cli#styling "Permanent link")

```
import flet as ft

def main(page: ft.Page):
    page.padding = 50
    page.theme_mode = ft.ThemeMode.LIGHT

    page.add(
        ft.Button(
            content="Styled button 1",
            style=ft.ButtonStyle(
                color={
                    ft.ControlState.HOVERED: ft.Colors.WHITE,
                    ft.ControlState.FOCUSED: ft.Colors.BLUE,
                    ft.ControlState.DEFAULT: ft.Colors.BLACK,
                },
                bgcolor={
                    ft.ControlState.FOCUSED: ft.Colors.PINK_200,
                    ft.ControlState.DEFAULT: ft.Colors.YELLOW,
                },
                padding={ft.ControlState.HOVERED: 20},
                overlay_color=ft.Colors.TRANSPARENT,
                elevation={
                    ft.ControlState.DEFAULT: 0,
                    ft.ControlState.HOVERED: 5,
                    ft.ControlState.PRESSED: 10,
                },
                animation_duration=500,
                side={
                    ft.ControlState.DEFAULT: ft.BorderSide(1, color=ft.Colors.BLUE_100),
                    ft.ControlState.HOVERED: ft.BorderSide(3, color=ft.Colors.BLUE_400),
                    ft.ControlState.PRESSED: ft.BorderSide(6, color=ft.Colors.BLUE_600),
                },
                shape={
                    ft.ControlState.HOVERED: ft.RoundedRectangleBorder(radius=20),
                    ft.ControlState.DEFAULT: ft.RoundedRectangleBorder(radius=2),
                },
            ),
        )
    )

ft.run(main)
```

### Animate on hover[#](https://docs.flet.dev/controls/button/?h=on_cli#animate-on-hover "Permanent link")

```
import flet as ft

def main(page: ft.Page):
    def animate(e: ft.Event[ft.Button]):
        e.control.rotate = 0.1 if e.data else 0
        page.update()

    page.add(
        ft.Button(
            content="Hover over me, I'm animated!",
            rotate=0,
            animate_rotation=100,
            on_hover=animate,
            on_click=lambda e: page.add(ft.Text("Clicked! Try a long press!")),
            on_long_press=lambda e: page.add(ft.Text("I knew you could do it!")),
        )
    )

ft.run(main)
```

Button[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button "Permanent link")
---------------------------------------------------------------------------------------

Bases: `LayoutControl`, `AdaptiveControl`

A customizable button control that can display text, icons, or both. It supports various styles, colors, and event handlers for user interaction.

Example

```
import flet as ft

def main(page: ft.Page):
    def on_click(e):
        print("Button clicked!")

    page.add(
        ft.Button(
            content="Click Me",
            icon=ft.Icons.ADD,
            color="white",
            bgcolor="blue",
            on_click=on_click,
        )
    )

ft.run(main)
```

### adaptive[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.adaptive "Permanent link")

```
adaptive: bool | None = None
```

Enables platform-specific rendering or inheritance of adaptiveness from parent controls.

### align[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.align "Permanent link")

Alignment of the control within its parent.

### animate_align[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.animate_align "Permanent link")

Enables implicit animation of the [`align`](https://docs.flet.dev/controls/layoutcontrol/#flet.LayoutControl.align "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">align</span>") property.

More information [here](https://docs.flet-docs.pages.dev/cookbook/cookbook/animations).

### animate_margin[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.animate_margin "Permanent link")

Enables implicit animation of the [`margin`](https://docs.flet.dev/controls/layoutcontrol/#flet.LayoutControl.margin "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">margin</span>") property.

More information [here](https://docs.flet-docs.pages.dev/cookbook/cookbook/animations).

### animate_offset[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.animate_offset "Permanent link")

Enables implicit animation of the [`offset`](https://docs.flet.dev/controls/layoutcontrol/#flet.LayoutControl.offset "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">offset</span>") property.

More information [here](https://docs.flet-docs.pages.dev/cookbook/cookbook/animations).

### animate_opacity[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.animate_opacity "Permanent link")

Enables implicit animation of the [`opacity`](https://docs.flet.dev/controls/layoutcontrol/#flet.LayoutControl.opacity "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">opacity</span>") property.

More information [here](https://docs.flet-docs.pages.dev/cookbook/cookbook/animations).

### animate_position[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.animate_position "Permanent link")

Enables implicit animation of the positioning properties ([`left`](https://docs.flet.dev/controls/layoutcontrol/#flet.LayoutControl.left "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">left</span>"), [`right`](https://docs.flet.dev/controls/layoutcontrol/#flet.LayoutControl.right "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">right</span>"), [`top`](https://docs.flet.dev/controls/layoutcontrol/#flet.LayoutControl.top "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">top</span>") and [`bottom`](https://docs.flet.dev/controls/layoutcontrol/#flet.LayoutControl.bottom "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">bottom</span>")).

More information [here](https://docs.flet-docs.pages.dev/cookbook/cookbook/animations).

### animate_rotation[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.animate_rotation "Permanent link")

Enables implicit animation of the [`rotate`](https://docs.flet.dev/controls/layoutcontrol/#flet.LayoutControl.rotate "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">rotate</span>") property.

More information [here](https://docs.flet-docs.pages.dev/cookbook/cookbook/animations).

### animate_scale[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.animate_scale "Permanent link")

Enables implicit animation of the [`scale`](https://docs.flet.dev/controls/layoutcontrol/#flet.LayoutControl.scale "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">scale</span>") property.

More information [here](https://docs.flet-docs.pages.dev/cookbook/cookbook/animations).

### aspect_ratio[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.aspect_ratio "Permanent link")

```
aspect_ratio: Number | None = None
```

TBD

### autofocus[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.autofocus "Permanent link")

```
autofocus: bool | None = None
```

### badge[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.badge "Permanent link")

A badge to show on top of this control.

### bgcolor[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.bgcolor "Permanent link")

```
bgcolor: ColorValue | None = field(
    default=None, metadata={"skip": True}
)
```

### bottom[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.bottom "Permanent link")

The distance that the child's bottom edge is inset from the bottom of the stack.

Note
Effective only if this control is a descendant of one of the following: [`Stack`](https://docs.flet.dev/controls/stack/#flet.Stack "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">Stack</span>") control, [`Page.overlay`](https://docs.flet.dev/controls/page/#flet.Page.overlay "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">overlay</span>") list.

### clip_behavior[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.clip_behavior "Permanent link")

### col[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.col "Permanent link")

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

### color[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.color "Permanent link")

### content[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.content "Permanent link")

### data[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.data "Permanent link")

Arbitrary data of any type.

### disabled[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.disabled "Permanent link")

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

### elevation[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.elevation "Permanent link")

```
elevation: Number = field(
    default=1, metadata={"skip": True}
)
```

### expand[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.expand "Permanent link")

Specifies whether/how this control should expand to fill available space in its parent layout.

More information [here](https://docs.flet-docs.pages.dev/cookbook/expanding-controls/#expand).

Note
Has effect only if the direct parent of this control is one of the following controls, or their subclasses: [`Column`](https://docs.flet.dev/controls/column/#flet.Column "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">Column</span>"), [`Row`](https://docs.flet.dev/controls/row/#flet.Row "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">Row</span>"), [`View`](https://docs.flet.dev/controls/view/#flet.View "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">View</span>"), [`Page`](https://docs.flet.dev/controls/page/#flet.Page "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">Page</span>").

### expand_loose[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.expand_loose "Permanent link")

```
expand_loose: bool = False
```

Allows the control to expand along the main axis if space is available, but does not require it to fill all available space.

More information [here](https://docs.flet-docs.pages.dev/cookbook/expanding-controls/#expand_loose).

Note
If `expand_loose` is `True`, it will have effect only if:

*   `expand` is not `None` and
*   the direct parent of this control is one of the following controls, or their subclasses: [`Column`](https://docs.flet.dev/controls/column/#flet.Column "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">Column</span>"), [`Row`](https://docs.flet.dev/controls/row/#flet.Row "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">Row</span>"), [`View`](https://docs.flet.dev/controls/view/#flet.View "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">View</span>"), [`Page`](https://docs.flet.dev/controls/page/#flet.Page "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">Page</span>").

### height[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.height "Permanent link")

Imposed Control height in virtual pixels.

### icon[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.icon "Permanent link")

### icon_color[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.icon_color "Permanent link")

### key[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.key "Permanent link")

### left[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.left "Permanent link")

The distance that the child's left edge is inset from the left of the stack.

Note
Effective only if this control is a descendant of one of the following: [`Stack`](https://docs.flet.dev/controls/stack/#flet.Stack "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">Stack</span>") control, [`Page.overlay`](https://docs.flet.dev/controls/page/#flet.Page.overlay "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">overlay</span>") list.

### margin[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.margin "Permanent link")

Sets the margin of the control.

### offset[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.offset "Permanent link")

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

### on_animation_end[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.on_animation_end "Permanent link")

Called when animation completes.

Can be used to chain multiple animations.

The `data` property of the event handler argument contains the name of the animation.

More information [here](https://docs.flet-docs.pages.dev/cookbook/cookbook/animations).

### on_blur[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.on_blur "Permanent link")

### on_cli ck[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.on_click "Permanent link")

### on_focus[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.on_focus "Permanent link")

### on_hover[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.on_hover "Permanent link")

### on_long_press[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.on_long_press "Permanent link")

### opacity[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.opacity "Permanent link")

Defines the transparency of the control.

Value ranges from `0.0` (completely transparent) to `1.0` (completely opaque without any transparency).

### page[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.page "Permanent link")

The page to which this control belongs to.

### parent[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.parent "Permanent link")

The direct ancestor(parent) of this control.

It defaults to `None` and will only have a value when this control is mounted (added to the page tree).

The `Page` control (which is the root of the tree) is an exception - it always has `parent=None`.

### right[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.right "Permanent link")

The distance that the child's right edge is inset from the right of the stack.

Note
Effective only if this control is a descendant of one of the following: [`Stack`](https://docs.flet.dev/controls/stack/#flet.Stack "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">Stack</span>") control, [`Page.overlay`](https://docs.flet.dev/controls/page/#flet.Page.overlay "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">overlay</span>") list.

### rotate[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.rotate "Permanent link")

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

### rtl[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.rtl "Permanent link")

Whether the text direction of the control should be right-to-left (RTL).

### scale[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.scale "Permanent link")

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

### style[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.style "Permanent link")

### tooltip[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.tooltip "Permanent link")

The tooltip ot show when this control is hovered over.

### top[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.top "Permanent link")

The distance that the child's top edge is inset from the top of the stack.

Note
Effective only if this control is a descendant of one of the following: [`Stack`](https://docs.flet.dev/controls/stack/#flet.Stack "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">Stack</span>") control, [`Page.overlay`](https://docs.flet.dev/controls/page/#flet.Page.overlay "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">overlay</span>") list.

### url[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.url "Permanent link")

### visible[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.visible "Permanent link")

Every control has `visible` property which is `True` by default - control is rendered on the page. Setting `visible` to `False` completely prevents control (and all its children if any) from rendering on a page canvas. Hidden controls cannot be focused or selected with a keyboard or mouse and they do not emit any events.

### width[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.width "Permanent link")

Imposed Control width in virtual pixels.

### before_event[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.before_event "Permanent link")

### before_update[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.before_update "Permanent link")

```
before_update()
```

### build[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.build "Permanent link")

```
build()
```

Called once during control initialization to define its child controls. self.page is available in this method.

### is_isolated[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.is_isolated "Permanent link")

```
is_isolated()
```

### update[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.update "Permanent link")

```
update() -> None
```

### will_unmount[#](https://docs.flet.dev/controls/button/?h=on_cli#flet.Button.will_unmount "Permanent link")

```
will_unmount()
```