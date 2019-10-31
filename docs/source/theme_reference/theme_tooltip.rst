.. _theme-tooltip:

UITooltip Theming Parameters
=============================

The :class:`UIToolTip <.UIToolTip>` theming block id is 'tool_tip'.

Misc
----

:class:`UITooltip <.UITooltip>` accepts the following miscellaneous parameters in a 'misc' block:

 - "**rect_width**" - The width of the rectangle around the tool tip in pixels, including any shadows or borders.
                      The height is determined dynamically.


Sub-elements
--------------

The :class:`UIToolTip <.UIToolTip>` contains a :class:`UITextBox <.UITextBox>` so you can use the block ID 'tool_tip.text_box' to start styling
it.

There is more information on theming the text box at :ref:`theme-text-box`.

Example
-------

Here is an example of a tool tip block in a JSON theme file, using parameters from the text box element.

.. code-block:: json
   :caption: tool_tip.json
   :linenos:

    {
        "tool_tip":
        {
            "misc":
            {
               "rect_width": "170"
            }
        },
        "tool_tip.text_box":
        {
            "colours":
            {
                "dark_bg":"#505050",
                "border": "#FFFFFF"
            },

            "misc":
            {
                "border_width": "2",
                "padding": "5,5"
            }
        }
    }
