.. _world-space-health-bar:

UIWorldSpaceHealthBar Theming Parameters
=========================================

The UIWorldSpaceHealthBar theming block id is 'world_space_health_bar'.

Colours
-------

UIWorldSpaceHealthBar makes use of these colour parameters in a 'colours' block:

 - "**normal_bg**" - The background colour of the health bar.
 - "**filled_bar**" - The colour of the actual bar itself, of the portion of it that is still full.
 - "**unfilled_bar**" - The colour of an empty portion of the health bar.


Example
-------

Here is an example of a world space health bar block in a JSON theme file using the parameters described above.

.. code-block:: json
   :caption: world_space_health_bar.json
   :linenos:

    {
        "label":
        {
            "colours":
            {
                "normal_bg": "#25292e",
                "filled_bar": "#f4251b",
                "unfilled_bar": "#CCCCCC"
            }
        }
    }
