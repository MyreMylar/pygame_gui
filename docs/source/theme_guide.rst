.. _theme-guide:

Theme Guide
===========

Pygame UI Elements can pretty much all be themed in some manner. A theme is created by loading a theme file in JSON
format. To load one, simply pass the path to the theme file into the UIManager when you create it. Like so:

.. code-block:: python
   :linenos:

    manager = pygame_gui.UIManager((800, 600), 'theme.json')

You can also theme your elements 'on the fly', while your pygame application is running. Just edit your theme file and
save it, and you should see the UI update to reflect your changes. This is particularly helpful when trying to fiddle
with colours, or visualise what the theming parameters do. You can also turn off live theming if you want to save a few
CPU cycles by setting that option when you create your UI manager.

The most basic theming you can do is to set the default colours for the UI, which are the colours used if no more
element specific colour is specified in the theme.

To set these you need to create a 'defaults' block in your JSON theme file, and a 'colours' sub-block within that. Then
within the colours block you can start to set individual colours by their IDs. It should look something like this:

.. code-block:: json
   :caption: theme.json
   :linenos:

    {
        "defaults":
        {
            "colours":
            {
                "normal_bg":"#45494e",
                "hovered_bg":"#35393e",
                "disabled_bg":"#25292e",
                "selected_bg":"#193754",
                "dark_bg":"#15191e",
                "normal_text":"#c5cbd8",
                "hovered_text":"#FFFFFF",
                "selected_text":"#FFFFFF",
                "disabled_text":"#6d736f",
                "link_text": "#0000EE",
                "link_hover": "#2020FF",
                "link_selected": "#551A8B",
                "text_shadow": "#777777",
                "normal_border": "#DDDDDD",
                "hovered_border": "#B0B0B0",
                "disabled_border": "#808080",
                "selected_border": "#8080B0",
                "active_border": "#8080B0",
                "filled_bar":"#f4251b",
                "unfilled_bar":"#CCCCCC"
            }
        }
    }

To add on, you don't only have to use hex values if you prefer, you can use different color models like rgb, rgba, hsl, cmy, and shorthand hex values. It's all up to preference

.. code-block:: json
    :caption: theme.json
    :linenos:
    {
        "defaults":
        {
            "colours":
            {
                "normal_bg":"#fff", # Shorthand Hex Value 
                "hovered_bg":"#ffff", # Shorthand Hex Value with Alpha
                "disabled_bg":"rgb(200, 150, 60)", #rgb value
                "selected_bg":"rgba(20, 50, 89, 225)", #rgba value
                "dark_bg":"hsl(30, 0.6, 0.7)", #hsl value
                "normal_text":"cmy(0.3, 0.5, 0.7)", #cmy value
                "hovered_text":"#FFFFFF", #capitalization does not matter
                "selected_text":"#ff22ff",
                "disabled_text":"RGB(40, 70, 90)",
                "link_text": "CMY(50%, 30%, 40%)",
                "link_hover": "cmy(50%, 30%, 0.7)",
                "link_selected": "#551A8BFF", # Hex value with alpha channel
                "text_shadow": "#777777",
                "normal_border": "hsl(40deg, 28%, 87%)",
            }
        }
    }



The currently supported color models are as follows
    Hex, RGB, RGBA, HSL, CMY 
.. tip::
    Percentage Values can either be expressed with a decimal number between 0 and 1, or a percentage value between 0 and 100 (e.g. 0.5 or 50% are the same)
    Degree Values can optionally have the "deg" identifier behind them to be more explicit (e.g. 40 and 40deg are the same)

    RGB and RGBA Values are bounded between 0 and 255
    HSL Values require 1 degree value and 2 percentage values, describing Hue, Saturation, and Luminence(Lightness) respectively
    CMY requires 3 percentage values

Of course, colours are not just colours - they can also be gradients, which have a very similar syntax. Like so:

