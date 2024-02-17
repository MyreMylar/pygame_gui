import pytest
import pygame

from pygame_gui.core.drawable_shapes.rect_drawable_shape import RectDrawableShape
from pygame_gui.ui_manager import UIManager


class TestRectDrawableShape:
    def test_creation(self, _init_pygame, _display_surface_return_none,
                      default_ui_manager: UIManager):
        RectDrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                          theming_parameters={'text': 'test',
                                              'font': default_ui_manager.get_theme().get_font([]),
                                              'normal_text': pygame.Color('#FFFFFF'),
                                              'normal_text_shadow': pygame.Color('#000000'),
                                              'shadow_width': 0,
                                              'border_width': 0,
                                              'normal_border': pygame.Color('#FFFFFF'),
                                              'normal_bg': pygame.Color('#000000'),
                                              'text_horiz_alignment': 'center',
                                              'text_vert_alignment': 'center'},
                          states=['normal'], manager=default_ui_manager)

    def test_full_rebuild_on_size_change_negative_values(self, _init_pygame, _display_surface_return_none,
                                                         default_ui_manager: UIManager):
        shape = RectDrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                                  theming_parameters={'text': 'test',
                                                      'font': default_ui_manager.get_theme().get_font([]),
                                                      'normal_text': pygame.Color('#FFFFFF'),
                                                      'normal_text_shadow': pygame.Color('#000000'),
                                                      'shadow_width': -10,
                                                      'border_width': -10,
                                                      'normal_border': pygame.Color('#FFFFFF'),
                                                      'normal_bg': pygame.Color('#000000'),
                                                      'text_horiz_alignment': 'center',
                                                      'text_vert_alignment': 'center'},
                                  states=['normal'], manager=default_ui_manager)
        shape.full_rebuild_on_size_change()

    def test_full_rebuild_on_size_change_large(self, _init_pygame, _display_surface_return_none,
                                               default_ui_manager: UIManager):
        shape = RectDrawableShape(containing_rect=pygame.Rect(0, 0, 25, 25),
                                  theming_parameters={'text': 'test',
                                                      'font': default_ui_manager.get_theme().get_font([]),
                                                      'normal_text': pygame.Color('#FFFFFF'),
                                                      'normal_text_shadow': pygame.Color('#000000'),
                                                      'shadow_width': 20,
                                                      'border_width': 20,
                                                      'normal_border': pygame.Color('#FFFFFF'),
                                                      'normal_bg': pygame.Color('#000000'),
                                                      'text_horiz_alignment': 'center',
                                                      'text_vert_alignment': 'center'},
                                  states=['normal'], manager=default_ui_manager)
        shape.full_rebuild_on_size_change()

    def test_full_rebuild_on_size_change_large_shadow(self, _init_pygame, _display_surface_return_none,
                                                      default_ui_manager: UIManager):
        shape = RectDrawableShape(containing_rect=pygame.Rect(0, 0, 2, 2),
                                  theming_parameters={'text': 'test',
                                                      'font': default_ui_manager.get_theme().get_font([]),
                                                      'normal_text': pygame.Color('#FFFFFF'),
                                                      'normal_text_shadow': pygame.Color('#000000'),
                                                      'shadow_width': 1,
                                                      'border_width': 0,
                                                      'normal_border': pygame.Color('#FFFFFF'),
                                                      'normal_bg': pygame.Color('#000000'),
                                                      'text_horiz_alignment': 'center',
                                                      'text_vert_alignment': 'center'},
                                  states=['normal'], manager=default_ui_manager)
        shape.full_rebuild_on_size_change()

    def test_collide_point(self, _init_pygame, _display_surface_return_none,
                           default_ui_manager: UIManager):
        shape = RectDrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                                  theming_parameters={'text': 'test',
                                                      'font': default_ui_manager.get_theme().get_font([]),
                                                      'normal_text': pygame.Color('#FFFFFF'),
                                                      'normal_text_shadow': pygame.Color('#000000'),
                                                      'shadow_width': 0,
                                                      'border_width': 0,
                                                      'normal_border': pygame.Color('#FFFFFF'),
                                                      'normal_bg': pygame.Color('#000000'),
                                                      'text_horiz_alignment': 'center',
                                                      'text_vert_alignment': 'center'},
                                  states=['normal'], manager=default_ui_manager)

        assert shape.collide_point((50, 50)) is True

    def test_set_position(self, _init_pygame, _display_surface_return_none,
                          default_ui_manager: UIManager):
        shape = RectDrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                                  theming_parameters={'text': 'test',
                                                      'font': default_ui_manager.get_theme().get_font([]),
                                                      'normal_text': pygame.Color('#FFFFFF'),
                                                      'normal_text_shadow': pygame.Color('#000000'),
                                                      'shadow_width': 0,
                                                      'border_width': 0,
                                                      'normal_border': pygame.Color('#FFFFFF'),
                                                      'normal_bg': pygame.Color('#000000'),
                                                      'text_horiz_alignment': 'center',
                                                      'text_vert_alignment': 'center'},
                                  states=['normal'], manager=default_ui_manager)

        shape.set_position((50, 50))
        assert shape.containing_rect.topleft == (50, 50)

    def test_set_dimensions(self, _init_pygame, _display_surface_return_none,
                            default_ui_manager: UIManager):
        shape = RectDrawableShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                                  theming_parameters={'text': 'test',
                                                      'font': default_ui_manager.get_theme().get_font([]),
                                                      'normal_text': pygame.Color('#FFFFFF'),
                                                      'normal_text_shadow': pygame.Color('#000000'),
                                                      'shadow_width': 0,
                                                      'border_width': 0,
                                                      'normal_border': pygame.Color('#FFFFFF'),
                                                      'normal_bg': pygame.Color('#000000'),
                                                      'text_horiz_alignment': 'center',
                                                      'text_vert_alignment': 'center'},
                                  states=['normal'], manager=default_ui_manager)

        shape.set_dimensions((50, 50))
        assert shape.containing_rect.width == 50


if __name__ == '__main__':
    pytest.console_main()
