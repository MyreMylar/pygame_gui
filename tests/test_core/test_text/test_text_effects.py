from collections import deque

import pygame
import pygame.freetype
import pytest

from pygame_gui.core.text import TextBoxLayout, TextLineChunkFTFont, TypingAppearEffect, FadeInEffect, FadeOutEffect
from pygame_gui.ui_manager import UIManager


class TestTypingAppearEffect:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        input_data = deque([])
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=1.0)
        typing_effect = TypingAppearEffect(text_box=text_box_layout)

        assert typing_effect.text_box == text_box_layout

    def test_update(self, _init_pygame, default_ui_manager: UIManager):
        the_font = pygame.freetype.Font(None, 12)
        the_font.origin = True
        the_font.pad = True
        input_data = deque([TextLineChunkFTFont(text='hello ',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text='this is a',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text=' test',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            ])
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=1.0)
        typing_effect = TypingAppearEffect(text_box=text_box_layout)

        assert typing_effect.text_progress == 0

        typing_effect.update(time_delta=0.06)
        typing_effect.update(time_delta=0.06)
        typing_effect.update(time_delta=0.06)
        typing_effect.update(time_delta=0.06)

        assert typing_effect.text_progress == 2

    def test_has_text_block_changed(self, _init_pygame, default_ui_manager: UIManager):
        the_font = pygame.freetype.Font(None, 12)
        the_font.origin = True
        the_font.pad = True
        input_data = deque([TextLineChunkFTFont(text='hello ',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text='this is a',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text=' test',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            ])
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=1.0)
        typing_effect = TypingAppearEffect(text_box=text_box_layout)

        assert not typing_effect.has_text_block_changed()

        typing_effect.update(time_delta=0.06)
        typing_effect.update(time_delta=0.06)

        assert typing_effect.has_text_block_changed()


class TestFadeInEffect:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        input_data = deque([])
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=1.0)
        fade_in_effect = FadeInEffect(text_box=text_box_layout)

        assert fade_in_effect.text_box == text_box_layout

    def test_update(self, _init_pygame, default_ui_manager: UIManager):
        the_font = pygame.freetype.Font(None, 12)
        the_font.origin = True
        the_font.pad = True
        input_data = deque([TextLineChunkFTFont(text='hello ',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text='this is a',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text=' test',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            ])
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=1.0)

        fade_in_effect = FadeInEffect(text_box=text_box_layout)

        assert fade_in_effect.alpha_value == 0

        fade_in_effect.update(time_delta=0.06)
        fade_in_effect.update(time_delta=0.06)

        assert fade_in_effect.alpha_value == (0.12 / fade_in_effect.time_per_alpha_change)

    def test_has_text_block_changed(self, _init_pygame, default_ui_manager: UIManager):
        the_font = pygame.freetype.Font(None, 12)
        the_font.origin = True
        the_font.pad = True
        input_data = deque([TextLineChunkFTFont(text='hello ',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text='this is a',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text=' test',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            ])
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=1.0)

        fade_in_effect = FadeInEffect(text_box=text_box_layout)

        assert not fade_in_effect.has_text_block_changed()

        fade_in_effect.update(time_delta=0.06)
        fade_in_effect.update(time_delta=0.06)

        assert fade_in_effect.has_text_block_changed()


class TestFadeOutEffect:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        input_data = deque([])
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=1.0)
        fade_out_effect = FadeOutEffect(text_box=text_box_layout)

        assert fade_out_effect.text_box == text_box_layout

    def test_update(self, _init_pygame, default_ui_manager: UIManager):
        the_font = pygame.freetype.Font(None, 12)
        the_font.origin = True
        the_font.pad = True
        input_data = deque([TextLineChunkFTFont(text='hello ',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text='this is a',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text=' test',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            ])
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=1.0)

        fade_out_effect = FadeOutEffect(text_box=text_box_layout)

        assert fade_out_effect.alpha_value == 255

        fade_out_effect.update(time_delta=0.06)
        fade_out_effect.update(time_delta=0.06)

        assert fade_out_effect.alpha_value == 255 - (0.12 / fade_out_effect.time_per_alpha_change)

    def test_has_text_block_changed(self, _init_pygame, default_ui_manager: UIManager):
        the_font = pygame.freetype.Font(None, 12)
        the_font.origin = True
        the_font.pad = True
        input_data = deque([TextLineChunkFTFont(text='hello ',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text='this is a',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            TextLineChunkFTFont(text=' test',
                                                font=the_font,
                                                underlined=False,
                                                colour=pygame.Color('#FFFFFF'),
                                                using_default_text_colour=False,
                                                bg_colour=pygame.Color('#FF0000')),
                            ])
        text_box_layout = TextBoxLayout(input_data_queue=input_data,
                                        layout_rect=pygame.Rect(0, 0, 200, 300),
                                        view_rect=pygame.Rect(0, 0, 200, 150),
                                        line_spacing=1.0)

        fade_out_effect = FadeOutEffect(text_box=text_box_layout)

        assert not fade_out_effect.has_text_block_changed()

        fade_out_effect.update(time_delta=0.06)
        fade_out_effect.update(time_delta=0.06)

        assert fade_out_effect.has_text_block_changed()


if __name__ == '__main__':
    pytest.console_main()
