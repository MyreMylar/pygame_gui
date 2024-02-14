import pytest
import pygame

from pygame_gui.core.ui_element import UIElement
from pygame_gui.core.ui_container import UIContainer
from pygame_gui.core.drawable_shapes import RectDrawableShape
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.core.utility import set_default_manager


class TestUIElement:
    def test_creation(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                  manager=default_ui_manager,
                  container=None,
                  starting_height=0,
                  layer_thickness=1)

        UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                  manager=None,
                  container=None,
                  starting_height=0,
                  layer_thickness=1)

        set_default_manager(None)

        with pytest.raises(ValueError, match="Need to create at least one UIManager to create UIElements"):
            UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                      manager=None,
                      container=None,
                      starting_height=0,
                      layer_thickness=1)

    def test_create_valid_id(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        element = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=None,
                            starting_height=0,
                            layer_thickness=1)

        element._create_valid_ids(None, None, object_id="none", element_id="test")
        assert len(element.element_ids) == 1
        assert element.element_ids == ["test"]
        assert len(element.object_ids) == 1
        assert element.object_ids == ["none"]

    def test_create_invalid_id(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        element = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=None,
                            starting_height=0,
                            layer_thickness=1)
        with pytest.raises(ValueError, match="Object ID cannot contain fullstops or spaces"):
            element._create_valid_ids(None, None, ". .", 'none')

    def test_update_containing_rect_position(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 300), manager=default_ui_manager)
        element_1 = UIElement(relative_rect=pygame.Rect(10, 10, 50, 50),
                              manager=default_ui_manager,
                              container=test_container,
                              starting_height=0,
                              layer_thickness=1,
                              anchors={'left': 'left',
                                       'right': 'left',
                                       'top': 'top',
                                       'bottom': 'top'})

        element_2 = UIElement(relative_rect=pygame.Rect(-60, 10, 50, 50),
                              manager=default_ui_manager,
                              container=test_container,
                              starting_height=0,
                              layer_thickness=1,
                              anchors={'left': 'right',
                                       'right': 'right',
                                       'top': 'top',
                                       'bottom': 'top'})

        element_3 = UIElement(relative_rect=pygame.Rect(-70, -70, 50, 50),
                              manager=default_ui_manager,
                              container=test_container,
                              starting_height=0,
                              layer_thickness=1,
                              anchors={'left': 'right',
                                       'right': 'right',
                                       'top': 'bottom',
                                       'bottom': 'bottom'})

        element_4 = UIElement(relative_rect=pygame.Rect(50, -50, 50, 50),
                              manager=default_ui_manager,
                              container=test_container,
                              starting_height=0,
                              layer_thickness=1,
                              anchors={'left': 'left',
                                       'right': 'left',
                                       'top': 'bottom',
                                       'bottom': 'bottom'})

        element_5 = UIElement(relative_rect=pygame.Rect(10, 10, 50, 50),
                              manager=default_ui_manager,
                              container=test_container,
                              starting_height=0,
                              layer_thickness=1,
                              anchors={'left': 'left',
                                       'right': 'right',
                                       'top': 'top',
                                       'bottom': 'bottom'})

        test_container.rect.topleft = (50, 50)
        test_container.relative_rect.topleft = (50, 50)

        assert element_1.rect.topleft == (110, 110)
        element_1.update_containing_rect_position()
        assert element_1.rect.topleft == (60, 60)

        assert element_2.rect.topleft == (340, 110)
        element_2.update_containing_rect_position()
        assert element_2.rect.topleft == (290, 60)

        assert element_3.rect.topleft == (330, 330)
        element_3.update_containing_rect_position()
        assert element_3.rect.topleft == (280, 280)

        assert element_4.rect.topleft == (150, 350)
        element_4.update_containing_rect_position()
        assert element_4.rect.topleft == (100, 300)

        assert element_5.rect.topleft == (110, 110)
        element_5.update_containing_rect_position()
        assert element_5.rect.topleft == (60, 60)

    def test_set_relative_position(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 300), manager=default_ui_manager)
        element_1 = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                              manager=default_ui_manager,
                              container=test_container,
                              starting_height=0,
                              layer_thickness=1,
                              anchors={'left': 'left',
                                       'right': 'left',
                                       'top': 'top',
                                       'bottom': 'top'})

        element_1.set_relative_position((20, 20))
        assert element_1.rect.topleft == (120, 120)
        assert element_1.rect.size == (50, 50)
        assert element_1.rect.bottomright == (170, 170)

        element_2 = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                              manager=default_ui_manager,
                              container=test_container,
                              starting_height=0,
                              layer_thickness=1,
                              anchors={'left': 'right',
                                       'right': 'right',
                                       'top': 'top',
                                       'bottom': 'top'})

        element_2.set_relative_position((-20, 20))
        assert element_2.rect.topleft == (380, 120)
        assert element_2.rect.size == (50, 50)
        assert element_2.rect.bottomright == (430, 170)

        element_3 = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                              manager=default_ui_manager,
                              container=test_container,
                              starting_height=0,
                              layer_thickness=1,
                              anchors={'left': 'right',
                                       'right': 'right',
                                       'top': 'bottom',
                                       'bottom': 'bottom'})

        element_3.set_relative_position((-70, -70))
        assert element_3.rect.topleft == (330, 330)
        assert element_3.rect.size == (50, 50)
        assert element_3.rect.bottomright == (380, 380)

        element_4 = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                              manager=default_ui_manager,
                              container=test_container,
                              starting_height=0,
                              layer_thickness=1,
                              anchors={'left': 'left',
                                       'right': 'left',
                                       'top': 'bottom',
                                       'bottom': 'bottom'})

        element_4.set_relative_position((30, -70))
        assert element_4.rect.topleft == (130, 330)
        assert element_4.rect.size == (50, 50)
        assert element_4.rect.bottomright == (180, 380)

        element_5 = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                              manager=default_ui_manager,
                              container=test_container,
                              starting_height=0,
                              layer_thickness=1,
                              anchors={'left': 'left',
                                       'right': 'right',
                                       'top': 'top',
                                       'bottom': 'bottom'})

        assert element_5.relative_right_margin == 250
        assert element_5.relative_bottom_margin == 250

        element_5.set_relative_position((20, 20))
        assert element_5.rect.topleft == (120, 120)
        assert element_5.rect.size == (50, 50)
        assert element_5.rect.bottomright == (170, 170)
        assert element_5.relative_right_margin == 230
        assert element_5.relative_bottom_margin == 230

    def test_set_position(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        test_container = UIContainer(relative_rect=pygame.Rect(10, 10, 300, 300), manager=default_ui_manager)
        element = UIElement(relative_rect=pygame.Rect(100, 100, 50, 50),
                            manager=default_ui_manager,
                            container=test_container,
                            starting_height=0,
                            layer_thickness=1)

        element.set_position(pygame.math.Vector2(150.0, 30.0))

        assert element.relative_rect.topleft == (140, 20)

        element_1 = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                              manager=default_ui_manager,
                              container=test_container,
                              starting_height=0,
                              layer_thickness=1,
                              anchors={'left': 'left',
                                       'right': 'left',
                                       'top': 'top',
                                       'bottom': 'top'})

        element_1.set_position((20, 20))
        assert element_1.relative_rect.topleft == (10, 10)
        assert element_1.relative_rect.size == (50, 50)
        assert element_1.relative_rect.bottomright == (60, 60)

        element_2 = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                              manager=default_ui_manager,
                              container=test_container,
                              starting_height=0,
                              layer_thickness=1,
                              anchors={'left': 'right',
                                       'right': 'right',
                                       'top': 'top',
                                       'bottom': 'top'})

        element_2.set_position((280, 120))
        assert element_2.relative_rect.topleft == (-30, 110)
        assert element_2.relative_rect.size == (50, 50)
        assert element_2.relative_rect.bottomright == (20, 160)

        element_3 = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                              manager=default_ui_manager,
                              container=test_container,
                              starting_height=0,
                              layer_thickness=1,
                              anchors={'left': 'right',
                                       'right': 'right',
                                       'top': 'bottom',
                                       'bottom': 'bottom'})

        element_3.set_position((230, 230))
        assert element_3.relative_rect.topleft == (-80, -80)
        assert element_3.relative_rect.size == (50, 50)
        assert element_3.relative_rect.bottomright == (-30, -30)

        element_4 = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                              manager=default_ui_manager,
                              container=test_container,
                              starting_height=0,
                              layer_thickness=1,
                              anchors={'left': 'left',
                                       'right': 'left',
                                       'top': 'bottom',
                                       'bottom': 'bottom'})

        element_4.set_position((130, 230))
        assert element_4.relative_rect.topleft == (120, -80)
        assert element_4.relative_rect.size == (50, 50)
        assert element_4.relative_rect.bottomright == (170, -30)

        element_5 = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                              manager=default_ui_manager,
                              container=test_container,
                              starting_height=0,
                              layer_thickness=1,
                              anchors={'left': 'left',
                                       'right': 'right',
                                       'top': 'top',
                                       'bottom': 'bottom'})

        assert element_5.relative_right_margin == 250
        assert element_5.relative_bottom_margin == 250

        element_5.set_position((20, 20))
        assert element_5.relative_rect.topleft == (10, 10)
        assert element_5.relative_rect.size == (50, 50)
        assert element_5.relative_rect.bottomright == (60, 60)
        assert element_5.relative_right_margin == 240
        assert element_5.relative_bottom_margin == 240

    def test_set_dimensions(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        test_container = UIContainer(relative_rect=pygame.Rect(10, 10, 300, 300),
                                     manager=default_ui_manager)

        element_1 = UIElement(relative_rect=pygame.Rect(30, 30, 50, 50),
                              manager=default_ui_manager,
                              container=test_container,
                              starting_height=0,
                              layer_thickness=1,
                              anchors={'left': 'left',
                                       'right': 'left',
                                       'top': 'top',
                                       'bottom': 'top'})
        assert element_1.relative_right_margin is None
        assert element_1.relative_bottom_margin is None

        element_1.set_dimensions((20, 20))
        assert element_1.relative_rect.topleft == (30, 30)
        assert element_1.relative_rect.size == (20, 20)
        assert element_1.relative_rect.bottomright == (50, 50)
        assert element_1.rect.topleft == (40, 40)
        assert element_1.rect.size == (20, 20)
        assert element_1.rect.bottomright == (60, 60)
        assert element_1.relative_right_margin is None
        assert element_1.relative_bottom_margin is None

        element_2 = UIElement(relative_rect=pygame.Rect(-60, 10, 50, 50),
                              manager=default_ui_manager,
                              container=test_container,
                              starting_height=0,
                              layer_thickness=1,
                              anchors={'left': 'right',
                                       'right': 'right',
                                       'top': 'top',
                                       'bottom': 'top'})

        assert element_2.relative_right_margin == 10
        assert element_2.relative_bottom_margin is None
        element_2.set_dimensions((60, 60))
        assert element_2.relative_rect.topleft == (-60, 10)
        assert element_2.relative_rect.size == (60, 60)
        assert element_2.relative_rect.bottomright == (0, 70)
        assert element_2.rect.topleft == (250, 20)
        assert element_2.rect.size == (60, 60)
        assert element_2.rect.bottomright == (310, 80)
        assert element_2.relative_right_margin == 0
        assert element_2.relative_bottom_margin is None

        element_3 = UIElement(relative_rect=pygame.Rect(-70, -70, 50, 50),
                              manager=default_ui_manager,
                              container=test_container,
                              starting_height=0,
                              layer_thickness=1,
                              anchors={'left': 'right',
                                       'right': 'right',
                                       'top': 'bottom',
                                       'bottom': 'bottom'})

        assert element_3.relative_right_margin == 20
        assert element_3.relative_bottom_margin == 20
        element_3.set_dimensions((30, 30))
        assert element_3.relative_rect.topleft == (-70, -70)
        assert element_3.relative_rect.size == (30, 30)
        assert element_3.relative_rect.bottomright == (-40, -40)
        assert element_3.rect.topleft == (240, 240)
        assert element_3.rect.size == (30, 30)
        assert element_3.rect.bottomright == (270, 270)
        assert element_3.relative_right_margin == 40
        assert element_3.relative_bottom_margin == 40

        element_4 = UIElement(relative_rect=pygame.Rect(50, -50, 50, 50),
                              manager=default_ui_manager,
                              container=test_container,
                              starting_height=0,
                              layer_thickness=1,
                              anchors={'left': 'left',
                                       'right': 'left',
                                       'top': 'bottom',
                                       'bottom': 'bottom'})

        assert element_4.relative_right_margin is None
        assert element_4.relative_bottom_margin == 0

        element_4.set_dimensions((100, 100))
        assert element_4.relative_rect.topleft == (50, -50)
        assert element_4.relative_rect.size == (100, 100)
        assert element_4.relative_rect.bottomright == (150, 50)
        assert element_4.rect.topleft == (60, 260)
        assert element_4.rect.size == (100, 100)
        assert element_4.rect.bottomright == (160, 360)
        assert element_4.relative_right_margin is None
        assert element_4.relative_bottom_margin == -50

        element_5 = UIElement(relative_rect=pygame.Rect(10, 10, 50, 50),
                              manager=default_ui_manager,
                              container=test_container,
                              starting_height=0,
                              layer_thickness=1,
                              anchors={'left': 'left',
                                       'right': 'right',
                                       'top': 'top',
                                       'bottom': 'bottom'})

        assert element_5.relative_right_margin == 240
        assert element_5.relative_bottom_margin == 240

        element_5.set_dimensions((90, 90))
        assert element_5.relative_rect.topleft == (10, 10)
        assert element_5.relative_rect.size == (90, 90)
        assert element_5.relative_rect.bottomright == (100, 100)
        assert element_5.rect.topleft == (20, 20)
        assert element_5.rect.size == (90, 90)
        assert element_5.rect.bottomright == (110, 110)
        assert element_5.relative_right_margin == 200
        assert element_5.relative_bottom_margin == 200

    def test_update(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        element = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=None,
                            starting_height=0,
                            layer_thickness=1)
        element.drawable_shape = RectDrawableShape(containing_rect=element.rect,
                                                   theming_parameters={'normal_bg': pygame.Color('#FFFF00'),
                                                                       'normal_border': pygame.Color('#FF0000'),
                                                                       'border_width': 1,
                                                                       'shadow_width': 1},
                                                   states=['normal'],
                                                   manager=default_ui_manager)
        element.drawable_shape.states['normal'].has_fresh_surface = True

        element.update(time_delta=0.05)

        assert element.image is not None

    def test_change_layer(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        element = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=None,
                            starting_height=0,
                            layer_thickness=1)

        assert element.get_top_layer() == 1
        element.change_layer(4)
        assert element.get_top_layer() == 5

    def test_kill(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        test_container = UIContainer(relative_rect=pygame.Rect(10, 10, 300, 300), manager=default_ui_manager)

        element = UIElement(relative_rect=pygame.Rect(30, 30, 50, 50),
                            manager=default_ui_manager,
                            container=test_container,
                            starting_height=0,
                            layer_thickness=1,
                            anchors={'left': 'left',
                                     'right': 'left',
                                     'top': 'top',
                                     'bottom': 'top'})

        assert len(test_container.elements) == 1
        assert len(default_ui_manager.ui_group.sprites()) == 3
        assert default_ui_manager.ui_group.sprites() == [default_ui_manager.get_root_container(),
                                                         test_container,
                                                         element]
        element.kill()
        assert len(test_container.elements) == 0
        assert len(default_ui_manager.ui_group.sprites()) == 2
        assert default_ui_manager.ui_group.sprites() == [default_ui_manager.get_root_container(),
                                                         test_container]

    def test_check_hover(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        element = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=None,
                            starting_height=0,
                            layer_thickness=1)

        default_ui_manager.mouse_position = (25, 25)
        assert element.check_hover(0.5, False) is True

        default_ui_manager.mouse_position = (100, 200)

        assert element.check_hover(0.5, False) is False

    def test_on_fresh_drawable_shape_ready(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        element = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=None,
                            starting_height=0,
                            layer_thickness=1)
        element.drawable_shape = RectDrawableShape(containing_rect=element.rect,
                                                   theming_parameters={'normal_bg': pygame.Color('#FFFF00'),
                                                                       'normal_border': pygame.Color('#FF0000'),
                                                                       'border_width': 1,
                                                                       'shadow_width': 1},
                                                   states=['normal'],
                                                   manager=default_ui_manager)
        element.drawable_shape.states['normal'].has_fresh_surface = True

        element.on_fresh_drawable_shape_ready()

        assert element.image is not None

    def test_stub_methods(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        element = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=None,
                            starting_height=0,
                            layer_thickness=1)

        element.on_hovered()
        element.on_unhovered()
        element.can_hover()
        element.while_hovering(0.5, pygame.math.Vector2(0.0, 0.0))
        assert element.can_hover() is True
        assert element.process_event(pygame.event.Event(pygame.USEREVENT, {})) is False
        element.focus()
        element.unfocus()
        element.rebuild_from_changed_theme_data()

    def test_hover_point(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        element = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=None,
                            starting_height=0,
                            layer_thickness=1)

        assert element.hover_point(25, 25) is True
        assert element.hover_point(100, 100) is False

    def test_set_visual_debug_mode(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                                   _display_surface_return_none):

        default_ui_manager.preload_fonts([{'name': 'fira_code', 'point_size': 8, 'style': 'regular'}])
        element = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=None,
                            starting_height=0,
                            layer_thickness=1)

        assert element.image is None
        element.set_visual_debug_mode(True)
        assert element.image is not None
        element.set_visual_debug_mode(False)
        assert element.image is None

        coloured_surface = pygame.Surface((50, 50))
        coloured_surface.fill(pygame.Color(200, 80, 80, 255))
        element._set_image(coloured_surface)
        assert element.pre_debug_image is None
        element.set_visual_debug_mode(True)
        assert element.pre_debug_image is not None
        element.set_visual_debug_mode(False)
        assert element.pre_debug_image is None

    def test_set_image_clip(self, _init_pygame, _display_surface_return_none, default_ui_manager: IUIManagerInterface):
        element = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=None,
                            starting_height=0,
                            layer_thickness=1)

        coloured_surface = pygame.Surface((50, 50), flags=pygame.SRCALPHA, depth=32)
        coloured_surface.fill(pygame.Color(200, 80, 80, 255))
        element._set_image(coloured_surface)

        after_clip_in_clip_colour = element.image.get_at((15, 25))
        after_clip_out_clip_colour = element.image.get_at((35, 25))
        assert after_clip_in_clip_colour == pygame.Color(200, 80, 80, 255)
        assert after_clip_out_clip_colour == pygame.Color(200, 80, 80, 255)
        element._set_image_clip(None)
        after_clip_in_clip_colour = element.image.get_at((15, 25))
        after_clip_out_clip_colour = element.image.get_at((35, 25))
        assert after_clip_in_clip_colour == pygame.Color(200, 80, 80, 255)
        assert after_clip_out_clip_colour == pygame.Color(200, 80, 80, 255)
        element._set_image_clip(pygame.Rect(0, 0, 25, 50))
        after_clip_in_clip_colour = element.image.get_at((15, 25))
        after_clip_out_clip_colour = element.image.get_at((35, 25))
        assert after_clip_in_clip_colour == pygame.Color(200, 80, 80, 255)
        assert after_clip_out_clip_colour == pygame.Color(0, 0, 0, 0)
        element._set_image_clip(None)
        after_clip_in_clip_colour = element.image.get_at((15, 25))
        after_clip_out_clip_colour = element.image.get_at((35, 25))
        assert after_clip_in_clip_colour == pygame.Color(200, 80, 80, 255)
        assert after_clip_out_clip_colour == pygame.Color(200, 80, 80, 255)

    def test_set_image(self, _init_pygame, _display_surface_return_none, default_ui_manager: IUIManagerInterface):
        element = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=None,
                            starting_height=0,
                            layer_thickness=1)

        coloured_surface_1 = pygame.Surface((50, 50), flags=pygame.SRCALPHA, depth=32)
        coloured_surface_1.fill(pygame.Color(200, 80, 80, 255))
        element._set_image(coloured_surface_1)
        assert element.image.get_at((10, 10)) == pygame.Color(200, 80, 80, 255)

        coloured_surface_2 = pygame.Surface((50, 50), flags=pygame.SRCALPHA, depth=32)
        coloured_surface_2.fill(pygame.Color(200, 150, 180, 255))
        element._set_image_clip(pygame.Rect(0, 0, 25, 50))
        element._set_image(coloured_surface_2)
        assert element.image.get_at((10, 10)) == pygame.Color(200, 150, 180, 255)

        element._set_image_clip(pygame.Rect(0, 0, 0, 0))
        element._set_image(coloured_surface_1)
        assert element.image == default_ui_manager.get_universal_empty_surface()

        element._set_image_clip(None)
        element._set_image(None)
        assert element.image is None

    def test_show(self, _init_pygame, default_ui_manager: IUIManagerInterface, _display_surface_return_none):
        element = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=None,
                            starting_height=0,
                            layer_thickness=1,
                            visible=0)

        assert element.visible == 0
        element.show()
        assert element.visible == 1

    def test_hide(self, _init_pygame, default_ui_manager: IUIManagerInterface, _display_surface_return_none):
        element = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=None,
                            starting_height=0,
                            layer_thickness=1)

        element.hovered = True
        element.hover_time = 1.0

        assert element.visible == 1

        element.hide()

        assert element.visible == 0

        assert element.hovered is False
        assert element.hover_time == 0.0

    def test_get_relative_rect(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        element = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=None,
                            starting_height=0,
                            layer_thickness=1)

        assert element.get_relative_rect() == pygame.Rect(0, 0, 50, 50)

    def test_get_element_ids(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        element = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=None,
                            starting_height=0,
                            layer_thickness=1)

        assert element.get_element_ids() is None

    def test_invalid_container(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        bad_container = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                                  manager=default_ui_manager,
                                  container=None,
                                  starting_height=0,
                                  layer_thickness=1)

        with pytest.raises(ValueError):
            element = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                                manager=default_ui_manager,
                                container=bad_container,
                                starting_height=0,
                                layer_thickness=1)

    def test_anchor_targets(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        element_1 = UIElement(relative_rect=pygame.Rect(100, 50, 40, 40),
                              manager=default_ui_manager,
                              container=None,
                              starting_height=0,
                              layer_thickness=1)

        element_2 = UIElement(relative_rect=pygame.Rect(0, 50, 40, 40),
                              manager=default_ui_manager,
                              container=None,
                              starting_height=0,
                              layer_thickness=1)

        element_3 = UIElement(relative_rect=pygame.Rect(50, 0, 40, 40),
                              manager=default_ui_manager,
                              container=None,
                              starting_height=0,
                              layer_thickness=1)

        element_4 = UIElement(relative_rect=pygame.Rect(50, 100, 40, 40),
                              manager=default_ui_manager,
                              container=None,
                              starting_height=0,
                              layer_thickness=1)

        anchor_element = UIElement(relative_rect=pygame.Rect(50, 50, 40, 40),
                                   manager=default_ui_manager,
                                   container=None,
                                   starting_height=0,
                                   layer_thickness=1,
                                   anchors={'top': 'top',
                                            'bottom': 'bottom',
                                            'left': 'left',
                                            'right': 'right',
                                            'left_target': element_1,
                                            'right_target': element_2,
                                            'top_target': element_3,
                                            'bottom_target': element_4})

        anchor_element.set_dimensions((30, 30))
        anchor_element.set_relative_position((45, 45))

        with pytest.warns(expected_warning=UserWarning, match=r'Supplied \w+ anchors are invalid'):
            anchor_element = UIElement(relative_rect=pygame.Rect(50, 50, 40, 40),
                                       manager=default_ui_manager,
                                       container=None,
                                       starting_height=0,
                                       layer_thickness=1,
                                       anchors={'top': 'trop',
                                                'bottom': 'bettom',
                                                'left': 'laft',
                                                'right': 'roight',
                                                'left_target': element_1,
                                                'right_target': element_2,
                                                'top_target': element_3,
                                                'bottom_target': element_4})

            anchor_element.set_dimensions((30, 30))
            anchor_element.set_relative_position((45, 45))
            anchor_element.set_position((45, 45))

        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 300), manager=default_ui_manager)

        center_element = UIElement(relative_rect=pygame.Rect(0, 0, 40, 40),
                                   manager=default_ui_manager,
                                   container=test_container,
                                   starting_height=0,
                                   layer_thickness=1,
                                   anchors={'center': 'center'})

        assert center_element.get_abs_rect().topleft == (230, 230)
        assert center_element.get_abs_rect().center == (250, 250)
        assert center_element.get_relative_rect().center == (20, 20)
        center_element.set_position((230, 230))
        assert center_element.get_relative_rect().center == (20, 20)

        UIElement(relative_rect=pygame.Rect(0, 0, 40, 40),
                  manager=default_ui_manager,
                  container=None,
                  starting_height=0,
                  layer_thickness=1,
                  anchors={'centerx': 'centerx'})

        UIElement(relative_rect=pygame.Rect(0, 0, 40, 40),
                  manager=default_ui_manager,
                  container=None,
                  starting_height=0,
                  layer_thickness=1,
                  anchors={'centery': 'centery'})

        UIElement(relative_rect=pygame.Rect(0, 0, 40, 40),
                  manager=default_ui_manager,
                  container=None,
                  starting_height=0,
                  layer_thickness=1,
                  anchors={'centerx': 'centerx',
                           'centerx_target': element_1})

        UIElement(relative_rect=pygame.Rect(0, 0, 40, 40),
                  manager=default_ui_manager,
                  container=None,
                  starting_height=0,
                  layer_thickness=1,
                  anchors={'centery': 'centery',
                           'centery_target': element_2})

        UIElement(relative_rect=pygame.Rect(0, 0, 40, 40),
                  manager=default_ui_manager,
                  container=None,
                  starting_height=0,
                  layer_thickness=1,
                  anchors={'left': 'left'})

        UIElement(relative_rect=pygame.Rect(0, 0, 40, 40),
                  manager=default_ui_manager,
                  container=None,
                  starting_height=0,
                  layer_thickness=1,
                  anchors={'left': 'right'})

        UIElement(relative_rect=pygame.Rect(0, 0, 40, 40),
                  manager=default_ui_manager,
                  container=None,
                  starting_height=0,
                  layer_thickness=1,
                  anchors={'right': 'right'})

        UIElement(relative_rect=pygame.Rect(0, 0, 40, 40),
                  manager=default_ui_manager,
                  container=None,
                  starting_height=0,
                  layer_thickness=1,
                  anchors={'right': 'left'})

    def test_enable_disable(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        element = UIElement(relative_rect=pygame.Rect(0, 0, 50, 50),
                            manager=default_ui_manager,
                            container=None,
                            starting_height=0,
                            layer_thickness=1)

        element.disable()
        assert not element.is_enabled
        element.enable()
        assert element.is_enabled


if __name__ == '__main__':
    pytest.console_main()
