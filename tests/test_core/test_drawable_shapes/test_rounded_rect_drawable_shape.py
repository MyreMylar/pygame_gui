import pygame
import pytest

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, \
    _display_surface_return_none

from pygame_gui.core.drawable_shapes.rounded_rect_drawable_shape import RoundedRectangleShape
from pygame_gui.ui_manager import UIManager
from pygame_gui.core.colour_gradient import ColourGradient


class TestRoundedRectangleShape:
    def test_creation(self, _init_pygame, default_ui_manager: UIManager):
        RoundedRectangleShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                              theming_parameters={'text': 'test',
                                                  'font': default_ui_manager.get_theme().get_font(object_ids=[],
                                                                                                  element_ids=[]),
                                                  'shadow_width': 0,
                                                  'border_width': 0,
                                                  'normal_border': pygame.Color('#FFFFFF'),
                                                  'normal_bg': pygame.Color('#000000'),
                                                  'shape_corner_radius': 2,
                                                  'text_horiz_alignment': 'center',
                                                  'text_vert_alignment': 'center'},
                              states=['normal'], manager=default_ui_manager)

    def test_update(self, _init_pygame, default_ui_manager: UIManager):
        shape = RoundedRectangleShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                              theming_parameters={'text': 'test',
                                                  'font': default_ui_manager.get_theme().get_font(object_ids=[],
                                                                                                  element_ids=[]),
                                                  'shadow_width': 2,
                                                  'border_width': 1,
                                                  'normal_border': pygame.Color('#FFFFFF'),
                                                  'normal_bg': pygame.Color('#000000'),
                                                  'hovered_border': pygame.Color('#FFFFFF'),
                                                  'hovered_bg': pygame.Color('#000000'),
                                                  'shape_corner_radius': 2,
                                                  'text_horiz_alignment': 'center',
                                                  'text_vert_alignment': 'center'},
                              states=['normal'], manager=default_ui_manager)
        shape.update()
        shape.update()

    def test_full_rebuild_on_size_change_negative_values(self, _init_pygame, default_ui_manager: UIManager):
        with pytest.warns(UserWarning, match='Clamping shadow_width'):
            shape = RoundedRectangleShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                                          theming_parameters={'text': 'test',
                                                              'font': default_ui_manager.ui_theme.get_font(
                                                                  object_ids=[],
                                                                  element_ids=[]),
                                                              'shadow_width': -10,
                                                              'border_width': -10,
                                                              'normal_border': pygame.Color('#FFFFFF'),
                                                              'normal_bg': pygame.Color('#000000'),
                                                              'shape_corner_radius': -10,
                                                              'text_horiz_alignment': 'center',
                                                              'text_vert_alignment': 'center'},
                                          states=['normal'], manager=default_ui_manager)
            shape.full_rebuild_on_size_change()

    def test_full_rebuild_on_size_change_corner_only_negative_values(self, _init_pygame, default_ui_manager: UIManager):
        with pytest.warns(UserWarning, match='Clamping shape_corner_radius'):
            shape = RoundedRectangleShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                                          theming_parameters={'text': 'test',
                                                              'font': default_ui_manager.ui_theme.get_font(
                                                                  object_ids=[],
                                                                  element_ids=[]),
                                                              'shadow_width': 2,
                                                              'border_width': 1,
                                                              'normal_border': pygame.Color('#FFFFFF'),
                                                              'normal_bg': pygame.Color('#000000'),
                                                              'shape_corner_radius': -10,
                                                              'text_horiz_alignment': 'center',
                                                              'text_vert_alignment': 'center'},
                                          states=['normal'], manager=default_ui_manager)
            shape.full_rebuild_on_size_change()

    def test_full_rebuild_on_size_change_large(self, _init_pygame, default_ui_manager: UIManager):
        with pytest.warns(UserWarning, match='Clamping shadow_width'):
            shape = RoundedRectangleShape(containing_rect=pygame.Rect(0, 0, 25, 25),
                                          theming_parameters={'text': 'test',
                                                              'font': default_ui_manager.ui_theme.get_font(
                                                                  object_ids=[],
                                                                  element_ids=[]),
                                                              'shadow_width': 20,
                                                              'border_width': 20,
                                                              'shape_corner_radius': 20,
                                                              'normal_border': pygame.Color('#FFFFFF'),
                                                              'normal_bg': pygame.Color('#000000'),
                                                              'text_horiz_alignment': 'center',
                                                              'text_vert_alignment': 'center'},
                                          states=['normal'], manager=default_ui_manager)
            shape.full_rebuild_on_size_change()

    def test_full_rebuild_on_size_change_large_corners_only(self, _init_pygame, default_ui_manager: UIManager):
        with pytest.warns(UserWarning, match='Clamping shape_corner_radius'):
            shape = RoundedRectangleShape(containing_rect=pygame.Rect(0, 0, 50, 50),
                                          theming_parameters={'text': 'test',
                                                              'font': default_ui_manager.ui_theme.get_font(
                                                                  object_ids=[],
                                                                  element_ids=[]),
                                                              'shadow_width': 1,
                                                              'border_width': 2,
                                                              'shape_corner_radius': 30,
                                                              'normal_border': pygame.Color('#FFFFFF'),
                                                              'normal_bg': pygame.Color('#000000'),
                                                              'text_horiz_alignment': 'center',
                                                              'text_vert_alignment': 'center'},
                                          states=['normal'], manager=default_ui_manager)
            shape.full_rebuild_on_size_change()

    def test_full_rebuild_on_size_change_large_shadow(self, _init_pygame, default_ui_manager: UIManager):
        with pytest.warns(UserWarning, match='Clamping shape_corner_radius'):
            theming_params = {'text': 'test',
                              'font': default_ui_manager.ui_theme.get_font(object_ids=[],
                                                                           element_ids=[]),
                              'shadow_width': 1,
                              'border_width': 0,
                              'shape_corner_radius': 2,
                              'normal_border': pygame.Color('#FFFFFF'),
                              'normal_bg': pygame.Color('#000000'),
                              'text_horiz_alignment': 'center',
                              'text_vert_alignment': 'center'}
            shape = RoundedRectangleShape(containing_rect=pygame.Rect(0, 0, 2, 2),
                                          theming_parameters=theming_params,
                                          states=['normal'], manager=default_ui_manager)
            shape.full_rebuild_on_size_change()

    def test_collide_point(self, _init_pygame, default_ui_manager: UIManager):
        theming_params = {'text': 'test',
                          'font': default_ui_manager.ui_theme.get_font(object_ids=[],
                                                                       element_ids=[]),
                          'shadow_width': 0,
                          'border_width': 0,
                          'shape_corner_radius': 40,
                          'normal_border': pygame.Color('#FFFFFF'),
                          'normal_bg': pygame.Color('#000000'),
                          'text_horiz_alignment': 'center',
                          'text_vert_alignment': 'center'}
        shape = RoundedRectangleShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                                      theming_parameters=theming_params,
                                      states=['normal'], manager=default_ui_manager)
        assert shape.collide_point((50, 50)) is True
        assert shape.collide_point((5, 50)) is True
        assert shape.collide_point((25, 25)) is True
        assert shape.collide_point((14, 14)) is True

    def test_set_position(self, _init_pygame, default_ui_manager: UIManager):
        shape = RoundedRectangleShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                                      theming_parameters={'text': 'test',
                                                          'font': default_ui_manager.ui_theme.get_font(object_ids=[],
                                                                                                       element_ids=[]),
                                                          'shadow_width': 0,
                                                          'border_width': 0,
                                                          'shape_corner_radius': 2,
                                                          'normal_border': pygame.Color('#FFFFFF'),
                                                          'normal_bg': pygame.Color('#000000'),
                                                          'text_horiz_alignment': 'center',
                                                          'text_vert_alignment': 'center'},
                                      states=['normal'], manager=default_ui_manager)
        shape.set_position((50, 50))

    def test_set_dimensions(self, _init_pygame, default_ui_manager: UIManager):
        shape = RoundedRectangleShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                                      theming_parameters={'text': 'test',
                                                          'font': default_ui_manager.ui_theme.get_font(object_ids=[],
                                                                                                       element_ids=[]),
                                                          'shadow_width': 0,
                                                          'border_width': 0,
                                                          'shape_corner_radius': 2,
                                                          'normal_border': pygame.Color('#FFFFFF'),
                                                          'normal_bg': pygame.Color('#000000'),
                                                          'text_horiz_alignment': 'center',
                                                          'text_vert_alignment': 'center'},
                                      states=['normal'], manager=default_ui_manager)
        shape.set_dimensions((50, 50))

    def test_creation_with_gradients(self, _init_pygame, default_ui_manager: UIManager):
        RoundedRectangleShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                              theming_parameters={'text': 'test',
                                                  'font': default_ui_manager.get_theme().get_font(object_ids=[],
                                                                                                  element_ids=[]),
                                                  'shadow_width': 0,
                                                  'border_width': 0,
                                                  'normal_border': ColourGradient(0, pygame.Color('#000000'),
                                                                                  pygame.Color('#FFFFFF')),
                                                  'normal_bg': ColourGradient(0, pygame.Color('#000000'),
                                                                              pygame.Color('#FFFFFF')),
                                                  'shape_corner_radius': 2,
                                                  'text_horiz_alignment': 'center',
                                                  'text_vert_alignment': 'center'},
                              states=['normal'], manager=default_ui_manager)

    def test_creation_with_filled_bar(self, _init_pygame, default_ui_manager: UIManager):
        RoundedRectangleShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                              theming_parameters={'text': 'test',
                                                  'font': default_ui_manager.get_theme().get_font(object_ids=[],
                                                                                                  element_ids=[]),
                                                  'shadow_width': 2,
                                                  'border_width': 1,
                                                  'normal_border': ColourGradient(0, pygame.Color('#000000'),
                                                                                  pygame.Color('#FFFFFF')),
                                                  'normal_bg': ColourGradient(0, pygame.Color('#000000'),
                                                                              pygame.Color('#FFFFFF')),
                                                  'filled_bar': ColourGradient(0, pygame.Color('#000000'),
                                                                               pygame.Color('#FFFFFF')),
                                                  'filled_bar_width': 50,
                                                  'shape_corner_radius': 2,
                                                  'text_horiz_alignment': 'center',
                                                  'text_vert_alignment': 'center'},
                              states=['normal'], manager=default_ui_manager)

    def test_creation_with_filled_bar_no_gradient(self, _init_pygame, default_ui_manager: UIManager):
        RoundedRectangleShape(containing_rect=pygame.Rect(0, 0, 100, 100),
                              theming_parameters={'text': 'test',
                                                  'font': default_ui_manager.get_theme().get_font(object_ids=[],
                                                                                                  element_ids=[]),
                                                  'shadow_width': 2,
                                                  'border_width': 1,
                                                  'normal_border': ColourGradient(0, pygame.Color('#000000'),
                                                                                  pygame.Color('#FFFFFF')),
                                                  'normal_bg': ColourGradient(0, pygame.Color('#000000'),
                                                                              pygame.Color('#FFFFFF')),
                                                  'filled_bar': pygame.Color('#000000'),
                                                  'filled_bar_width': 50,
                                                  'shape_corner_radius': 2,
                                                  'text_horiz_alignment': 'center',
                                                  'text_vert_alignment': 'center'},
                              states=['normal'], manager=default_ui_manager)
