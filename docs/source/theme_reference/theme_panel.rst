.. _theme-panel:

UIPanel Theming Parameters
==========================

The :class:`UIPanel <pygame_gui.elements.UIPanel>` theming block id is 'panel'.

Colours
-------

.. figure:: ../_static/panel_colour_parameters.png

   A diagram of which part of the element is themed by which colour parameter.

:class:`UIPanel <pygame_gui.elements.UIPanel>` makes use of the following these colour parameters in a 'colours' block.
All of these colours can also be a colour gradient:

 - "**dark_bg**" -  The background colour/gradient of the panel element.
 - "**normal_border**" - The colour/gradient of the border around the panel (if it has one).

Images
-------

:class:`UIPanel <pygame_gui.elements.UIPanel>` accepts an image specified in the theme via an 'images' block. An
'images' block can have these parameters:

 - "**background_image**" - The image displayed on the panel. It has the following block of sub-parameters:

    - "**path**" - The path to the image to be displayed.
    - "**sub_surface_rect**" - An optional rectangle (described like "x,y,width,height") that will be used to grab a smaller portion of the image specified. This allows us to create many image surfaces from one image file.

Misc
----

:class:`UIPanel <pygame_gui.elements.UIPanel>` accepts the following miscellaneous parameters in a 'misc' block:

 - "**shape**" - Can be one of 'rectangle' or 'rounded_rectangle'. Different shapes for this UI element.
 - "**shape_corner_radius**" - Only used if our shape is 'rounded_rectangle'. It sets the radius used for the rounded corners. Defaults to "2".
 - "**border_width**" - The width of the border around the element in pixels. Defaults to "1".
 - "**shadow_width**" - The width of the shadow around the element in pixels. Defaults to "2".


Example
-------

Here is an example of a panel block in a JSON theme file, using the parameters described above.

.. code-block:: json
   :caption: panel.json
   :linenos:

    {
        "panel":
        {
            "colours":
            {
                "dark_bg":"#21282D",
                "border": "#999999"
            },

            "background_image":
            {
                "path": "data/images/splat.png",
                "sub_surface_rect": "0,0,32,32"
            },

            "misc":
            {
                "shape": "rounded_rectangle",
                "shape_corner_radius": "10",
                "border_width": "1",
                "shadow_width": "15"
            }
        }
    }
