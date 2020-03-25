.. _theme-button:

UIButton Theming Parameters
===========================

.. raw:: html

    <video width="140" height="60" nocontrols playsinline autoplay muted loop>
        <source src="../_static/button.mp4" type="video/mp4">
        Your browser does not support the video tag.
    </video>

The :class:`UIButton <pygame_gui.elements.UIButton>` theming block id is 'button'.

Colours
-------

.. figure:: ../_static/button_colour_parameters.png

   A diagram of which part of the element is themed by which colour parameter. This correspondence is the same for the
   parameters named for the different button states e.g. the parameter 'hovered_bg' themes the same area as 'normal_bg'
   when the button is in the hovered state.

:class:`UIButton <pygame_gui.elements.UIButton>` makes use of these colour parameters in a 'colours' block. All of
these colours can also be a colour gradient:

 - "**normal_bg**" - The background colour/gradient of the button in the default state.
 - "**hovered_bg**" - The background colour/gradient of the button when the mouse pointer is over it.
 - "**disabled_bg**" - The background colour/gradient of the button when the button has been disabled (so users cannot interact with it)
 - "**selected_bg**" - The background colour/gradient of the button when the button has select focus.
 - "**active_bg**" - The background colour/gradient of the button 'mid-click', you will mostly see it while dragging things around via buttons.
 - "**normal_text**" - The colour/gradient of the button's text in the default state.
 - "**hovered_text**" - The colour/gradient of the button's text when the mouse pointer is over it.
 - "**disabled_text**" - The colour/gradient of the button's text when the button has been disabled (so users cannot interact with it)
 - "**selected_text**" - The colour/gradient of the button's text when the button has select focus.
 - "**active_text**" - The colour/gradient of the button's text (if any) 'mid-click', you will mostly see it while dragging things around via buttons.
 - "**normal_border**" - The colour/gradient of the border around the button (if it has one), in the default state.
 - "**hovered_border**" - The colour/gradient of the border around the button (if it has one), in the hovered state.
 - "**disabled_border**" - The colour/gradient of the border around the button (if it has one), in the disabled state.
 - "**selected_border**" - The colour/gradient of the border around the button (if it has one), in the selected state.
 - "**active_border**" - The colour/gradient of the border around the button (if it has one), in the active state.

Font
-----

:class:`UIButton <pygame_gui.elements.UIButton>` accepts a font specified in the theme via a 'font' block. A 'font'
block has these parameters:

 - "**name**" - Necessary to make a valid block. This is the name that this font goes by in the UI, if this is a new font then subsequent font instances with different styles or sizes should use the same name.
 - "**size**" - Necessary to make a valid block. This is the point size of the font to use on the button.
 - "**bold**" - Optional parameter. Set it to "1" to make this font bold.
 - "**italic**" - Optional parameter. Set it to "1" to make this font italic.

Only specify paths if this is the first use of this font name in the GUI:

 - "**regular_path**" - The path to this font's file with no particular style applied.
 - "**bold_path**" - The path to this font's file with bold style applied.
 - "**italic_path**" - The path to this font's file with italic style applied.
 - "**bold_italic_path**" - The path to this font's file with bold and italic style applied.

Images
-------

:class:`UIButton <pygame_gui.elements.UIButton>` accepts images specified in the theme via an 'images' block. An
'images' block has these parameters:

 - "**normal_image**" - The image displayed in the buttons default state. It has the following block of sub-parameters:

    - "**path**" - The path to the image to be displayed.
    - "**sub_surface_rect**" - An optional rectangle (described like "x,y,width,height") that will be used to grab a smaller portion of the image specified. This allows us to create many image surfaces from one image file.

 - "**hovered_image**" - The image displayed in the buttons hovered state. It has the following block of sub-parameters:

    - "**path**" - The path to the image to be displayed.
    - "**sub_surface_rect**" - An optional rectangle (described like "x,y,width,height") that will be used to grab a smaller portion of the image specified. This allows us to create many image surfaces from one image file.

 - "**selected_image**" - The image displayed in the buttons select focused state. It has the following block of sub-parameters:

    - "**path**" - The path to the image to be displayed.
    - "**sub_surface_rect**" - An optional rectangle (described like "x,y,width,height") that will be used to grab a smaller portion of the image specified. This allows us to create many image surfaces from one image file.

 - "**disabled_image**" - The image displayed in the buttons disabled state. It has the following block of sub-parameters:

    - "**path**" - The path to the image to be displayed.
    - "**sub_surface_rect**" - An optional rectangle (described like "x,y,width,height") that will be used to grab a smaller portion of the image specified. This allows us to create many image surfaces from one image file.


