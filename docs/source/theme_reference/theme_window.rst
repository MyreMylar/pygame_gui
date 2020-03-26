.. _theme-window:

UIWindow Theming Parameters
===========================

The :class:`UIWindow <pygame_gui.elements.UIWindow>` theming block id is 'window'.

Colours
-------

.. figure:: ../_static/window_colour_parameters.png

   A diagram of which part of the element is themed by which colour parameter.

:class:`UIWindow <pygame_gui.elements.UIWindow>` makes use of these colour parameters in a 'colours' block. All of these colours can
also be a colour gradient:

 - "**dark_bg**" - The background colour/gradient of the 'back' of the scroll bar, the colour of the track that the scroll bar moves along.
 - "**normal_border**" - The colour/gradient of the border around the scroll bar.

Misc
----

:class:`UIWindow <pygame_gui.elements.UIWindow>` accepts the following miscellaneous parameters in a 'misc' block:

 - "**shape**" - Can be one of 'rectangle' or 'rounded_rectangle'. Different shapes for this UI element.
 - "**shape_corner_radius**" - Only used if our shape is 'rounded_rectangle'. It sets the radius used for the rounded corners. Defaults to "2".
 - "**border_width**" - The width of the border around the element in pixels. Defaults to "1".
 - "**shadow_width**" - The width of the shadow around the element in pixels. Defaults to "2".
 - "**enable_title_bar**" - Controls whether the title bar appears with it's attendant buttons. "1" is enabled and "0" is disabled. Defaults to "1".
 - "**enable_close_button**" - Controls whether the close button appears on the title bar, only has any affect if the title bar exists. "1" is enabled and "0" is disabled. Defaults to "1".
 - "**title_bar_height**" - The height of the title bar in pixels if it exists. Defaults to 28.

Sub-elements
--------------

You can reference all of the buttons that are sub elements of the window with a theming block id of
'window.button'. You can also reference the buttons individually by adding their object IDs:

 - 'window.#title_bar'
 - 'window.#close_button'

There is more information on theming buttons at :ref:`theme-button`.

Example
-------

Here is an example of a window block in a JSON theme file, using the parameters described above.

.. code-block:: json
   :caption: window.json
   :linenos:

   {
      "window":
      {
         "colours":
         {
            "dark_bg":"#21282D",
            "normal_border": "#999999"
         },

         "misc":
         {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "10",
            "border_width": "1",
            "shadow_width": "15",
            "title_bar_height": "20"
         }
      },
      "window.#title_bar":
      {
         "misc":
         {
            "text_horiz_alignment": "center"
         }
      }
   }
