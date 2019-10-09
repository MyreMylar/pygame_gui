.. _theme-drop-down-menu:

UIDropDownMenu Theming Parameters
=================================

The UIDropDownMenu theming block id is 'drop_down_menu'.

Misc
----

UIDropDownMenu accepts the following miscellaneous parameters in a 'misc' block:

 - "**expand_direction**" - Can be set to **'up'** or **'down'**. Defaults to 'down'. Changing this parameter will change the direction that the menu will expand away from the initial starting point.

Important Note
--------------

While the UIDropDownMenu doesn't have many theming parameters all of it's own; because it is composed of multiple UIButton elements, it also inherits the
:ref:`theme-button`. As such, you can include those parameters in your 'drop_down_menu' block as well and they will affect those parts of the
drop down which are made of buttons - which is basically all of it.

Example
-------

Here is an example of a drop down menu block in a JSON theme file, using the parameters described above (and a couple from UIButton).

.. code-block:: json
   :caption: drop_down_menu.json
   :linenos:

    {
        "drop_down_menu":
        {
            "misc":
            {
                "expand_direction": "down"
            },

            "colours":
            {
                "normal_bg": "#25292e",
                "hovered_bg": "#35393e"
            }
        }
    }
