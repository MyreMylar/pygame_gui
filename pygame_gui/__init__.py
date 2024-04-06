"""
Pygame GUI module

Provides bits and bobs of UI to help make more complicated interactions with games built in pygame
easier to accomplish.
"""
from pygame_gui.ui_manager import UIManager
from pygame_gui import core
from pygame_gui import elements
from pygame_gui import windows
from pygame_gui import data
from pygame_gui._constants import UI_BUTTON_PRESSED, UI_BUTTON_DOUBLE_CLICKED, UI_BUTTON_START_PRESS
from pygame_gui._constants import UI_BUTTON_ON_HOVERED, UI_BUTTON_ON_UNHOVERED
from pygame_gui._constants import UI_TEXT_ENTRY_FINISHED, UI_TEXT_ENTRY_CHANGED
from pygame_gui._constants import UI_TEXT_BOX_LINK_CLICKED
from pygame_gui._constants import UI_DROP_DOWN_MENU_CHANGED, UI_HORIZONTAL_SLIDER_MOVED, UI_2D_SLIDER_MOVED
from pygame_gui._constants import UI_SELECTION_LIST_NEW_SELECTION
from pygame_gui._constants import UI_SELECTION_LIST_DROPPED_SELECTION
from pygame_gui._constants import UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION
from pygame_gui._constants import UI_WINDOW_CLOSE, UI_WINDOW_MOVED_TO_FRONT, UI_WINDOW_RESIZED
from pygame_gui._constants import UI_CONFIRMATION_DIALOG_CONFIRMED
from pygame_gui._constants import UI_FILE_DIALOG_PATH_PICKED, UI_COLOUR_PICKER_COLOUR_PICKED
from pygame_gui._constants import UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED
from pygame_gui._constants import UI_CONSOLE_COMMAND_ENTERED, UI_TEXT_EFFECT_FINISHED
from pygame_gui._constants import TEXT_EFFECT_TYPING_APPEAR, TEXT_EFFECT_FADE_IN
from pygame_gui._constants import TEXT_EFFECT_FADE_OUT, TEXT_EFFECT_BOUNCE, TEXT_EFFECT_TILT
from pygame_gui._constants import TEXT_EFFECT_SHAKE
from pygame_gui._constants import TEXT_EFFECT_EXPAND_CONTRACT
from pygame_gui._constants import UITextEffectType
from pygame_gui.core.utility import PackageResource

__all__ = ['UIManager',
           'core',
           'elements',
           'windows',
           'data',
           'PackageResource',
           'UITextEffectType',
           'UI_BUTTON_PRESSED',
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
           'TEXT_EFFECT_BOUNCE',
           'TEXT_EFFECT_TILT',
           'TEXT_EFFECT_EXPAND_CONTRACT',
           'TEXT_EFFECT_SHAKE'
           ]
