.. _theme-vertical-scroll-bar:

UIVerticalScrollBar Theming Parameters
=======================================

The UIVerticalScrollBar theming block id is 'vertical_scroll_bar'.

Colours
-------

UIVerticalScrollBar makes use of these colour parameters in a 'colours' block:

 - "**dark_bg**" - The background colour of the 'back' of the scroll bar, the colour of the track that the scroll bar moves along.

Important Note
--------------

While the UIVerticalScrollBar doesn't have many theming parameters all of it's own; because it is composed of multiple UIButton elements, it also inherits the
:ref:`theme-button`. As such, you can include those parameters in your 'vertical_scroll_bar' block as well and they will affect those parts of the
scroll bar which are made of buttons - which is most of it.

Example
-------

Here is an example of a vertical scroll bar block in a JSON theme file, using the parameters described above (and some from UIButton).

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
        }
