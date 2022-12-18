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

| To add on, you don't only have to use hex values if you prefer, but you also can use the different supported color model syntax. It's all up to preference
| 

.. list-table:: Supported Colour models
    :widths: 10 10 40 40 

    * - Name
      - Accepted Value Types
      - Example
      - Notes
    * - Hex
      - 6 Hexidecimal Digits
      - #A2F3BB
      - Native Pygame Color
    * - Hex (With Alpha)
      - 8 Hexidecimal Digits
      - #A2F3BBFF
      - Native Pygame Color
    * - Shorthand Hex
      - 3 Hexidecimal Digits
      - #FAB
      - Expands doubly (e.g. would be #FFAABB)
    * - Shorthand Hex (With Alpha)
      - 4 Hexidecimal Digits
      - #AF2F
      - Expands doubly (e.g. would be #AAFF22FF)
    * - RGB
      - 3 numbers between 0 and 255
      - rgb(20, 230, 43)
      - Red, Green, Blue
    * - RGBA
      - 4 numbers between 0 and 255
      - rgba(20, 230, 43, 255)
      - Red, Green, Blue, Alpha
    * - HSL
      - Degree, 2 Percentage Values
      - hsl(30deg, 40%, .5)
      - Hue, Saturation, Luminence
    * - HSLA
      - Degree, 3 Percentage Values
      - hsla(10deg, 40%, .5, 0.7)
      - Hue, Saturation, Luminence, Alpha
    * - HSV
      - Degree, 2 Percentage Values
      - hsv(60deg, 40%, 12%)
      - Hue, Saturation, Value
    * - HSVA
      - Degree, 3 Percentage Values
      - hsva(20deg, 40%, .5, 70%)
      - Hue, Saturation, Value, Alpha
    * - CMY
      - 3 percentage values
      - cmy(.3, .5, .7)
      - Cyan, Magneta, Yellow

.. list-table:: Value Types
    :widths: 10 40 20 20 20

    * - Name
      - Description   
      - Examples
      - Invalid Examples
      - Used In
    * - Degree
      - An Integer Value Bounded from 0 to 360
            * Can optionally have the "deg" unit appended to the end
      - 270, 30deg, 45deg 
      - 37.5, 32.8deg, -15deg, -22
      - HSL, HSLA, HSV, HSVA
    * - Percentage
      - Can accept data in two formats:
            * A float value bounded from 0 to 1
            * A percentage value with an integer value bounded from 0 to 100
      - 40%, 0.67, 27%
      - 0.4%, 2, 200%
      - HSL, HSLA, HSV, HSVA, CMY
    * - U8
      - An integer value bounded from 0 to 255
      - 12, 55, 154, 243, 255, 0
      - 12.4, -23, -27.4, 20.0
      - RGB, RGBA



.. note:: **Do I really need to memorize colour values just to get a colour? That's such a hassle**
    
    | We hear you, anything besides simple primary colors and values are pretty difficult to remember
    |
    | For that reason, colour names like "yellow", "purple", "pink",  etc... are supported as well ( Based on the CSS Color values found `here <https://w3schools.sinsixx.com/css/css_colornames.asp.htm>`_ ) 
    | as a little plus, these colour names are not case sensitive, so don't worry about that
    | 
    | If you'd like to easily find a custom colour that is not provided, `colorpicker.me <https://www.colorpicker.me>`_ is a great way to choose a color value to use and paste in your theme file

.. code-block:: json
    :caption: theme.json with different valid colour expressions
    :linenos:

    {
        "defaults":
        {
            "colours":
            {
                "normal_bg": "#f2f",
                "hovered_bg": "#ff7a",
                "disabled_bg": "rgb(200, 150, 60)",
                "selected_bg": "rgba(20, 50, 89, 225)",
                "dark_bg": "hsl(30, 0.6, 0.7)",
                "normal_text": "hsla(3deg, 0.5, 0.7, 90%)",
                "hovered_text": "#FFFFFF",
                "selected_text": "purple",
                "disabled_text": "RGB(40, 70, 90)",
                "link_text": "HSV(50deg, 30%, 40%)",
                "link_hover": "cmy(50%, 30%, 0.7)",
                "link_selected": "teal",
                "text_shadow": "skyblue",
                "normal_border": "gold",
            }
        }
    }



.. note:: Some More Notes About Colours

    - In shorthand hex values like #fff and #ffff, each value represents itself twice. for example: #123 == #112233 and #1234 == #11223344
    - Color Model names are **not** case sensitive, you can write RGB, rGb, or whatever, it will not affect the validity of the color string
    - Hex values are also **not** case sensitive, #FFF and #fff are exactly the same

    


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
