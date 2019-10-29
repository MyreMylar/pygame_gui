.. _theme-vertical-scroll-bar:

UIVerticalScrollBar Theming Parameters
=======================================

The :class:`UIVerticalScrollBar <.UIVerticalScrollBar>` theming block id is 'vertical_scroll_bar'.

Colours
-------

:class:`UIVerticalScrollBar <.UIVerticalScrollBar>` makes use of these colour parameters in a 'colours' block:

 - "**dark_bg**" - The background colour of the 'back' of the scroll bar, the colour of the track that the scroll bar moves along.

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
