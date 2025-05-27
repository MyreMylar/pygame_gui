.. _theme-check-box:

UICheckBox Theming Parameters
=============================

The :class:`UICheckBox <pygame_gui.elements.UICheckBox>` theming block id is 'check_box'.

Colours
-------

:class:`UICheckBox <pygame_gui.elements.UICheckBox>` accepts the following colour parameters in a 'colours' block:

 - "**normal_bg**" - The background colour of the checkbox in its normal state.
 - "**normal_border**" - The border colour of the checkbox in its normal state.
 - "**hovered_bg**" - The background colour of the checkbox when it is being hovered over.
 - "**hovered_border**" - The border colour of the checkbox when it is being hovered over.
 - "**disabled_bg**" - The background colour of the checkbox when it is disabled.
 - "**disabled_border**" - The border colour of the checkbox when it is disabled.
 - "**selected_bg**" - The background colour of the checkbox when it is checked or indeterminate.
 - "**selected_border**" - The border colour of the checkbox when it is checked or indeterminate.
 - "**normal_text**" - The colour of the check symbol when the checkbox is in its normal state.
 - "**hovered_text**" - The colour of the check symbol when the checkbox is being hovered over.
 - "**disabled_text**" - The colour of the check symbol when the checkbox is disabled.
 - "**selected_text**" - The colour of the check symbol when the checkbox is checked or indeterminate.
 - "**normal_text_shadow**" - The colour of the check symbol's shadow in normal state.
 - "**hovered_text_shadow**" - The colour of the check symbol's shadow when hovered.
 - "**disabled_text_shadow**" - The colour of the check symbol's shadow when disabled.
 - "**selected_text_shadow**" - The colour of the check symbol's shadow when checked or indeterminate.

Font
----

:class:`UICheckBox <pygame_gui.elements.UICheckBox>` accepts the following font parameter in a 'font' block:

 - "**name**" - The name of the font to use for the check symbol. Defaults to the UI theme's default font.
 - "**size**" - The size of the font to use for the check symbol.
 - "**bold**" - Whether the font should be bold.
 - "**italic**" - Whether the font should be italic.

Miscellaneous
-------------

:class:`UICheckBox <pygame_gui.elements.UICheckBox>` accepts the following miscellaneous parameters in a 'misc' block:

 - "**shape**" - Can be one of 'rectangle' or 'rounded_rectangle'. Different shapes for this UI element.
 - "**shape_corner_radius**" - Only used if our shape is 'rounded_rectangle'. It sets the radius, or radii, used for the rounded corners. Use a single integer to set all corners to the same radius, or four integers separated by commas to set each corner individually.
 - "**border_width**" - The width in pixels of the border around the checkbox. Defaults to 1.
 - "**shadow_width**" - The width in pixels of the shadow behind the checkbox. Defaults to 2.
 - "**check_symbol**" - The symbol to display when the checkbox is checked. Defaults to "✓".
 - "**indeterminate_symbol**" - The symbol to display when the checkbox is in indeterminate state. Defaults to "−".
 - "**text_offset**" - The distance in pixels between the checkbox and its text label. Defaults to 5.
 - "**tool_tip_delay**" - Time in seconds before the checkbox's tool tip (if it has one) will appear. Default is "1.0".

Sub-elements
------------

The :class:`UICheckBox <pygame_gui.elements.UICheckBox>` contains a :class:`UILabel <pygame_gui.elements.UILabel>` for its text, so you can use the block ID 'check_box.label' to style the text label.

There is more information on theming the label at :ref:`theme-label`.

Example
-------

Here is an example of a checkbox block in a JSON theme file, using the parameters described above.

.. code-block:: json
   :caption: check_box.json
   :linenos:

    {
        "check_box":
        {
            "colours":
            {
                "normal_bg": "#25292e",
                "normal_border": "#AAAAAA",
                "hovered_bg": "#35393e", 
                "hovered_border": "#B0B0B0",
                "disabled_bg": "#25292e",
                "disabled_border": "#808080",
                "selected_bg": "#193784",
                "selected_border": "#8080B0",
                "normal_text": "#c5cbd8",
                "hovered_text": "#FFFFFF",
                "disabled_text": "#6d736f",
                "selected_text": "#FFFFFF",
                "normal_text_shadow": "#10101070",
                "hovered_text_shadow": "#10101070", 
                "disabled_text_shadow": "#10101070",
                "selected_text_shadow": "#10101070"
            },
            "font":
            {
                "name": "fira_code",
                "size": "14",
                "bold": "0",
                "italic": "0"
            },
            "images":
            {
                "normal_image": {
                    "package": "data.images",
                    "resource": "checkbox_states.png",
                    "sub_surface_rect": "0,0,16,16"
                },
                "hovered_image": {
                    "package": "data.images",
                    "resource": "checkbox_states.png",
                    "sub_surface_rect": "16,0,16,16"
                },
                "selected_image": {
                    "package": "data.images",
                    "resource": "checkbox_states.png",
                    "sub_surface_rect": "32,0,16,16"
                },
                "disabled_image": {
                    "package": "data.images",
                    "resource": "checkbox_states.png",
                    "sub_surface_rect": "48,0,16,16"
                }
            },
            "misc":
            {
                "shape": "rounded_rectangle",
                "shape_corner_radius": "3",
                "border_width": "2",
                "shadow_width": "2",
                "check_symbol": "✓",
                "indeterminate_symbol": "−",
                "text_offset": "8",
                "tool_tip_delay": "1.5"
            }
        }
    } 