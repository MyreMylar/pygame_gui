.. _world-space-health-bar:

UIWorldSpaceHealthBar Theming Parameters
=========================================

The :class:`UIWorldSpaceHealthBar <.UIWorldSpaceHealthBar>` theming block id is 'world_space_health_bar'.

Colours
-------

:class:`UIWorldSpaceHealthBar <.UIWorldSpaceHealthBar>` makes use of these colour parameters in a 'colours' block:

 - "**normal_border**" - The colour of the health bar's border if it has one.
 - "**filled_bar**" - The colour of the actual bar itself, of the portion of it that is still full.
 - "**unfilled_bar**" - The colour of an empty portion of the health bar.

Misc
-----

:class:`UIWorldSpaceHealthBar <.UIWorldSpaceHealthBar>` has the following miscellaneous parameters in a 'misc' block:

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
                "border_width": 0
            }
        }
    }
