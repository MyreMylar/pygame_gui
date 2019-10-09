.. _theme-label:

UILabel Theming Parameters
==========================

The UILabel theming block id is 'label'.

Colours
-------

UILabel makes use of these colour parameters in a 'colours' block:

 - "**dark_bg**" - The background colour of the label text.
 - "**normal_text**" - The colour of the text itself.

Font
-----

UILabel accepts a font specified in the theme via a 'font' block. A 'font' block has these parameters:

 - "**name**" - Necessary to make a valid block. This is the name that this font goes by in the UI, if this is a new font then subsequent font instances with different styles or sizes should use the same name.
 - "**size**" - Necessary to make a valid block. This is the point size of the font to use on the label.
 - "**bold**" - Optional parameter. Set it to "1" to make this font bold.
 - "**italic**" - Optional parameter. Set it to "1" to make this font italic.

Only specify paths if this is the first use of this font name in the GUI:

 - "**regular_path**" - The path to this font's file with no particular style applied.
 - "**bold_path**" - The path to this font's file with bold style applied.
 - "**italic_path**" - The path to this font's file with italic style applied.
 - "**bold_italic_path**" - The path to this font's file with bold and italic style applied.

Example
-------

Here is an example of a label block in a JSON theme file using the parameters described above.

.. code-block:: json
   :caption: label.json
   :linenos:

    {
        "label":
        {
            "colours":
            {
                "dark_bg": "#25292e",
                "normal_text": "#c5cbd8"
            },
            "font":
            {
                "name": "montserrat",
                "size": "12",
                "bold": "0",
                "italic": "0"
            }
        }
    }