.. code-block:: json
   :caption: theme.json
   :linenos:

   {
        "defaults":
        {
            "colours":
            {
               "normal_bg":"#45494e,#65696e,90",
               "hovered_bg":"rgb(30, 40, 60),#f3f,rgb(50, 60, 70),90deg"
            }
        }
   }

Where the first two (or three) parameters indicate the colours used in the gradient, separated by commas, and the last
parameter indicates the direction of the gradient as an angle in degrees (from 0 to 360).

To add theming for specific UI elements you then need to add additional blocks at the same level as the
'defaults' block. These blocks require an ID that references which elements that they apply to. IDs have a hierarchy
allowing us to reference elements that are part of other elements. To address sub-elements we join them with a full stop
For example, if we wanted to theme the vertical scroll bars that are part of a text box we could use
'text_box.vertical_scroll_bar' as the theme ID.

The parts of a theming block ID can be made up either of their element IDs or an 'ObjectID' which is passed to the
element when it is created. ObjectID objects contain two string IDs - one called 'object_id'  intended for identifying
this specific object and another called 'class_id' for identifying this object as part of a class of objects that share
theming parameters.

As a rule the entries in more specific theming ID blocks are preferred to more general ones. This means entries under
your ObjectID's 'object_id' are preferred over it's 'class_id' and the 'class_id' is preferred over it's 'element_id'.
It also means that if your object is part of a hierarchy, then IDs that specify more of the hierarchy will be preferred
over those that only specify the final part of theme ID.

e.g. for the buttons on a scroll bar:

    - 'vertical_scroll_bar.button' preferred over 'button'
    - 'vertical_scroll_bar.@arrow_button' preferred over 'vertical_scroll_bar.button'
    - 'vertical_scroll_bar.#bottom_button' preferred over 'vertical_scroll_bar.@arrow_button'

Object IDs - in depth
----------------------

By convention pygame_gui starts an 'element_id' with no prefix, a 'class_id' with a prefix of '@' and an 'object_id'
with a prefix of '#'. These are just conventions and not enforced by the code, but I find it helps make it easier to
remember what type of ID each block refers to in larger theme files. Your ids must match between the code and the json
theme file (including any prefixes in both).

To create an ObjectID for one of your elements, you first need to import the ObjectID class from the core submodule,
then you can create on and pass it into your element when you create it. See the example below:

.. code-block:: python
   :caption: object_id.py
   :linenos:

   from pygame_gui.core import ObjectID
   from pygame_gui.elements import UIButton

   ...  # other code ommitted here -
        # see quick start guide for how to get up and running with a single button

   hello_button = UIButton(relative_rect=pygame.Rect((350, 280), (-1, -1)),
                           text='Hello',
                           manager=manager,
                           object_id=ObjectID(class_id='@friendly_buttons',
                                              object_id='#hello_button'))


Once the ObjectID is in place in the code you can refer to it in a block in your loaded theme file, like so:

.. code-block:: json
   :caption: theme.json
   :linenos:

    {
        "button":
        {
            "misc":
            {
                "border_width": "1",
                "shadow_width": "2"
            }
       },
       "@friendly_buttons":
        {
            "misc":
            {
                "shadow_width": "5",
                "shape": "rounded_rectangle"
            }
       },
       "#hello_button":
        {
            "misc":
            {
                "text_horiz_alignment": "left"
            }
       }
   }



Theme block categories
----------------------
There are four general categories of theming which each have their own sub-blocks under the theme block IDs:

    - 'colours'
    - 'font'
    - 'misc'
    - 'images'

Here's an example of adding a 'button' theme block to the JSON file above:

