.. _theme-vertical-scroll-bar:

UIVerticalScrollBar Theming Parameters
=======================================

.. raw:: html

    <video width="44" height="240" nocontrols playsinline autoplay muted loop>
        <source src="../_static/vertical_scroll_bar.mp4" type="video/mp4">
        Your browser does not support the video tag.
    </video>

The :class:`UIVerticalScrollBar <pygame_gui.elements.UIVerticalScrollBar>` theming block id is 'vertical_scroll_bar'.

Colours
-------

.. figure:: ../_static/vertical_scroll_bar_colour_parameters.png

   A diagram of which part of the element is themed by which colour parameter. The scroll bar's buttons are themed in a
   separate block.

:class:`UIVerticalScrollBar <pygame_gui.elements.UIVerticalScrollBar>` makes use of these colour parameters in a 'colours' block. All of these colours can
also be a colour gradient:

 - "**dark_bg**" - The background colour/gradient of the 'back' of the scroll bar, the colour of the track that the scroll bar moves along.
 - "**normal_border**" - The colour/gradient of the border around the scroll bar.
 - "**disabled_dark_bg**" - The colour/gradient of the track when disabled.
 - "**disabled_border**" - The border colour/gradient of the slider when disabled.

Misc
----

:class:`UIVerticalScrollBar <pygame_gui.elements.UIVerticalScrollBar>` accepts the following miscellaneous parameters in a 'misc' block:

 - "**shape**" - Can be one of 'rectangle' or 'rounded_rectangle'. Different shapes for this UI element.
 - "**shape_corner_radius**" - Only used if our shape is 'rounded_rectangle'. It sets the radius used for the rounded corners.
 - "**border_width**" - the width in pixels of the border around the bar. Defaults to 1.
 - "**shadow_width**" - the width in pixels of the shadow behind the bar. Defaults to 1.
 - "**enable_arrow_buttons**" - Enables or disables the arrow buttons for the scroll bar. "1" is enabled, "0" is disabled. Defaults to "1".

Sub-elements
--------------

You can reference all three of the buttons that are sub elements of the scroll bar with a theming block id of
'vertical_scroll_bar.button'. You can also reference the three buttons individually by adding their object IDs:

 - 'vertical_scroll_bar.#top_button'
 - 'vertical_scroll_bar.#bottom_button'
 - 'vertical_scroll_bar.#sliding_button'

There is more information on theming buttons at :ref:`theme-button`.

Example
-------

Here is an example of some vertical scroll bar blocks in a JSON theme file, using the parameters described above (and some from UIButton).

.. code-block:: json
   :caption: vertical_scroll_bar.json
   :linenos:

    {
        "vertical_scroll_bar":
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
               "enable_arrow_buttons": "0"
            }
        },
        "vertical_scroll_bar.button":
        {
            "misc":
            {
               "border_width": "1"
            }
        },
        "vertical_scroll_bar.#sliding_button":
        {
            "colours":
            {
               "normal_bg": "#FF0000"
            }
        }
    }
