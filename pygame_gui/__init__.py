"""
Pygame GUI module

Provides bits and bobs of UI to help make more complicated interactions with games built in pygame
easier to accomplish.
"""
from pygame_gui.ui_manager import UIManager
from pygame_gui import core
from pygame_gui import elements
from pygame_gui import windows
from pygame_gui.elements import text
from pygame_gui._constants import UI_BUTTON_PRESSED, UI_BUTTON_DOUBLE_CLICKED, UI_BUTTON_START_PRESS
from pygame_gui._constants import UI_BUTTON_ON_HOVERED, UI_BUTTON_ON_UNHOVERED
from pygame_gui._constants import UI_TEXT_BOX_LINK_CLICKED, UI_TEXT_ENTRY_FINISHED
from pygame_gui._constants import UI_DROP_DOWN_MENU_CHANGED, UI_HORIZONTAL_SLIDER_MOVED
from pygame_gui._constants import UI_SELECTION_LIST_NEW_SELECTION
from pygame_gui._constants import UI_SELECTION_LIST_DROPPED_SELECTION
from pygame_gui._constants import UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION
from pygame_gui._constants import UI_WINDOW_CLOSE, UI_WINDOW_MOVED_TO_FRONT
from pygame_gui._constants import UI_CONFIRMATION_DIALOG_CONFIRMED
from pygame_gui._constants import UI_FILE_DIALOG_PATH_PICKED, UI_COLOUR_PICKER_COLOUR_PICKED
from pygame_gui._constants import UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED
from pygame_gui._constants import TEXT_EFFECT_TYPING_APPEAR, TEXT_EFFECT_FADE_IN
from pygame_gui._constants import TEXT_EFFECT_FADE_OUT

__all__ = ['UIManager',
           'core',
           'elements',
           'windows',
           'text',
           'UI_BUTTON_PRESSED',
           'UI_BUTTON_START_PRESS',
           'UI_BUTTON_ON_HOVERED',
           'UI_BUTTON_ON_UNHOVERED',
           'UI_BUTTON_DOUBLE_CLICKED',
           'UI_TEXT_BOX_LINK_CLICKED',
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
           'TEXT_EFFECT_TYPING_APPEAR',
           'TEXT_EFFECT_FADE_IN',
           'TEXT_EFFECT_FADE_OUT'
           ]
