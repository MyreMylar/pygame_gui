"""
Some  constants used across the GUI
TODO: Using strings for now for compatibility but we could deprecate these to be integers later.
"""
from warnings import warn
from pygame.event import custom_type


class UITextEffectType:
    """
    A Type for Text effect constants, so we can mess with them later if needs be
    """
    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return self._name

    def __eq__(self, other):
        if isinstance(other, UITextEffectType):
            return self._name == other._name
        elif isinstance(other, str):
            return self._name == other
        return False

    def __add__(self, other):
        if isinstance(other, str):
            return self._name + other
        raise AttributeError("Can't append to anything other than a string")

    def __radd__(self, other):
        if isinstance(other, str):
            return other + self._name
        raise AttributeError("Can't append to anything other than a string")


class OldType(int):
    """
    Deprecation class for Old style user events. Can be removed in 0.8.0 along with
    all the old events.
    """
    def __new__(cls, x,  *args, **kwargs):
        instance = int.__new__(cls, x, *args, **kwargs)
        return instance

    def __eq__(self, other):
        warn("Pygame GUI event types can now "
             "be used directly as event.type "
             "rather than event.user_type. This old style user_type event will "
             "go away in version 0.8.0", DeprecationWarning, stacklevel=2)
        return int.__eq__(self, other)


# UI Event types
UI_BUTTON_PRESSED = custom_type()
UI_BUTTON_START_PRESS = custom_type()
UI_BUTTON_DOUBLE_CLICKED = custom_type()
UI_BUTTON_ON_HOVERED = custom_type()
UI_BUTTON_ON_UNHOVERED = custom_type()
UI_TEXT_BOX_LINK_CLICKED = custom_type()
UI_TEXT_ENTRY_CHANGED = custom_type()
UI_TEXT_ENTRY_FINISHED = custom_type()
UI_DROP_DOWN_MENU_CHANGED = custom_type()
UI_HORIZONTAL_SLIDER_MOVED = custom_type()
UI_2D_SLIDER_MOVED = custom_type()
UI_SELECTION_LIST_NEW_SELECTION = custom_type()
UI_SELECTION_LIST_DROPPED_SELECTION = custom_type()
UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION = custom_type()
UI_FORM_SUBMITTED = custom_type()
UI_WINDOW_CLOSE = custom_type()
UI_WINDOW_MOVED_TO_FRONT = custom_type()
UI_WINDOW_RESIZED = custom_type()
UI_CONFIRMATION_DIALOG_CONFIRMED = custom_type()
UI_FILE_DIALOG_PATH_PICKED = custom_type()
UI_COLOUR_PICKER_COLOUR_PICKED = custom_type()
UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED = custom_type()
UI_CONSOLE_COMMAND_ENTERED = custom_type()
UI_TEXT_EFFECT_FINISHED = custom_type()

# Text effects
TEXT_EFFECT_TYPING_APPEAR = UITextEffectType('typing_appear')
TEXT_EFFECT_FADE_IN = UITextEffectType('fade_in')
TEXT_EFFECT_FADE_OUT = UITextEffectType('fade_out')
TEXT_EFFECT_TILT = UITextEffectType('tilt')
TEXT_EFFECT_BOUNCE = UITextEffectType('bounce')
TEXT_EFFECT_EXPAND_CONTRACT = UITextEffectType('expand_contract')
TEXT_EFFECT_SHAKE = UITextEffectType('shake')

