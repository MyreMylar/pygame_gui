.. _screen-space-health-bar:

UIScreenSpaceHealthBar Theming Parameters
=========================================

.. raw:: html

    <video width="240" height="44" nocontrols playsinline autoplay muted loop>
        <source src="../_static/screen_space_health_bar.mp4" type="video/mp4">
        Your browser does not support the video tag.
    </video>

The :class:`UIScreenSpaceHealthBar <pygame_gui.elements.UIScreenSpaceHealthBar>` theming block id is 'screen_space_health_bar'.

Colours
-------

.. figure:: ../_static/screen_space_health_bar_colour_parameters.png

   A diagram of which part of the element is themed by which colour parameter. The text shadow **cannot** be themed
   with a colour gradient.

:class:`UIScreenSpaceHealthBar <pygame_gui.elements.UIScreenSpaceHealthBar>` makes use of these colour parameters in a 'colours' block. Most of these colours can
also be a colour gradient:

 - "**normal_text**" - The colour/gradient of the health bars's text.
 - "**text_shadow**" - The colour of the shadow behind the text (so it stands out better).
 - "**normal_border**" - The colour/gradient of the border around the health bar.
 - "**filled_bar**" - The colour/gradient of the actual bar itself, of the portion of it that is still full.
 - "**unfilled_bar**" - The colour/gradient of an empty portion of the health bar.

Misc
----

:class:`UIScreenSpaceHealthBar <pygame_gui.elements.UIScreenSpaceHealthBar>` accepts the following miscellaneous parameters in a 'misc' block:

 - "**shape**" - Can be one of 'rectangle' or 'rounded_rectangle'. Different shapes for this UI element.
 - "**shape_corner_radius**" - Only used if our shape is 'rounded_rectangle'. It sets the radius used for the rounded corners.
 - "**border_width**" - the width in pixels of the border around the bar. Defaults to 1.
 - "**shadow_width**" - the width in pixels of the shadow behind the bar. Defaults to 1.


Font
-----

:class:`UIScreenSpaceHealthBar <pygame_gui.elements.UIScreenSpaceHealthBar>` accepts a font specified in the theme via a 'font' block. A 'font' block has these parameters:

 - "**name**" - Necessary to make a valid block. This is the name that this font goes by in the UI, if this is a new font then subsequent font instances with different styles or sizes should use the same name.
 - "**size**" - Necessary to make a valid block. This is the point size of the font to use on the health bar.
 - "**bold**" - Optional parameter. Set it to "1" to make this font bold.
 - "**italic**" - Optional parameter. Set it to "1" to make this font italic.

Only specify paths if this is the first use of this font name in the GUI:

 - "**regular_path**" - The path to this font's file with no particular style applied.
 - "**bold_path**" - The path to this font's file with bold style applied.
 - "**italic_path**" - The path to this font's file with italic style applied.
 - "**bold_italic_path**" - The path to this font's file with bold and italic style applied.

Example
-------

Here is an example of a screen space health bar block in a JSON theme file using the parameters described above.

.. code-block:: json
   :caption: screen_space_health_bar.json
   :linenos:

    {
        "label":
        {
            "colours":
            {
                "normal_text": "#c5cbd8",
                "text_shadow": "#777777",
                "border": "#DDDDDD",
                "filled_bar": "#f4251b,#A4150b,180",
                "unfilled_bar": "#CCCCCC"
            },
            "font":
            {
                "name": "montserrat",
                "size": "12",
                "bold": "0",
                "italic": "1"
            }
        }
    }
