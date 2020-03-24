.. _world-space-health-bar:

UIWorldSpaceHealthBar Theming Parameters
=========================================

The :class:`UIWorldSpaceHealthBar <pygame_gui.elements.UIWorldSpaceHealthBar>` theming block id is 'world_space_health_bar'.

Colours
-------

.. figure:: ../_static/world_space_health_bar_colour_parameters.png

   A diagram of which part of the element is themed by which colour parameter.

:class:`UIWorldSpaceHealthBar <pygame_gui.elements.UIWorldSpaceHealthBar>` makes use of these colour parameters in a 'colours' block:

 - "**normal_border**" - The colour/gradient of the health bar's border if it has one.
 - "**filled_bar**" - The colour/gradient of the actual bar itself, of the portion of it that is still full.
 - "**unfilled_bar**" - The colour/gradient of an empty portion of the health bar.

Misc
-----

:class:`UIWorldSpaceHealthBar <pygame_gui.elements.UIWorldSpaceHealthBar>` has the following miscellaneous parameters in a 'misc' block:

 - "**shape**" - Can be one of 'rectangle' or 'rounded_rectangle'. Different shapes for this UI element.
 - "**shape_corner_radius**" - Only used if our shape is 'rounded_rectangle'. It sets the radius used for the rounded corners.
 - "**hover_height**" - The height in pixels that the health bar will appear over the sprite. Defaults to "10".
 - "**border_width**" - The width of the border around the health bar. Defaults to "1". Can be "0" to remove the border.
 - "**shadow_width**" - The width of the border around the health bar. Defaults to "1". Can be "0" to remove the border.

Example
-------

Here is an example of a world space health bar block in a JSON theme file using the parameters described above.

.. code-block:: json
   :caption: world_space_health_bar.json
   :linenos:

    {
        "world_space_health_bar":
        {
            "colours":
            {
                "border": "#AAAAAA",
                "filled_bar": "#f4251b",
                "unfilled_bar": "#CCCCCC"
            },
            "misc":
            {
                "hover_height": "5",
                "border_width": "0"
            }
        }
    }
