.. _theme-horizontal-scroll-bar:

UIHorizontalScrollBar Theming Parameters
========================================


The :class:`UIHorizontalScrollBar <pygame_gui.elements.UIHorizontalScrollBar>` theming block id is 'horizontal_scroll_bar'.

Colours
-------

.. figure:: ../_static/vertical_scroll_bar_colour_parameters.png

   A diagram of which part of the element is themed by which colour parameter. The scroll bar's buttons are themed in a
   separate block.

:class:`UIHorizontalScrollBar <pygame_gui.elements.UIHorizontalScrollBar>` makes use of these colour parameters in a 'colours' block. All of these colours can
also be a colour gradient:

 - "**dark_bg**" - The background colour/gradient of the 'back' of the scroll bar, the colour of the track that the scroll bar moves along.
 - "**normal_border**" - The colour/gradient of the border around the scroll bar.
 - "**disabled_dark_bg**" - The colour/gradient of the track when disabled.
 - "**disabled_border**" - The border colour/gradient of the slider when disabled.

Misc
----

:class:`UIHorizontalScrollBar <pygame_gui.elements.UIHorizontalScrollBar>` accepts the following miscellaneous parameters in a 'misc' block:

 - "**shape**" - Can be one of 'rectangle' or 'rounded_rectangle'. Different shapes for this UI element.
 - "**shape_corner_radius**" - Only used if our shape is 'rounded_rectangle'. It sets the radius, or radii, used for the rounded corners. Use a single integer to set all corners to the same radius, or four integers separated by commas to set each corner individually.
 - "**border_width**" - the width in pixels of the border around the bar. Defaults to 1.
 - "**shadow_width**" - the width in pixels of the shadow behind the bar. Defaults to 1.
 - "**enable_arrow_buttons**" - Enables or disables the arrow buttons for the scroll bar. "1" is enabled, "0" is disabled. Defaults to "1".
 - "**tool_tip_delay**" - time in seconds before the button's tool tip (if it has one) will appear. Default is "1.0".

Sub-elements
--------------

You can reference all three of the buttons that are sub elements of the scroll bar with a theming block id of
'horizontal_scroll_bar.button'. You can reference both of the arrow buttons with the class_id: '@arrow_button'.
You can also reference the three buttons individually by adding their object IDs:

 - 'horizontal_scroll_bar.#left_button'
 - 'horizontal_scroll_bar.#right_button'
 - 'horizontal_scroll_bar.#sliding_button'

There is more information on theming buttons at :ref:`theme-button`.

Example
-------

Here is an example of some horizontal scroll bar blocks in a JSON theme file, using the parameters described above (and some from UIButton).

.. code-block:: json
   :caption: horizontal_scroll_bar.json
   :linenos:

    {
        "horizontal_scroll_bar":
        {
            "colours":
            {
                "normal_bg": "#25292e",
                "hovered_bg": "#35393e",
                "disabled_bg": "#25292e",
                "selected_bg": "#25292e",
                "active_bg": "#193784",
                "dark_bg": "#15191e",
                "normal_text": "#c5cbd8",
                "hovered_text": "#FFFFFF",
                "selected_text": "#FFFFFF",
                "disabled_text": "#6d736f"
            },
            "misc":
            {
               "shape": "rectangle",
               "border_width": "0",
               "enable_arrow_buttons": "1"
            }
        },
        "horizontal_scroll_bar.button":
        {
            "misc":
            {
               "border_width": "1"
            }
        },
        "horizontal_scroll_bar.@arrow_button":
        {
            "misc":
            {
               "shadow_width": "0"
            }
        },
        "horizontal_scroll_bar.#sliding_button":
        {
            "colours":
            {
               "normal_bg": "#FF0000"
            }
        }
    }
