"""
Some  constants used across the GUI
TODO: Using strings for now for compatibility but we could deprecate these to be integers later.
"""

# UI Event types
UI_BUTTON_PRESSED = 'ui_button_pressed'
UI_TEXT_BOX_LINK_CLICKED = 'ui_text_box_link_clicked'
UI_TEXT_ENTRY_FINISHED = 'ui_text_entry_finished'
UI_DROP_DOWN_MENU_CHANGED = 'ui_drop_down_menu_changed'

# Text effects
TEXT_EFFECT_TYPING_APPEAR = 'typing_appear'
TEXT_EFFECT_FADE_IN = 'fade_in'
TEXT_EFFECT_FADE_OUT = 'fade_out'

__all__ = ['UI_BUTTON_PRESSED',
           'UI_TEXT_BOX_LINK_CLICKED',
           'UI_TEXT_ENTRY_FINISHED',
           'UI_DROP_DOWN_MENU_CHANGED',
           'TEXT_EFFECT_TYPING_APPEAR',
           'TEXT_EFFECT_FADE_IN',
           'TEXT_EFFECT_FADE_OUT']