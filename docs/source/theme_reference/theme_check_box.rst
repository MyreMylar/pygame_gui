.. _theme-check-box:

UICheckBox Theming Parameters
=============================

The :class:`UICheckBox <pygame_gui.elements.UICheckBox>` theming block id is 'check_box'.

Colours
-------

:class:`UICheckBox <pygame_gui.elements.UICheckBox>` accepts the following colour parameters in a 'colours' block:

 - "**normal_bg**" - The background colour of the checkbox in its normal state.
 - "**normal_border**" - The border colour of the checkbox in its normal state.
 - "**hovered_bg**" - The background colour of the checkbox when it is being hovered over.
 - "**hovered_border**" - The border colour of the checkbox when it is being hovered over.
 - "**disabled_bg**" - The background colour of the checkbox when it is disabled.
 - "**disabled_border**" - The border colour of the checkbox when it is disabled.
 - "**selected_bg**" - The background colour of the checkbox when it is checked or indeterminate.
 - "**selected_border**" - The border colour of the checkbox when it is checked or indeterminate.
 - "**normal_text**" - The colour of the check symbol when the checkbox is in its normal state.
 - "**hovered_text**" - The colour of the check symbol when the checkbox is being hovered over.
 - "**disabled_text**" - The colour of the check symbol when the checkbox is disabled.
 - "**selected_text**" - The colour of the check symbol when the checkbox is checked or indeterminate.
 - "**normal_text_shadow**" - The colour of the check symbol's shadow in normal state.
 - "**hovered_text_shadow**" - The colour of the check symbol's shadow when hovered.
 - "**disabled_text_shadow**" - The colour of the check symbol's shadow when disabled.
 - "**selected_text_shadow**" - The colour of the check symbol's shadow when checked or indeterminate.

Font
----

:class:`UICheckBox <pygame_gui.elements.UICheckBox>` accepts the following font parameter in a 'font' block:

 - "**name**" - The name of the font to use for the check symbol. Defaults to the UI theme's default font.
 - "**size**" - The size of the font to use for the check symbol.
 - "**bold**" - Whether the font should be bold.
 - "**italic**" - Whether the font should be italic.

You only need to specify locations if this is the first use of this font name in the GUI.

Images
-------

:class:`UICheckBox <pygame_gui.elements.UICheckBox>` accepts images specified in the theme via an 'images' block. The checkbox supports both single-image and multi-image modes for enhanced visual effects.

**Single Image Mode (Legacy)**

For simple checkboxes with one image per state, use these parameters:

 - "**normal_image**" - The image displayed in the checkbox's default state. It has the following block of sub-parameters:

    - "**path**" - The string path to the image to be displayed. OR
    - "**package** - The name of the python package containing this resource - e.g. 'data.images'
    - "**resource** - The file name of the resource in the python package - e.g. 'splat.png' - Use a 'package' and 'resource' or a 'path' not both.
    - "**sub_surface_rect**" - An optional rectangle (described like "x,y,width,height") that will be used to grab a smaller portion of the image specified. This allows us to create many image surfaces from one image file.
    - "**premultiplied**" - Optional parameter to declare that a loaded image already contains premultiplied alpha and does not need premultiplying. Set to "1" to enable, "0" to disable (default).

 - "**hovered_image**" - The image displayed in the checkbox's hovered state. Uses the same sub-parameters as normal_image.

 - "**selected_image**" - The image displayed in the checkbox's checked/indeterminate state. Uses the same sub-parameters as normal_image.

 - "**disabled_image**" - The image displayed in the checkbox's disabled state. Uses the same sub-parameters as normal_image.

**Multi-Image Mode**

For more complex checkboxes with multiple images per state and precise positioning control, use these parameters:

 - "**normal_images**" - A list of images for the normal state. Each image has the following parameters:

    - "**id**" - A unique identifier for this image.
    - "**path**" - The string path to the image to be displayed. OR
    - "**package**" - The name of the python package containing this resource.
    - "**resource**" - The file name of the resource in the python package.
    - "**layer**" - The layer number for rendering order (lower numbers render first).
    - "**position**" - Optional tuple of (x, y) values between 0.0 and 1.0 representing relative position. Defaults to (0.5, 0.5) for center.
    - "**premultiplied**" - Optional parameter to declare that a loaded image already contains premultiplied alpha.

 - "**hovered_images**" - A list of images for the hovered state. Uses the same parameters as normal_images.
 - "**selected_images**" - A list of images for the checked/indeterminate state. Uses the same parameters as normal_images.
 - "**disabled_images**" - A list of images for the disabled state. Uses the same parameters as normal_images.

**Image Positioning Notes**:
- The "position" parameter accepts values between 0.0 and 1.0 for both x and y coordinates.
- (0.0, 0.0) represents top-left, (1.0, 1.0) represents bottom-right.
- If no position is specified, the image will be centered (0.5, 0.5).
- Images are rendered in layer order (lowest layer number first), allowing precise control over visual composition.
- If a state doesn't specify images, it will fall back to the normal state images.
- Both modes work alongside the traditional text-based check symbols.

Miscellaneous
-------------

