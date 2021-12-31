from collections import deque

import pygame
import pygame.freetype
import pytest

from pygame_gui.core.text import TypingAppearEffect, FadeInEffect, FadeOutEffect
from pygame_gui.core.text import TextLineChunkFTFont
from pygame_gui.core.text.text_effects import BounceEffect, TiltEffect, ExpandContractEffect
from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui import TEXT_EFFECT_BOUNCE, TEXT_EFFECT_TILT, TEXT_EFFECT_EXPAND_CONTRACT


class TestTypingAppearEffect:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('Hello world', pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)
        typing_effect = TypingAppearEffect(text_owner=text_box)

        assert typing_effect.text_owner == text_box

    def test_update(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('hello <font color=#FF0000>this is a</font> test',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)
        typing_effect = TypingAppearEffect(text_owner=text_box)

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
        typing_effect = TypingAppearEffect(text_owner=text_box)

        assert not typing_effect.has_text_changed()

        typing_effect.update(time_delta=0.06)
        typing_effect.update(time_delta=0.06)

        assert typing_effect.has_text_changed()


class TestFadeInEffect:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('Hello world', pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)
        fade_in_effect = FadeInEffect(text_box=text_box)

        assert fade_in_effect.text_owner == text_box

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

        assert not fade_in_effect.has_text_changed()

        fade_in_effect.update(time_delta=0.06)
        fade_in_effect.update(time_delta=0.06)

        assert fade_in_effect.has_text_changed()


class TestFadeOutEffect:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('Hello world', pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)
        fade_out_effect = FadeOutEffect(text_owner=text_box)

        assert fade_out_effect.text_owner == text_box

    def test_update(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('hello <font color=#FF0000>this is a</font> test',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        fade_out_effect = FadeOutEffect(text_owner=text_box)

        assert fade_out_effect.alpha_value == 255

        fade_out_effect.update(time_delta=0.06)
        fade_out_effect.update(time_delta=0.06)

        assert fade_out_effect.alpha_value == 255 - (0.12 / fade_out_effect.time_per_alpha_change)

    def test_has_text_block_changed(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('hello <font color=#FF0000>this is a</font> test',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        fade_out_effect = FadeOutEffect(text_owner=text_box)

        assert not fade_out_effect.has_text_changed()

        fade_out_effect.update(time_delta=0.06)
        fade_out_effect.update(time_delta=0.06)

        assert fade_out_effect.has_text_changed()


class TestBounceEffect:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_BOUNCE, effect_tag='test')

        assert isinstance(text_box.active_text_chunk_effects[0]['effect'], BounceEffect)

    def test_update(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_BOUNCE, effect_tag='test')

        effect = text_box.active_text_chunk_effects[0]['effect']

        assert effect.bounce_height == 0

        effect.update(time_delta=0.06)
        effect.update(time_delta=0.06)

        assert effect.bounce_height != 0

    def test_has_text_changed(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_BOUNCE, effect_tag='test')
        effect: BounceEffect = text_box.active_text_chunk_effects[0]['effect']

        assert not effect.has_text_changed()

        effect.update(time_delta=0.06)
        effect.update(time_delta=0.06)

        assert effect.has_text_changed()

    def test_apply_effect(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_BOUNCE, effect_tag='test')
        effect = text_box.active_text_chunk_effects[0]['effect']
        chunk = text_box.active_text_chunk_effects[0]['chunk']

        assert chunk.effects_offset_pos == (0, 0)

        effect.update(time_delta=0.06)
        effect.update(time_delta=0.06)
        effect.apply_effect()

        assert chunk.effects_offset_pos != (0, 0)


class TestTiltEffect:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_TILT, effect_tag='test')

        assert isinstance(text_box.active_text_chunk_effects[0]['effect'], TiltEffect)

    def test_update(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_TILT, effect_tag='test')

        effect: TiltEffect = text_box.active_text_chunk_effects[0]['effect']

        assert effect.current_rotation == 0

        effect.update(time_delta=0.06)
        effect.update(time_delta=0.06)

        assert effect.current_rotation != 0

    def test_has_text_changed(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_TILT, effect_tag='test')
        effect: TiltEffect = text_box.active_text_chunk_effects[0]['effect']

        assert not effect.has_text_changed()

        effect.update(time_delta=0.06)
        effect.update(time_delta=0.06)

        assert effect.has_text_changed()

    def test_apply_effect(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_TILT, effect_tag='test')
        effect: TiltEffect = text_box.active_text_chunk_effects[0]['effect']
        chunk: TextLineChunkFTFont = text_box.active_text_chunk_effects[0]['chunk']

        assert chunk.effects_rotation == 0

        effect.update(time_delta=0.06)
        effect.update(time_delta=0.06)
        effect.apply_effect()

        assert chunk.effects_rotation != 0


class TestExpandContractEffect:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_EXPAND_CONTRACT, effect_tag='test')

        assert isinstance(text_box.active_text_chunk_effects[0]['effect'], ExpandContractEffect)

    def test_update(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_EXPAND_CONTRACT, effect_tag='test')

        effect: ExpandContractEffect = text_box.active_text_chunk_effects[0]['effect']

        assert effect.current_scale == 1.0

        effect.update(time_delta=0.06)
        effect.update(time_delta=0.06)

        assert effect.current_scale != 1.0

    def test_has_text_changed(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_EXPAND_CONTRACT, effect_tag='test')
        effect: ExpandContractEffect = text_box.active_text_chunk_effects[0]['effect']

        assert not effect.has_text_changed()

        effect.update(time_delta=0.06)
        effect.update(time_delta=0.06)

        assert effect.has_text_changed()

    def test_apply_effect(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_EXPAND_CONTRACT, effect_tag='test')
        effect: ExpandContractEffect = text_box.active_text_chunk_effects[0]['effect']
        chunk: TextLineChunkFTFont = text_box.active_text_chunk_effects[0]['chunk']

        assert chunk.effects_scale == 1.0

        effect.update(time_delta=0.06)
        effect.update(time_delta=0.06)
        effect.apply_effect()

        assert chunk.effects_scale != 1.0


if __name__ == '__main__':
    pytest.console_main()
