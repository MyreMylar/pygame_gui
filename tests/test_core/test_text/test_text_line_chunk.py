import pygame
import pygame.freetype
import pytest

from pygame_gui.core.colour_gradient import ColourGradient
from pygame_gui.core.text import TextLineChunkFTFont
from pygame_gui.ui_manager import UIManager


class TestTextLineChunkFTFont:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):

        the_font = pygame.freetype.Font(None, 30)
        the_font.origin = True
        the_font.pad = True

        chunk = TextLineChunkFTFont(text='test',
                                    font=the_font,
                                    underlined=False,
                                    colour=pygame.Color('#FFFFFF'),
                                    using_default_text_colour=False,
                                    bg_colour=pygame.Color('#00000000'))

        assert chunk.text == 'test'

    def test_style_match(self, _init_pygame, default_ui_manager: UIManager):

        the_font = pygame.freetype.Font(None, 30)
        the_font.origin = True
        the_font.pad = True

        the_second_font = pygame.freetype.Font(None, 14)
        the_second_font.origin = True
        the_second_font.pad = True

        chunk_1 = TextLineChunkFTFont(text='test',
                                      font=the_font,
                                      underlined=False,
                                      colour=pygame.Color('#FFFFFF'),
                                      using_default_text_colour=False,
                                      bg_colour=pygame.Color('#00000000'))

        # only text differs so the styles should match
        chunk_2 = TextLineChunkFTFont(text='a match',
                                      font=the_font,
                                      underlined=False,
                                      colour=pygame.Color('#FFFFFF'),
                                      using_default_text_colour=False,
                                      bg_colour=pygame.Color('#00000000'))

        assert chunk_1.style_match(chunk_2)

        # no underline so should be no style match
        chunk_3 = TextLineChunkFTFont(text='not a match',
                                      font=the_font,
                                      underlined=True,
                                      colour=pygame.Color('#FFFFFF'),
                                      using_default_text_colour=False,
                                      bg_colour=pygame.Color('#00000000'))

        assert not chunk_1.style_match(chunk_3)

        # different font so should be no style match
        chunk_4 = TextLineChunkFTFont(text='not a match',
                                      font=the_second_font,
                                      underlined=False,
                                      colour=pygame.Color('#FFFFFF'),
                                      using_default_text_colour=False,
                                      bg_colour=pygame.Color('#00000000'))

        assert not chunk_1.style_match(chunk_4)

        # different font colour so should be no style match
        chunk_5 = TextLineChunkFTFont(text='not a match',
                                      font=the_font,
                                      underlined=False,
                                      colour=pygame.Color('#FF8080'),
                                      using_default_text_colour=False,
                                      bg_colour=pygame.Color('#00000000'))

        assert not chunk_1.style_match(chunk_5)

        # different background colour so should be no style match
        chunk_6 = TextLineChunkFTFont(text='not a match',
                                      font=the_font,
                                      underlined=False,
                                      colour=pygame.Color('#FFFFFF'),
                                      using_default_text_colour=False,
                                      bg_colour=pygame.Color('#5050F0'))

        assert not chunk_1.style_match(chunk_6)

    def test_finalise(self, _init_pygame, default_ui_manager: UIManager):
        the_font = pygame.freetype.Font(None, 30)
        the_font.origin = True
        the_font.pad = True

        chunk_1 = TextLineChunkFTFont(text='test',
                                      font=the_font,
                                      underlined=False,
                                      colour=pygame.Color('#FFFFFF'),
                                      using_default_text_colour=False,
                                      bg_colour=pygame.Color('#FF0000'))

        layout_surface = pygame.Surface((200, 300), depth=32, flags=pygame.SRCALPHA)
        layout_surface.fill((0, 0, 0, 0))
        chunk_1.finalise(layout_surface,
                         pygame.Rect(0, 0, 200, 300),
                         chunk_1.y_origin,
                         chunk_1.height,
                         chunk_1.height)

        assert layout_surface.get_at((10, 10)) == pygame.Color('#FF0000')

        chunk_2 = TextLineChunkFTFont(text='test',
                                      font=the_font,
                                      underlined=False,
                                      colour=ColourGradient(0,
                                                            pygame.Color('#FFFF00'),
                                                            pygame.Color('#FF0000')),
                                      using_default_text_colour=False,
                                      bg_colour=pygame.Color('#FF0000'))

        layout_surface_2 = pygame.Surface((200, 300), depth=32, flags=pygame.SRCALPHA)
        layout_surface_2.fill((0, 0, 0, 0))
        chunk_2.finalise(layout_surface_2,
                         pygame.Rect(0, 0, 200, 300),
                         chunk_2.y_origin,
                         chunk_2.height,
                         chunk_2.height)

        assert layout_surface_2.get_at((10, 10)) == pygame.Color('#FF0000')

        chunk_3 = TextLineChunkFTFont(text='test',
                                      font=the_font,
                                      underlined=False,
                                      colour=ColourGradient(0,
                                                            pygame.Color('#FFFF00'),
                                                            pygame.Color('#FF0000')),
                                      using_default_text_colour=False,
                                      bg_colour=ColourGradient(0,
                                                               pygame.Color('#FFFF00'),
                                                               pygame.Color('#FF0000')))

        layout_surface_3 = pygame.Surface((200, 300), depth=32, flags=pygame.SRCALPHA)
        layout_surface_3.fill((0, 0, 0, 0))
        chunk_3.finalise(layout_surface_3,
                         pygame.Rect(0, 0, 200, 300),
                         chunk_3.y_origin,
                         chunk_3.height,
                         chunk_3.height)

        assert layout_surface_3.get_at((10, 10)) != pygame.Color('#00000000')

        chunk_4 = TextLineChunkFTFont(text='test',
                                      font=the_font,
                                      underlined=False,
                                      colour=pygame.Color('#FFFFFF'),
                                      using_default_text_colour=False,
                                      bg_colour=ColourGradient(0,
                                                               pygame.Color('#FFFF00'),
                                                               pygame.Color('#FF0000')))

        layout_surface_4 = pygame.Surface((200, 300), depth=32, flags=pygame.SRCALPHA)
        layout_surface_4.fill((0, 0, 0, 0))
        chunk_4.finalise(layout_surface_4,
                         pygame.Rect(0, 0, 200, 300),
                         chunk_4.y_origin,
                         chunk_4.height,
                         chunk_4.height)

        assert layout_surface_4.get_at((10, 10)) != pygame.Color('#00000000')

    def test_split(self, _init_pygame, default_ui_manager: UIManager):

        the_font = pygame.freetype.Font(None, 30)
        the_font.origin = True
        the_font.pad = True

        chunk = TextLineChunkFTFont(text='test this',
                                    font=the_font,
                                    underlined=False,
                                    colour=pygame.Color('#FFFFFF'),
                                    using_default_text_colour=False,
                                    bg_colour=pygame.Color('#00000000'))

        with pytest.raises(ValueError, match='Line width is too narrow'):
            chunk.split(requested_x=0, line_width=0, row_start_x=0)

        assert len(chunk.split_points) == 1
        assert chunk.split_points[0] == 5
        original_chunk_width = chunk.width

        new_chunk = chunk.split(requested_x=70, line_width=200, row_start_x=0)

        assert chunk.width == 62
        assert new_chunk.width == 53
        assert original_chunk_width == (chunk.width + new_chunk.width)
        assert chunk.height == new_chunk.height

    def test_split_index(self, _init_pygame, default_ui_manager: UIManager):

        the_font = pygame.freetype.Font(None, 30)
        the_font.origin = True
        the_font.pad = True

        chunk = TextLineChunkFTFont(text='test this',
                                    font=the_font,
                                    underlined=False,
                                    colour=pygame.Color('#FFFFFF'),
                                    using_default_text_colour=False,
                                    bg_colour=pygame.Color('#00000000'))

        with pytest.raises(ValueError, match='Line width is too narrow'):
            chunk.split(requested_x=0, line_width=0, row_start_x=0)

        assert len(chunk.split_points) == 1
        assert chunk.split_points[0] == 5
        original_chunk_width = chunk.width

        new_chunk = chunk.split_index(index=5)

        assert chunk.width == 62
        assert new_chunk.width == 53
        assert original_chunk_width == (chunk.width + new_chunk.width)
        assert chunk.height == new_chunk.height

        assert chunk.split_index(index=-1) is None

    def test_clear(self, _init_pygame, default_ui_manager: UIManager):

        the_font = pygame.freetype.Font(None, 30)
        the_font.origin = True
        the_font.pad = True

        chunk = TextLineChunkFTFont(text='test this',
                                    font=the_font,
                                    underlined=False,
                                    colour=pygame.Color('#FFFFFF'),
                                    using_default_text_colour=False,
                                    bg_colour=pygame.Color('#FF00FF'))

        layout_surface = pygame.Surface((200, 300), depth=32, flags=pygame.SRCALPHA)
        layout_surface.fill((0, 0, 0, 0))
        chunk.finalise(layout_surface,
                       pygame.Rect(0, 0, 200, 300),
                       chunk.y_origin,
                       chunk.height,
                       chunk.height)

        assert layout_surface.get_at((10, 10)) == pygame.Color('#FF00FF')

        chunk.clear()

        assert layout_surface.get_at((10, 10)) == pygame.Color('#00000000')

    def test_add_text(self, _init_pygame, default_ui_manager: UIManager):

        the_font = pygame.freetype.Font(None, 30)
        the_font.origin = True
        the_font.pad = True

        chunk = TextLineChunkFTFont(text='test this',
                                    font=the_font,
                                    underlined=False,
                                    colour=pygame.Color('#FFFFFF'),
                                    using_default_text_colour=False,
                                    bg_colour=pygame.Color('#FF00FF'))

        assert chunk.text == 'test this'

        chunk.add_text(' for great justice')

        assert chunk.text == 'test this for great justice'

    def test_insert_text(self, _init_pygame, default_ui_manager: UIManager):

        the_font = pygame.freetype.Font(None, 30)
        the_font.origin = True
        the_font.pad = True

        chunk = TextLineChunkFTFont(text='test this',
                                    font=the_font,
                                    underlined=False,
                                    colour=pygame.Color('#FFFFFF'),
                                    using_default_text_colour=False,
                                    bg_colour=pygame.Color('#FF00FF'))

        assert chunk.text == 'test this'

        chunk.insert_text(input_text=' inserting all of', index=4)

        assert chunk.text == 'test inserting all of this'

        chunk = TextLineChunkFTFont(text='',
                                    font=the_font,
                                    underlined=False,
                                    colour=pygame.Color('#FFFFFF'),
                                    using_default_text_colour=False,
                                    bg_colour=pygame.Color('#FF00FF'))

        assert chunk.text == ''
        chunk.insert_text(input_text='start from no text', index=0)

        assert chunk.text == 'start from no text'

        chunk = TextLineChunkFTFont(text='hello',
                                    font=the_font,
                                    underlined=False,
                                    colour=pygame.Color('#FFFFFF'),
                                    using_default_text_colour=False,
                                    bg_colour=pygame.Color('#FF00FF'),
                                    max_dimensions=(50, 30))

        chunk.insert_text(input_text=' world', index=5)
        assert chunk.text == 'hello world'

    def test_delete_letter_at_index(self, _init_pygame, default_ui_manager: UIManager):

        the_font = pygame.freetype.Font(None, 30)
        the_font.origin = True
        the_font.pad = True

        chunk = TextLineChunkFTFont(text='test this',
                                    font=the_font,
                                    underlined=False,
                                    colour=pygame.Color('#FFFFFF'),
                                    using_default_text_colour=False,
                                    bg_colour=pygame.Color('#FF00FF'))

        assert chunk.text == 'test this'

        chunk.delete_letter_at_index(index=7)

        assert chunk.text == 'test ths'

        chunk.delete_letter_at_index(index=7)

        assert chunk.text == 'test th'

        chunk.delete_letter_at_index(index=7)

        assert chunk.text == 'test th'

        chunk.delete_letter_at_index(index=100)

        assert chunk.text == 'test th'

        chunk.delete_letter_at_index(index=0)

        assert chunk.text == 'est th'

        chunk.delete_letter_at_index(index=0)

        assert chunk.text == 'st th'

        chunk.delete_letter_at_index(index=0)
        chunk.delete_letter_at_index(index=0)
        chunk.delete_letter_at_index(index=0)
        chunk.delete_letter_at_index(index=0)

        assert chunk.text == 'h'

        chunk.delete_letter_at_index(index=0)
        chunk.delete_letter_at_index(index=0)

        text_rect = the_font.get_rect('A')
        text_width = sum([char_metric[4] for char_metric in the_font.get_metrics('')])
        text_height = text_rect.height

        assert chunk.text == ''
        assert chunk.size == (text_width, text_height)

        chunk = TextLineChunkFTFont(text='hello',
                                    font=the_font,
                                    underlined=False,
                                    colour=pygame.Color('#FFFFFF'),
                                    using_default_text_colour=False,
                                    bg_colour=pygame.Color('#FF00FF'),
                                    max_dimensions=(50, 30))
        chunk.delete_letter_at_index(index=0)

    def test_backspace_letter_at_index(self, _init_pygame, default_ui_manager: UIManager):

        the_font = pygame.freetype.Font(None, 30)
        the_font.origin = True
        the_font.pad = True

        chunk = TextLineChunkFTFont(text='test this',
                                    font=the_font,
                                    underlined=False,
                                    colour=pygame.Color('#FFFFFF'),
                                    using_default_text_colour=False,
                                    bg_colour=pygame.Color('#FF00FF'))

        assert chunk.text == 'test this'

        chunk.backspace_letter_at_index(index=7)

        assert chunk.text == 'test tis'

        chunk.backspace_letter_at_index(index=7)

        assert chunk.text == 'test ts'

        chunk.backspace_letter_at_index(index=7)

        assert chunk.text == 'test t'

        chunk.backspace_letter_at_index(index=100)

        assert chunk.text == 'test t'

        chunk.backspace_letter_at_index(index=0)

        assert chunk.text == 'test t'

        chunk.backspace_letter_at_index(index=0)

        assert chunk.text == 'test t'

        chunk.backspace_letter_at_index(index=0)
        chunk.backspace_letter_at_index(index=0)
        chunk.backspace_letter_at_index(index=0)
        chunk.backspace_letter_at_index(index=0)

        assert chunk.text == 'test t'

        chunk.backspace_letter_at_index(index=6)
        chunk.backspace_letter_at_index(index=5)
        chunk.backspace_letter_at_index(index=4)
        chunk.backspace_letter_at_index(index=3)
        chunk.backspace_letter_at_index(index=2)
        chunk.backspace_letter_at_index(index=1)

        text_rect = the_font.get_rect('A')
        text_width = sum([char_metric[4] for char_metric in the_font.get_metrics('')])
        text_height = text_rect.height

        assert chunk.text == ''
        assert chunk.size == (text_width, text_height)

        chunk = TextLineChunkFTFont(text='hello',
                                    font=the_font,
                                    underlined=False,
                                    colour=pygame.Color('#FFFFFF'),
                                    using_default_text_colour=False,
                                    bg_colour=pygame.Color('#FF00FF'),
                                    max_dimensions=(50, 30))
        chunk.backspace_letter_at_index(index=1)

    def test_x_pos_to_letter_index(self):
        the_font = pygame.freetype.Font(None, 30)
        the_font.origin = True
        the_font.pad = True

        chunk = TextLineChunkFTFont(text='test this',
                                    font=the_font,
                                    underlined=False,
                                    colour=pygame.Color('#FFFFFF'),
                                    using_default_text_colour=False,
                                    bg_colour=pygame.Color('#FF00FF'))

        letter_index = chunk.x_pos_to_letter_index(x_pos=62)
        assert letter_index == 5

        letter_index = chunk.x_pos_to_letter_index(x_pos=37)
        assert letter_index == 3

        letter_index = chunk.x_pos_to_letter_index(x_pos=0)
        assert letter_index == 0

        letter_index = chunk.x_pos_to_letter_index(x_pos=100)
        assert letter_index == 8

    def test_redraw(self, _init_pygame, default_ui_manager: UIManager):

        the_font = pygame.freetype.Font(None, 30)
        the_font.origin = True
        the_font.pad = True

        chunk = TextLineChunkFTFont(text='test this',
                                    font=the_font,
                                    underlined=False,
                                    colour=pygame.Color('#FFFFFF'),
                                    using_default_text_colour=False,
                                    bg_colour=pygame.Color('#FF00FF'))

        layout_surface = pygame.Surface((200, 300), depth=32, flags=pygame.SRCALPHA)
        layout_surface.fill((0, 0, 0, 0))
        chunk.finalise(layout_surface,
                       pygame.Rect(0, 0, 200, 300),
                       chunk.y_origin,
                       chunk.height,
                       chunk.height)

        assert layout_surface.get_at((10, 10)) == pygame.Color('#FF00FF')

        chunk.clear()

        assert layout_surface.get_at((10, 10)) == pygame.Color('#00000000')

        chunk.redraw()

        assert layout_surface.get_at((10, 10)) == pygame.Color('#FF00FF')

    def test_set_alpha(self, _init_pygame, default_ui_manager: UIManager):
        the_font = pygame.freetype.Font(None, 30)
        the_font.origin = True
        the_font.pad = True
        chunk = TextLineChunkFTFont(text='test this',
                                    font=the_font,
                                    underlined=False,
                                    colour=pygame.Color('#FFFFFF'),
                                    using_default_text_colour=False,
                                    bg_colour=pygame.Color('#FF00FF'))
        layout_surface = pygame.Surface((200, 300), depth=32, flags=pygame.SRCALPHA)
        layout_surface.fill((0, 0, 0, 0))
        chunk.finalise(layout_surface,
                       pygame.Rect(0, 0, 200, 300),
                       chunk.y_origin,
                       chunk.height,
                       chunk.height)

        chunk.grab_pre_effect_surface()
        chunk.set_alpha(128)
        chunk.set_alpha(50)
        chunk.set_alpha(255)
        chunk.grab_pre_effect_surface()
        chunk.set_alpha(0)

        assert chunk.alpha == 0

    def test_set_offset_position(self, _init_pygame, default_ui_manager: UIManager):
        the_font = pygame.freetype.Font(None, 30)
        the_font.origin = True
        the_font.pad = True
        chunk = TextLineChunkFTFont(text='test this',
                                    font=the_font,
                                    underlined=False,
                                    colour=pygame.Color('#FFFFFF'),
                                    using_default_text_colour=False,
                                    bg_colour=pygame.Color('#FF00FF'))
        layout_surface = pygame.Surface((200, 300), depth=32, flags=pygame.SRCALPHA)
        layout_surface.fill((0, 0, 0, 0))
        chunk.finalise(layout_surface,
                       pygame.Rect(0, 0, 200, 300),
                       chunk.y_origin,
                       chunk.height,
                       chunk.height)
        chunk.grab_pre_effect_surface()
        chunk.set_offset_pos((10, 10))

        chunk.set_offset_pos((0, 0))

        assert chunk.effects_offset_pos == (0, 0)

    def test_set_scale(self, _init_pygame, default_ui_manager: UIManager):
        the_font = pygame.freetype.Font(None, 30)
        the_font.origin = True
        the_font.pad = True
        chunk = TextLineChunkFTFont(text='test this',
                                    font=the_font,
                                    underlined=False,
                                    colour=pygame.Color('#FFFFFF'),
                                    using_default_text_colour=False,
                                    bg_colour=pygame.Color('#FF00FF'))
        layout_surface = pygame.Surface((200, 300), depth=32, flags=pygame.SRCALPHA)
        layout_surface.fill((0, 0, 0, 0))
        chunk.finalise(layout_surface,
                       pygame.Rect(0, 0, 200, 300),
                       chunk.y_origin,
                       chunk.height,
                       chunk.height)
        chunk.grab_pre_effect_surface()
        chunk.set_scale(2.0)
        chunk.set_scale(1.0)

        assert chunk.effects_scale == 1.0

    def test_set_rotation(self, _init_pygame, default_ui_manager: UIManager):
        the_font = pygame.freetype.Font(None, 30)
        the_font.origin = True
        the_font.pad = True
        chunk = TextLineChunkFTFont(text='test this',
                                    font=the_font,
                                    underlined=False,
                                    colour=pygame.Color('#FFFFFF'),
                                    using_default_text_colour=False,
                                    bg_colour=pygame.Color('#FF00FF'))
        layout_surface = pygame.Surface((200, 300), depth=32, flags=pygame.SRCALPHA)
        layout_surface.fill((0, 0, 0, 0))
        chunk.finalise(layout_surface,
                       pygame.Rect(0, 0, 200, 300),
                       chunk.y_origin,
                       chunk.height,
                       chunk.height)
        chunk.grab_pre_effect_surface()
        chunk.set_rotation(45)
        chunk.set_rotation(180)
        chunk.set_rotation(0)

        assert chunk.effects_rotation == 0


if __name__ == '__main__':
    pytest.console_main()
