.. _screen-space-health-bar:

UIScreenSpaceHealthBar Theming Parameters
=========================================

The UIScreenSpaceHealthBar theming block id is 'screen_space_health_bar'.

Colours
-------

UIScreenSpaceHealthBar makes use of these colour parameters in a 'colours' block:

 - "**normal_bg**" - The background colour of the health bar.
 - "**normal_text**" - The colour of the health bars's text.
 - "**text_shadow**" - The colour of the shadow behind the text (so it stands out better).
 - "**border**" - The colour of the border around the health bar.
 - "**filled_bar**" - The colour of the actual bar itself, of the portion of it that is still full.
 - "**unfilled_bar**" - The colour of an empty portion of the health bar.

Font
-----

UIScreenSpaceHealthBar accepts a font specified in the theme via a 'font' block. A 'font' block has these parameters:

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
                "normal_bg": "#25292e",
                "normal_text": "#c5cbd8",
                "text_shadow": "#777777",
                "border": "#DDDDDD",
                "filled_bar": "#f4251b",
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
