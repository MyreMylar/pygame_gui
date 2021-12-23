from collections import deque

import pygame
import pygame.freetype
import pytest

from pygame_gui.core.text import TextBoxLayout, TextLineChunkFTFont, TypingAppearEffect, FadeInEffect, FadeOutEffect
from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_text_box import UITextBox


class TestTypingAppearEffect:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('Hello world', pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)
        typing_effect = TypingAppearEffect(text_box=text_box)

        assert typing_effect.text_box == text_box

    def test_update(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('hello <font color=#FF0000>this is a</font> test',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)
        typing_effect = TypingAppearEffect(text_box=text_box)

        assert typing_effect.text_progress == 0

        typing_effect.update(time_delta=0.06)
        typing_effect.update(time_delta=0.06)
        typing_effect.update(time_delta=0.06)
        typing_effect.update(time_delta=0.06)

        assert typing_effect.text_progress == 2

    def test_has_text_block_changed(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('hello <font color=#FF0000>this is a</font> test',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)
        typing_effect = TypingAppearEffect(text_box=text_box)

        assert not typing_effect.has_text_block_changed()

        typing_effect.update(time_delta=0.06)
        typing_effect.update(time_delta=0.06)

        assert typing_effect.has_text_block_changed()


class TestFadeInEffect:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('Hello world', pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)
        fade_in_effect = FadeInEffect(text_box=text_box)

        assert fade_in_effect.text_box == text_box

    def test_update(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('hello <font color=#FF0000>this is a</font> test',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        fade_in_effect = FadeInEffect(text_box=text_box)

        assert fade_in_effect.alpha_value == 0

        fade_in_effect.update(time_delta=0.06)
        fade_in_effect.update(time_delta=0.06)

        assert fade_in_effect.alpha_value == (0.12 / fade_in_effect.time_per_alpha_change)

    def test_has_text_block_changed(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('hello <font color=#FF0000>this is a</font> test',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        fade_in_effect = FadeInEffect(text_box=text_box)

        assert not fade_in_effect.has_text_block_changed()

        fade_in_effect.update(time_delta=0.06)
        fade_in_effect.update(time_delta=0.06)

        assert fade_in_effect.has_text_block_changed()


class TestFadeOutEffect:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('Hello world', pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)
        fade_out_effect = FadeOutEffect(text_box=text_box)

        assert fade_out_effect.text_box == text_box

    def test_update(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('hello <font color=#FF0000>this is a</font> test',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        fade_out_effect = FadeOutEffect(text_box=text_box)

        assert fade_out_effect.alpha_value == 255

        fade_out_effect.update(time_delta=0.06)
        fade_out_effect.update(time_delta=0.06)

        assert fade_out_effect.alpha_value == 255 - (0.12 / fade_out_effect.time_per_alpha_change)

    def test_has_text_block_changed(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('hello <font color=#FF0000>this is a</font> test',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        fade_out_effect = FadeOutEffect(text_box=text_box)

        assert not fade_out_effect.has_text_block_changed()

        fade_out_effect.update(time_delta=0.06)
        fade_out_effect.update(time_delta=0.06)

        assert fade_out_effect.has_text_block_changed()


if __name__ == '__main__':
    pytest.console_main()