.. code-block:: json
   :caption: theme.json
   :linenos:

    {
        "defaults":
        {
            "colours":
            {
                "normal_bg":"#45494e",
                "hovered_bg":"#35393e",
                "disabled_bg":"#25292e",
                "selected_bg":"#193754",
                "dark_bg":"#15191e",
                "normal_text":"#c5cbd8",
                "hovered_text":"#FFFFFF",
                "selected_text":"#FFFFFF",
                "disabled_text":"#6d736f",
                "link_text": "#0000EE",
                "link_hover": "#2020FF",
                "link_selected": "#551A8B",
                "text_shadow": "#777777",
                "normal_border": "#DDDDDD",
                "hovered_border": "#B0B0B0",
                "disabled_border": "#808080",
                "selected_border": "#8080B0",
                "active_border": "#8080B0",
                "filled_bar":"#f4251b",
                "unfilled_bar":"#CCCCCC"
            }
        },

        "button":
        {
            "colours":
            {
                "normal_bg":"#45494e",
                "hovered_bg":"#35393e",
                "disabled_bg":"#25292e",
                "selected_bg":"#193754",
                "active_bg":"#193754",
                "dark_bg":"#15191e",
                "normal_text":"#c5cbd8",
                "hovered_text":"#FFFFFF",
                "selected_text":"#FFFFFF",
                "disabled_text":"#6d736f",
                "active_text":"#FFFFFF",
                "normal_border": "#DDDDDD",
                "hovered_border": "#B0B0B0",
                "disabled_border": "#808080",
                "selected_border": "#8080B0",
                "active_border": "#8080B0"
            },

            "misc":
            {
                "tool_tip_delay": "1.5"
            }
        }
    }

Each of the UI Elements supports different theme options, what exactly these are is detailed in the individual
theming guide for each element shown below.

Theme Prototypes
----------------

As well as creating theming blocks that address specific elements, or classes of elements, you can also create theming
blocks that don't have an ID that matches any element in your UI.

Why would you do this?

To save yourself a bunch of typing by taking advantage of theme prototypes, that's why! In every element theme block
you create you can also specify a 'prototype' theme block which will be loaded as that block parameters first before
any changes are applied. This lets us quickly apply a bunch of identical theming changes to multiple different parts
of our UI theme.

Prototype theme blocks must be defined higher in the theme file than where they are used, otherwise they won't exist to
be imported.

Here's a quick example:

.. code-block:: json
   :caption: theme.json
   :linenos:

   {
      "#new_shape_style":
      {
         "misc":
         {
            "shape": "rectangle",
            "border_width": "2",
            "shadow_width": "1"
         }
      },

      "button"
      {
         "prototype": "#new_shape_style"
      },

      "horizontal_slider"
      {
         "prototype": "#new_shape_style",
         "misc":
         {
            "enable_arrow_buttons": 0
         }
      }
   }

Multiple Theme Files
--------------------

Because of the way that pygame_gui loads theme files you can load multiple theme
files with different stuff defined in each one into a single UI Manger:

.. code-block:: python
   :linenos:

    manager = pygame_gui.UIManager((800, 600), 'base_theme.json')
    manager.get_theme().load_theme('menu_theme.json')
    manager.get_theme().load_theme('hud_theme.json')

As long as you keep your IDs distinct you can divide your theming up into lots
of different files.

Alternatively, if memory is tight and you are using lots of data in your themes,
you could also use different UI Managers with different loaded themes
for different states of your game.


Theme Options Per Element
-------------------------
.. toctree::
    theme_reference/theme_button
    theme_reference/theme_drop_down_menu
    theme_reference/theme_horizontal_scroll_bar
    theme_reference/theme_horizontal_slider
    theme_reference/theme_image
    theme_reference/theme_label
    theme_reference/theme_panel
    theme_reference/theme_progress_bar
    theme_reference/theme_screen_space_health_bar
    theme_reference/theme_scrolling_container
    theme_reference/theme_selection_list
    theme_reference/theme_status_bar
    theme_reference/theme_text_box
    theme_reference/theme_text_entry_line
    theme_reference/theme_tooltip
    theme_reference/theme_vertical_scroll_bar
    theme_reference/theme_window
    theme_reference/theme_world_space_health_bar

Theme Options Per Window
-------------------------
.. toctree::
    theme_reference/theme_colour_picker_dialog
    theme_reference/theme_confirmation_dialog
    theme_reference/theme_file_dialog
    theme_reference/theme_message_window
