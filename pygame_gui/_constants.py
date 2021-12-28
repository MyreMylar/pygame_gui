"""
Some  constants used across the GUI
TODO: Using strings for now for compatibility but we could deprecate these to be integers later.
"""
from warnings import warn
from pygame.event import custom_type

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
TEXT_EFFECT_TYPING_APPEAR = 'typing_appear'
TEXT_EFFECT_FADE_IN = 'fade_in'
TEXT_EFFECT_FADE_OUT = 'fade_out'


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
           'OldType']
