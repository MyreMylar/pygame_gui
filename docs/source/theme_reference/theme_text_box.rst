.. _theme-text-box:

UITextBox Theming Parameters
============================

The UITextBox theming block id is 'text_box'.

Colours
-------

UITextBox makes use of these colour parameters in a 'colours' block:

 - "**dark_bg**" -  The background colour of the text box element.
 - "**border**" - The colour of the border around the text box element.
 - "**link_text**" - The default colour of any links in the text.
 - "**link_hover**" - The colour of link text when we hover over it with the mouse.
 - "**link_selected**" - The colour of link text when they are clicked on with the mouse.

Misc
----

UITextBox accepts the following miscellaneous parameters in a 'misc' block:

- "**border_width**" -  the width of the border around the element in pixels. Defaults to "1".
- "**padding**" - the horizontal and vertical 'padding' between the border and where we render the text. Defaults to "4,2".
- "**link_normal_underline**" - Set to either "1" or "0". Whether link text is normally underlined. Defaults to "0" (False).
- "**link_hover_underline**" - Set to either "1" or "0". Whether link text is underlined when they are hovered over with the mouse. Defaults to "1" (True).

Important Note
--------------

The UITextBox sometimes also contains a UIVerticalSlider, if the text to show is longer than the rectangle to display
it, in this case the :ref:`theme-vertical-scroll-bar` can also be included in you text_box block to style it.

Example
-------

Here is an example of a text box block in a JSON theme file, using the parameters described above.

.. code-block:: json
   :caption: text_box.json
   :linenos:

    {
        "text_box":
        {
            "colours":
            {
                "dark_bg":"#21282D",
                "border": "#999999",
                "link_text": "#FF0000",
                "link_hover": "#FFFF00",
                "link_selected": "#FFFFFF"
            },

            "misc":
            {
                "border_width": "1",
                "padding": "10,10",
                "link_normal_underline": "0",
                "link_hover_underline": "1"
            }
        }
    }