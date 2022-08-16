"""
Some  constants used across the GUI
TODO: Using strings for now for compatibility but we could deprecate these to be integers later.
"""
from warnings import warn
from pygame.event import custom_type


class UITextEffectType:
    """
    A Type for Text effect constants so we can mess with them later if needs be
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
UI_SELECTION_LIST_NEW_SELECTION = custom_type()
UI_SELECTION_LIST_DROPPED_SELECTION = custom_type()
UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION = custom_type()
UI_WINDOW_CLOSE = custom_type()
UI_WINDOW_MOVED_TO_FRONT = custom_type()
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
           'UI_SELECTION_LIST_NEW_SELECTION',
           'UI_SELECTION_LIST_DROPPED_SELECTION',
           'UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION',
           'UI_WINDOW_CLOSE',
           'UI_WINDOW_MOVED_TO_FRONT',
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
           'OldType'
           ]
