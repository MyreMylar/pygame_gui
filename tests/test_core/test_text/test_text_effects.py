import pygame
import pygame.freetype
import pytest

from pygame_gui.core.text import TypingAppearEffect, FadeInEffect, FadeOutEffect
from pygame_gui.core.text import TextLineChunkFTFont
from pygame_gui.core.text.text_effects import BounceEffect, TiltEffect, ExpandContractEffect
from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.elements.ui_label import UILabel
from pygame_gui import TEXT_EFFECT_FADE_OUT, TEXT_EFFECT_FADE_IN, TEXT_EFFECT_TYPING_APPEAR
from pygame_gui import TEXT_EFFECT_BOUNCE, TEXT_EFFECT_TILT, TEXT_EFFECT_EXPAND_CONTRACT
from pygame_gui import UITextEffectType, UI_TEXT_EFFECT_FINISHED


class TestTypingAppearEffect:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('Hello world', pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)
        typing_effect = TypingAppearEffect(text_owner=text_box)

        assert typing_effect.text_owner == text_box

        label = UILabel(pygame.Rect((10, 10), (200, 100)), 'Hello world',
                        default_ui_manager)
        label_typing_effect = TypingAppearEffect(text_owner=label)

        assert label_typing_effect.text_owner == label

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

        label = UILabel(pygame.Rect((10, 10), (200, 100)), 'Hell',
                        default_ui_manager)
        label_typing_effect = TypingAppearEffect(text_owner=label)

        assert label_typing_effect.text_progress == 0

        label.update(time_delta=0.06)
        label.update(time_delta=0.06)
        label.update(time_delta=0.06)
        label.update(time_delta=0.06)
        label.update(time_delta=0.06)
        label.update(time_delta=0.06)
        label.update(time_delta=0.06)
        label.update(time_delta=0.06)

        assert label_typing_effect.text_progress == 0

    def test_has_text_changed(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('hello <font color=#FF0000>this is a</font> test',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)
        typing_effect = TypingAppearEffect(text_owner=text_box)

        assert not typing_effect.has_text_changed()

        typing_effect.update(time_delta=0.06)
        typing_effect.update(time_delta=0.06)

        assert typing_effect.has_text_changed()

        label = UILabel(pygame.Rect((10, 10), (200, 100)), 'Hello world',
                        default_ui_manager)
        label_typing_effect = TypingAppearEffect(text_owner=label)

        assert not label_typing_effect.has_text_changed()

        label_typing_effect.update(time_delta=0.06)
        label_typing_effect.update(time_delta=0.06)

        assert label_typing_effect.has_text_changed()

    def test_set_active_effect_and_params(self, _init_pygame,
                                          default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_TYPING_APPEAR,
                                   params={'time_per_letter': 3.0,
                                           'time_per_letter_deviation': 1.0},
                                   effect_tag='test')

        assert isinstance(text_box.active_text_chunk_effects[0]['effect'],
                          TypingAppearEffect)

        label = UILabel(pygame.Rect((10, 10), (200, 100)), 'Hello world',
                        default_ui_manager)

        label.set_active_effect(TEXT_EFFECT_TYPING_APPEAR,
                                params={'time_per_letter': 3.0,
                                        'time_per_letter_deviation': 1.0})

        label.set_active_effect(None)

        with pytest.warns(UserWarning, match='UILabels do not support effect tags'):
            label.set_active_effect(TEXT_EFFECT_TYPING_APPEAR,
                                    params={'time_per_letter': 3.0,
                                            'time_per_letter_deviation': 1.0},
                                    effect_tag='test')

        with pytest.warns(UserWarning, match='Unsupported effect name'):
            label.set_active_effect(TEXT_EFFECT_BOUNCE)

        with pytest.warns(UserWarning, match='Unsupported effect name'):
            label.set_active_effect("bunce")

    def test_finish_effect(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_TYPING_APPEAR, effect_tag='test')
        effect: TypingAppearEffect = text_box.active_text_chunk_effects[0]['effect']

        assert not effect.has_text_changed()

        effect.update(time_delta=0.06)
        effect.update(time_delta=20.0)
        effect.update(time_delta=0.06)

        for event in pygame.event.get():
            if event.type == UI_TEXT_EFFECT_FINISHED:
                assert event.effect == TEXT_EFFECT_TYPING_APPEAR


class TestFadeInEffect:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('Hello world', pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)
        fade_in_effect = FadeInEffect(text_owner=text_box)

        assert fade_in_effect.text_owner == text_box

        label = UILabel(pygame.Rect((10, 10), (200, 100)), 'Hello world',
                        default_ui_manager)
        label_fade_in_effect = FadeInEffect(text_owner=label)

        assert label_fade_in_effect.text_owner == label

    def test_update(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('hello <font color=#FF0000>this is a</font> test',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        fade_in_effect = FadeInEffect(text_owner=text_box)

        assert fade_in_effect.alpha_value == 0

        fade_in_effect.update(time_delta=0.06)
        fade_in_effect.update(time_delta=0.06)

        assert fade_in_effect.alpha_value == (0.12 / fade_in_effect.time_per_alpha_change)

        label = UILabel(pygame.Rect((10, 10), (200, 100)), 'Hello world',
                        default_ui_manager)
        label_fade_in_effect = FadeInEffect(text_owner=label)

        assert label_fade_in_effect.alpha_value == 0

        label_fade_in_effect.update(time_delta=0.06)
        label_fade_in_effect.update(time_delta=0.06)

        assert label_fade_in_effect.alpha_value == (0.12 / label_fade_in_effect.time_per_alpha_change)

    def test_has_text_changed(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('hello <font color=#FF0000>this is a</font> test',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        fade_in_effect = FadeInEffect(text_owner=text_box)

        assert not fade_in_effect.has_text_changed()

        fade_in_effect.update(time_delta=0.06)
        fade_in_effect.update(time_delta=0.06)

        assert fade_in_effect.has_text_changed()

        label = UILabel(pygame.Rect((10, 10), (200, 100)), 'Hello world',
                        default_ui_manager)
        label_fade_in_effect = FadeInEffect(text_owner=label)

        assert not label_fade_in_effect.has_text_changed()

        label_fade_in_effect.update(time_delta=0.06)
        label_fade_in_effect.update(time_delta=0.06)

        assert label_fade_in_effect.has_text_changed()

    def test_params(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_FADE_IN,
                                   params={'time_per_alpha_change': 19.0},
                                   effect_tag='test')

        assert isinstance(text_box.active_text_chunk_effects[0]['effect'], FadeInEffect)

        label = UILabel(pygame.Rect((10, 10), (200, 100)), 'Hello world',
                        default_ui_manager)

        label.set_active_effect(TEXT_EFFECT_FADE_IN,
                                params={'time_per_alpha_change': 19.0})

    def test_finish_effect(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_FADE_IN, effect_tag='test')
        effect: FadeInEffect = text_box.active_text_chunk_effects[0]['effect']

        assert not effect.has_text_changed()

        effect.update(time_delta=0.06)
        effect.update(time_delta=20.0)
        effect.update(time_delta=0.06)

        for event in pygame.event.get():
            if event.type == UI_TEXT_EFFECT_FINISHED:
                assert event.effect == TEXT_EFFECT_FADE_IN


class TestFadeOutEffect:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('Hello world', pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)
        fade_out_effect = FadeOutEffect(text_owner=text_box)

        assert fade_out_effect.text_owner == text_box

        label = UILabel(pygame.Rect((10, 10), (200, 100)), 'Hello world',
                        default_ui_manager)
        label_fade_out_effect = FadeOutEffect(text_owner=label)

        assert label_fade_out_effect.text_owner == label

    def test_update(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('hello <font color=#FF0000>this is a</font> test',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        fade_out_effect = FadeOutEffect(text_owner=text_box)

        assert fade_out_effect.alpha_value == 255

        fade_out_effect.update(time_delta=0.06)
        fade_out_effect.update(time_delta=0.06)

        assert fade_out_effect.alpha_value == 255 - (0.12 / fade_out_effect.time_per_alpha_change)

        label = UILabel(pygame.Rect((10, 10), (200, 100)), 'Hello world',
                        default_ui_manager)
        label_fade_out_effect = FadeOutEffect(text_owner=label)

        assert label_fade_out_effect.alpha_value == 255

        label_fade_out_effect.update(time_delta=0.06)
        label_fade_out_effect.update(time_delta=0.06)

        assert label_fade_out_effect.alpha_value == 255 - (0.12 / label_fade_out_effect.time_per_alpha_change)

    def test_has_text_block_changed(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('hello <font color=#FF0000>this is a</font> test',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        fade_out_effect = FadeOutEffect(text_owner=text_box)

        assert not fade_out_effect.has_text_changed()

        fade_out_effect.update(time_delta=0.06)
        fade_out_effect.update(time_delta=0.06)

        assert fade_out_effect.has_text_changed()

    def test_params(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_FADE_OUT,
                                   params={'time_per_alpha_change': 19.0},
                                   effect_tag='test')

        assert isinstance(text_box.active_text_chunk_effects[0]['effect'], FadeOutEffect)

        label = UILabel(pygame.Rect((10, 10), (200, 100)), 'Hello world',
                        default_ui_manager)

        label.set_active_effect(TEXT_EFFECT_FADE_OUT,
                                params={'time_per_alpha_change': 19.0})

    def test_finish_effect(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_FADE_OUT, effect_tag='test')
        effect: FadeOutEffect = text_box.active_text_chunk_effects[0]['effect']

        assert not effect.has_text_changed()

        effect.update(time_delta=0.06)
        effect.update(time_delta=20.0)
        effect.update(time_delta=0.06)

        for event in pygame.event.get():
            if event.type == UI_TEXT_EFFECT_FINISHED:
                assert event.effect == TEXT_EFFECT_FADE_OUT


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

    def test_params(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_BOUNCE,
                                   params={'loop': False,
                                           'bounce_max_height': 10,
                                           'time_to_complete_bounce': 19.0},
                                   effect_tag='test')

        assert isinstance(text_box.active_text_chunk_effects[0]['effect'], BounceEffect)

    def test_finish_effect(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_BOUNCE, effect_tag='test',
                                   params={'loop': False})
        effect: BounceEffect = text_box.active_text_chunk_effects[0]['effect']

        assert not effect.has_text_changed()

        effect.update(time_delta=0.06)
        effect.update(time_delta=20.0)
        effect.update(time_delta=0.06)

        for event in pygame.event.get():
            if event.type == UI_TEXT_EFFECT_FINISHED:
                assert event.effect == TEXT_EFFECT_BOUNCE


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

    def test_params(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_TILT,
                                   params={'loop': False,
                                           'max_rotation': 360,
                                           'time_to_complete_rotation': 9.0},
                                   effect_tag='test')

        assert isinstance(text_box.active_text_chunk_effects[0]['effect'], TiltEffect)

    def test_finish_effect(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_TILT, effect_tag='test',
                                   params={'loop': False})
        effect: TiltEffect = text_box.active_text_chunk_effects[0]['effect']

        assert not effect.has_text_changed()

        effect.update(time_delta=0.06)
        effect.update(time_delta=20.0)
        effect.update(time_delta=0.06)

        for event in pygame.event.get():
            if event.type == UI_TEXT_EFFECT_FINISHED:
                assert event.effect == TEXT_EFFECT_TILT


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

    def test_params(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_EXPAND_CONTRACT,
                                   params={'loop': False,
                                           'max_scale': 2.0,
                                           'time_to_complete_expand_contract': 10.0},
                                   effect_tag='test')

        assert isinstance(text_box.active_text_chunk_effects[0]['effect'], ExpandContractEffect)

    def test_finish_effect(self, _init_pygame, default_ui_manager: UIManager):
        text_box = UITextBox('<effect id=test>Hello world</effect>',
                             pygame.Rect((10, 10), (200, 100)),
                             default_ui_manager)

        text_box.set_active_effect(TEXT_EFFECT_EXPAND_CONTRACT, effect_tag='test',
                                   params={'loop': False})
        effect: ExpandContractEffect = text_box.active_text_chunk_effects[0]['effect']

        assert not effect.has_text_changed()

        effect.update(time_delta=0.06)
        effect.update(time_delta=20.0)
        effect.update(time_delta=0.06)

        for event in pygame.event.get():
            if event.type == UI_TEXT_EFFECT_FINISHED:
                assert event.effect == TEXT_EFFECT_EXPAND_CONTRACT


class TestTextEffectType:

    def basic_tests(self, _init_pygame):
        test_effect_type = UITextEffectType('test_effect')

        assert 'this is test_effect' == 'this is ' + test_effect_type

        assert 'test_effect this is' == test_effect_type + ' this is'

        assert 'text_effect' == test_effect_type

        assert 'text_effect' == str(test_effect_type)

        with pytest.raises(AttributeError, match="Can't append to anything other than a string"):
            test_effect_type + 5
        with pytest.raises(AttributeError,
                           match="Can't append to anything other than a string"):
            val = 5 + test_effect_type


if __name__ == '__main__':
    pytest.console_main()