Misc
----

:class:`UIButton <pygame_gui.elements.UIButton>` accepts the following miscellaneous parameters in a 'misc' block:

 - "**shape**" - Can be one of 'rectangle', 'rounded_rectangle' or 'ellipse'. Different shapes for this UI element.
 - "**shape_corner_radius**" - Only used if our shape is 'rounded_rectangle'. It sets the radius used for the rounded corners.
 - "**border_width**" - the width in pixels of the border around the button. Defaults to 0.
 - "**shadow_width**" - the width in pixels of the shadow behind the button. Defaults to 0.
 - "**tool_tip_delay**" - time in seconds before a the buttons tool sip (if it has one) will appear. Default is "1.0".
 - "**text_horiz_alignment**" - Set to "left", "right" or "center". Controls the horizontal placement of the button text, if this button has any text. Default is "center".
 - "**text_vert_alignment**" - Set to "top", "bottom or "center". Controls the vertical placement of the button text, if this button has any text. Default is "center".
 - "**text_horiz_alignment_padding**" - If horizontal alignment is set to 'left' or 'right' this value will control the buffer between the edge of the button and where we start placing the text. Default is "1".
 - "**text_vert_alignment_padding**" - If vertical alignment is set to 'top' or 'bottom' this value will control the buffer between the edge of the button and where we start placing the text. Default is "1".
 - "**state_transitions**" - A block of parameters that define any fade transitions between button states. Normally buttons states visually change instantly, if you setup values here the button will instead fade from one state to the next. Transition definitions are one way, if you want to go in both directions, use two parameters. Transition parameters have this format:

   - "**startstate_targetstate**" - Can be set to any positive floating point value, representing the transition time in seconds.

Example
-------

Here is an example of a button block in a JSON theme file using all the parameters described above.

.. code-block:: json
   :caption: button.json
   :linenos:

    {
        "button":
        {
            "colours":
            {
                "normal_bg": "#25292e",
                "hovered_bg": "#35393e",
                "disabled_bg": "#25292e",
                "selected_bg": "#25292e",
                "active_bg": "#193784",
                "normal_text": "#c5cbd8",
                "hovered_text": "#FFFFFF",
                "selected_text": "#FFFFFF",
                "disabled_text": "#6d736f",
                "active_text": "#6d736f",
                "normal_border": "#AAAAAA",
                "hovered_border": "#B0B0B0",
                "disabled_border": "#808080",
                "selected_border": "#8080B0",
                "active_border": "#8080B0"
            },
            "font":
            {
                "name": "montserrat",
                "size": "12",
                "bold": "0",
                "italic": "1",
                "regular_path": "data/fonts/Montserrat-Regular.ttf",
                "bold_path": "data/fonts/Montserrat-Bold.ttf",
                "italic_path": "data/fonts/Montserrat-Italic.ttf",
                "bold_italic_path": "data/fonts/Montserrat-BoldItalic.ttf"
            },
            "images":
            {
                "normal_image": {
                    "path": "data/images/buttons.png",
                    "sub_surface_rect": "0,0,32,32"
                },
                "hovered_image": {
                    "path": "data/images/buttons.png",
                    "sub_surface_rect": "32,0,32,32"
                },
                "selected_image": {
                    "path": "data/images/buttons.png",
                    "sub_surface_rect": "64,0,32,32"
                },
                "disabled_image": {
                    "path": "data/images/buttons.png",
                    "sub_surface_rect": "96,0,32,32"
                }

            },
            "misc":
            {
                "border_width": "1",
                "shadow_width": "1",
                "tool_tip_delay": "1.0",
                "text_horiz_alignment": "left",
                "text_vert_alignment": "top",
                "text_horiz_alignment_padding": "10",
                "text_vert_alignment_padding": "5"
                "state_transitions":
                {
                    "normal_hovered": "0.5",
                    "hovered_normal": "0.5
                }
            }
        }
    }