:class:`UICheckBox <pygame_gui.elements.UICheckBox>` accepts the following miscellaneous parameters in a 'misc' block:

 - "**shape**" - Can be one of 'rectangle' or 'rounded_rectangle'. Different shapes for this UI element.
 - "**shape_corner_radius**" - Only used if our shape is 'rounded_rectangle'. It sets the radius, or radii, used for the rounded corners. Use a single integer to set all corners to the same radius, or four integers separated by commas to set each corner individually.
 - "**border_width**" - The width in pixels of the border around the checkbox. Defaults to 1.
 - "**shadow_width**" - The width in pixels of the shadow behind the checkbox. Defaults to 2.
 - "**check_symbol**" - The symbol to display when the checkbox is checked. Defaults to "✓".
 - "**indeterminate_symbol**" - The symbol to display when the checkbox is in indeterminate state. Defaults to "−".
 - "**text_offset**" - The distance in pixels between the checkbox and its text label. Defaults to 5.
 - "**tool_tip_delay**" - Time in seconds before the checkbox's tool tip (if it has one) will appear. Default is "1.0".

Sub-elements
------------

The :class:`UICheckBox <pygame_gui.elements.UICheckBox>` contains a :class:`UILabel <pygame_gui.elements.UILabel>` for its text, so you can use the block ID 'check_box.label' to style the text label.

There is more information on theming the label at :ref:`theme-label`.

Example
-------

Here are examples of checkbox blocks in JSON theme files using the parameters described above.

**Single Image Mode Example:**

.. code-block:: json
   :caption: check_box_single_image.json
   :linenos:

    {
        "check_box":
        {
            "colours":
            {
                "normal_bg": "#25292e",
                "normal_border": "#AAAAAA",
                "hovered_bg": "#35393e", 
                "hovered_border": "#B0B0B0",
                "disabled_bg": "#25292e",
                "disabled_border": "#808080",
                "selected_bg": "#193784",
                "selected_border": "#8080B0",
                "normal_text": "#c5cbd8",
                "hovered_text": "#FFFFFF",
                "disabled_text": "#6d736f",
                "selected_text": "#FFFFFF",
                "normal_text_shadow": "#10101070",
                "hovered_text_shadow": "#10101070", 
                "disabled_text_shadow": "#10101070",
                "selected_text_shadow": "#10101070"
            },
            "font":
            {
                "name": "fira_code",
                "size": "14",
                "bold": "0",
                "italic": "0"
            },
            "images":
            {
                "normal_image": {
                    "package": "data.images",
                    "resource": "checkbox_states.png",
                    "sub_surface_rect": "0,0,16,16"
                },
                "hovered_image": {
                    "package": "data.images",
                    "resource": "checkbox_states.png",
                    "sub_surface_rect": "16,0,16,16"
                },
                "selected_image": {
                    "package": "data.images",
                    "resource": "checkbox_states.png",
                    "sub_surface_rect": "32,0,16,16"
                },
                "disabled_image": {
                    "package": "data.images",
                    "resource": "checkbox_states.png",
                    "sub_surface_rect": "48,0,16,16"
                }
            },
            "misc":
            {
                "shape": "rounded_rectangle",
                "shape_corner_radius": "3",
                "border_width": "2",
                "shadow_width": "2",
                "check_symbol": "✓",
                "indeterminate_symbol": "−",
                "text_offset": "8",
                "tool_tip_delay": "1.5"
            }
        }
    }

**Multi-Image Mode Example:**

.. code-block:: json
   :caption: check_box_multi_image.json
   :linenos:

    {
        "check_box":
        {
            "colours":
            {
                "normal_text": "#c5cbd8",
                "hovered_text": "#FFFFFF",
                "disabled_text": "#6d736f",
                "selected_text": "#FFFFFF"
            },
            "font":
            {
                "name": "fira_code",
                "size": "14"
            },
            "images":
            {
                "normal_images": [
                    {
                        "id": "checkbox_base",
                        "path": "images/checkbox_base.png",
                        "layer": 0
                    },
                    {
                        "id": "checkbox_border",
                        "path": "images/checkbox_border.png",
                        "layer": 1
                    }
                ],
                "hovered_images": [
                    {
                        "id": "checkbox_base",
                        "path": "images/checkbox_base.png",
                        "layer": 0
                    },
                    {
                        "id": "checkbox_border",
                        "path": "images/checkbox_border.png",
                        "layer": 1
                    },
                    {
                        "id": "hover_glow",
                        "path": "images/checkbox_glow.png",
                        "layer": 2
                    }
                ],
                "selected_images": [
                    {
                        "id": "checkbox_base_selected",
                        "path": "images/checkbox_base_selected.png",
                        "layer": 0
                    },
                    {
                        "id": "checkbox_border",
                        "path": "images/checkbox_border.png",
                        "layer": 1
                    },
                    {
                        "id": "check_mark",
                        "path": "images/checkbox_check.png",
                        "layer": 2
                    }
                ],
                "disabled_images": [
                    {
                        "id": "checkbox_base_disabled",
                        "path": "images/checkbox_base_disabled.png",
                        "layer": 0
                    }
                ]
            },
            "misc":
            {
                "shape": "rounded_rectangle",
                "shape_corner_radius": "3",
                "border_width": "2",
                "shadow_width": "2",
                "check_symbol": "✓",
                "indeterminate_symbol": "−",
                "text_offset": "8",
                "tool_tip_delay": "1.5"
            }
        }
    } 