_namedColours = {
  "aliceblue": "#f0f8ff",
  "antiquewhite": "#faebd7",
  "aqua": "#00ffff",
  "aquamarine": "#7fffd4",
  "azure": "#f0ffff",
  "beige": "#f5f5dc",
  "bisque": "#ffe4c4",
  "black": "#000000",
  "blanchedalmond": "#ffebcd",
  "blue": "#0000ff",
  "blueviolet": "#8a2be2",
  "brown": "#a52a2a",
  "burlywood": "#deb887",
  "cadetblue": "#5f9ea0",
  "chartreuse": "#7fff00",
  "chocolate": "#d2691e",
  "coral": "#ff7f50",
  "cornflowerblue": "#6495ed",
  "cornsilk": "#fff8dc",
  "crimson": "#dc143c",
  "cyan": "#00ffff",
  "darkblue": "#00008b",
  "darkcyan": "#008b8b",
  "darkgoldenrod": "#b8860b",
  "darkgray": "#a9a9a9",
  "darkgreen": "#006400",
  "darkgrey": "#a9a9a9",
  "darkkhaki": "#bdb76b",
  "darkmagenta": "#8b008b",
  "darkolivegreen": "#556b2f",
  "darkorange": "#ff8c00",
  "darkorchid": "#9932cc",
  "darkred": "#8b0000",
  "darksalmon": "#e9967a",
  "darkseagreen": "#8fbc8f",
  "darkslateblue": "#483d8b",
  "darkslategray": "#2f4f4f",
  "darkslategrey": "#2f4f4f",
  "darkturquoise": "#00ced1",
  "darkviolet": "#9400d3",
  "deeppink": "#ff1493",
  "deepskyblue": "#00bfff",
  "dimgray": "#696969",
  "dimgrey": "#696969",
  "dodgerblue": "#1e90ff",
  "firebrick": "#b22222",
  "floralwhite": "#fffaf0",
  "forestgreen": "#228b22",
  "fuchsia": "#ff00ff",
  "gainsboro": "#dcdcdc",
  "ghostwhite": "#f8f8ff",
  "goldenrod": "#daa520",
  "gold": "#ffd700",
  "gray": "#808080",
  "green": "#008000",
  "greenyellow": "#adff2f",
  "grey": "#808080",
  "honeydew": "#f0fff0",
  "hotpink": "#ff69b4",
  "indianred": "#cd5c5c",
  "indigo": "#4b0082",
  "ivory": "#fffff0",
  "khaki": "#f0e68c",
  "lavenderblush": "#fff0f5",
  "lavender": "#e6e6fa",
  "lawngreen": "#7cfc00",
  "lemonchiffon": "#fffacd",
  "lightblue": "#add8e6",
  "lightcoral": "#f08080",
  "lightcyan": "#e0ffff",
  "lightgoldenrodyellow": "#fafad2",
  "lightgray": "#d3d3d3",
  "lightgreen": "#90ee90",
  "lightgrey": "#d3d3d3",
  "lightpink": "#ffb6c1",
  "lightsalmon": "#ffa07a",
  "lightseagreen": "#20b2aa",
  "lightskyblue": "#87cefa",
  "lightslategray": "#778899",
  "lightslategrey": "#778899",
  "lightsteelblue": "#b0c4de",
  "lightyellow": "#ffffe0",
  "lime": "#00ff00",
  "limegreen": "#32cd32",
  "linen": "#faf0e6",
  "magenta": "#ff00ff",
  "maroon": "#800000",
  "mediumaquamarine": "#66cdaa",
  "mediumblue": "#0000cd",
  "mediumorchid": "#ba55d3",
  "mediumpurple": "#9370db",
  "mediumseagreen": "#3cb371",
  "mediumslateblue": "#7b68ee",
  "mediumspringgreen": "#00fa9a",
  "mediumturquoise": "#48d1cc",
  "mediumvioletred": "#c71585",
  "midnightblue": "#191970",
  "mintcream": "#f5fffa",
  "mistyrose": "#ffe4e1",
  "moccasin": "#ffe4b5",
  "navajowhite": "#ffdead",
  "navy": "#000080",
  "oldlace": "#fdf5e6",
  "olive": "#808000",
  "olivedrab": "#6b8e23",
  "orange": "#ffa500",
  "orangered": "#ff4500",
  "orchid": "#da70d6",
  "palegoldenrod": "#eee8aa",
  "palegreen": "#98fb98",
  "paleturquoise": "#afeeee",
  "palevioletred": "#db7093",
  "papayawhip": "#ffefd5",
  "peachpuff": "#ffdab9",
  "peru": "#cd853f",
  "pink": "#ffc0cb",
  "plum": "#dda0dd",
  "powderblue": "#b0e0e6",
  "purple": "#800080",
  "rebeccapurple": "#663399",
  "red": "#ff0000",
  "rosybrown": "#bc8f8f",
  "royalblue": "#4169e1",
  "saddlebrown": "#8b4513",
  "salmon": "#fa8072",
  "sandybrown": "#f4a460",
  "seagreen": "#2e8b57",
  "seashell": "#fff5ee",
  "sienna": "#a0522d",
  "silver": "#c0c0c0",
  "skyblue": "#87ceeb",
  "slateblue": "#6a5acd",
  "slategray": "#708090",
  "slategrey": "#708090",
  "snow": "#fffafa",
  "springgreen": "#00ff7f",
  "steelblue": "#4682b4",
  "tan": "#d2b48c",
  "teal": "#008080",
  "thistle": "#d8bfd8",
  "tomato": "#ff6347",
  "turquoise": "#40e0d0",
  "violet": "#ee82ee",
  "wheat": "#f5deb3",
  "white": "#ffffff",
  "whitesmoke": "#f5f5f5",
  "yellow": "#ffff00",
  "yellowgreen": "#9acd32"
}

__all__ = ['UI_BUTTON_PRESSED',
           'UI_BUTTON_START_PRESS',
           'UI_BUTTON_DOUBLE_CLICKED',
           'UI_BUTTON_ON_HOVERED',
           'UI_BUTTON_ON_UNHOVERED',
           'UI_TEXT_BOX_LINK_CLICKED',
           'UI_TEXT_ENTRY_CHANGED',
           'UI_TEXT_ENTRY_FINISHED',
           'UI_DROP_DOWN_MENU_CHANGED',
           'UI_HORIZONTAL_SLIDER_MOVED',
           'UI_2D_SLIDER_MOVED',
           'UI_SELECTION_LIST_NEW_SELECTION',
           'UI_SELECTION_LIST_DROPPED_SELECTION',
           'UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION',
           'UI_FORM_SUBMITTED',
           'UI_WINDOW_CLOSE',
           'UI_WINDOW_MOVED_TO_FRONT',
           "UI_WINDOW_RESIZED",
           'UI_CONFIRMATION_DIALOG_CONFIRMED',
           'UI_FILE_DIALOG_PATH_PICKED',
           'UI_COLOUR_PICKER_COLOUR_PICKED',
           'UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED',
           'UI_CONSOLE_COMMAND_ENTERED',
           'UI_TEXT_EFFECT_FINISHED',
           'TEXT_EFFECT_TYPING_APPEAR',
           'TEXT_EFFECT_FADE_IN',
           'TEXT_EFFECT_FADE_OUT',
           'TEXT_EFFECT_TILT',
           'TEXT_EFFECT_BOUNCE',
           'TEXT_EFFECT_EXPAND_CONTRACT',
           'TEXT_EFFECT_SHAKE',
           'UITextEffectType',
           'OldType',
           '_namedColours'
           ]
