import os
import pytest
import pygame
import pygame_gui

from tests.conftest import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.elements.text.text_effects import TextBoxEffect, TypingAppearEffect, FadeInEffect, FadeOutEffect


class TestTextEffects:
    def test_creation(self, _init_pygame):
        text_effect = TextBoxEffect('test')
        text_effect.update(0.5)
        assert text_effect.get_end_text_pos() == 4
        assert text_effect.get_final_alpha() == 255

    def test_create_typing_effect(self, _init_pygame):
        text_effect = TypingAppearEffect('test')
        assert text_effect.should_full_redraw() is False

    def test_create_fade_in_effect(self, _init_pygame):
        text_effect = FadeInEffect('test')
        assert text_effect.should_redraw_from_chunks() is False

    def test_create_fade_out_effect(self, _init_pygame):
        text_effect = FadeOutEffect('test')
        assert text_effect.should_redraw_from_chunks() is False
