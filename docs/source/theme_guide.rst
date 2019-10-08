.. _theme-guide:

Theme Guide
===========

Pygame UI Elements can pretty much all be themed in some manner. A theme is created by loading a theme file in JSON
format. To load one, simply pass the path to the theme file into the UIManager when you create it. Like so:

.. code-block:: python
   :linenos:

    manager = pygame_gui.UIManager((800, 600), 'theme.json')


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
                "border": "#DDDDDD",
                "filled_bar":"#f4251b",
                "unfilled_bar":"#CCCCCC"
            }
        }
    }

To add theming for specific UI elements you then need to add additional blocks at the same level as the
'defaults' block. These blocks can either be given an ID representing the type of element, or you can
create a unique 'object' ID block, by convention prefixed with a '#', and then assign this unique ID to
UI elements when you create them.

There are four general categories of theming which each have their own sub-blocks:

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
                "border": "#DDDDDD",
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
                "active_text":"#FFFFFF"
            },

            "misc":
            {
                "tool_tip_delay": "1.5"
            }
        }
    }

Each of the UI Elements supports different theme options, what exactly these are is detailed in the individual
theming guide for each element shown below.

Theme Options Per Element
-------------------------
.. toctree::
    theme_reference/theme_button
    theme_reference/theme_drop_down_menu
    theme_reference/theme_horizontal_slider
    theme_reference/theme_image
    theme_reference/theme_label
    theme_reference/theme_screen_space_health_bar
    theme_reference/theme_text_box
    theme_reference/theme_text_entry_line
    theme_reference/theme_tooltip
    theme_reference/theme_vertical_scroll_bar
    theme_reference/theme_world_space_health_bar
