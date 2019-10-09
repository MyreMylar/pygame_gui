.. _theme-tooltip:

UITooltip Theming Parameters
=============================

The UIToolTip theming block id is 'tool_tip'. But it currently supports no specific theming parameters of it's own.

Important Note
--------------

The UIToolTip contains a UITextBox so the :ref:`theme-text-box` can also be included in your tool_tip block to style it.

Example
-------

Here is an example of a tool tip block in a JSON theme file, using parameters from the text box element.

.. code-block:: json
   :caption: tool_tip.json
   :linenos:

    {
        "tool_tip":
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
