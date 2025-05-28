import os

import pygame
import pytest

from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.core.ui_container import UIContainer
from pygame_gui.elements.ui_2d_slider import UI2DSlider
from pygame_gui.ui_manager import UIManager
from tests.shared_comparators import compare_surfaces


class TestUI2DSlider:

    def test_creation(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                      _display_surface_return_none):
        slider = UI2DSlider(relative_rect=pygame.Rect(100, 100, 100, 100),
                            start_value_x=50,
                            value_range_x=(0, 100),
                            start_value_y=50,
                            value_range_y=(0, 100),
                            manager=default_ui_manager)
        assert slider.image is not None

    def test_rebuild(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                     _display_surface_return_none):
        slider = UI2DSlider(relative_rect=pygame.Rect(100, 100, 100, 100),
                            start_value_x=50,
                            value_range_x=(0, 100),
                            start_value_y=50,
                            value_range_y=(0, 100),
                            manager=default_ui_manager)
        slider.rebuild()

        assert slider.image is not None

    def test_kill(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                  _display_surface_return_none):
        slider = UI2DSlider(relative_rect=pygame.Rect(100, 100, 100, 100),
                            start_value_x=50,
                            value_range_x=(0, 100),
                            start_value_y=50,
                            value_range_y=(0, 100),
                            manager=default_ui_manager)

        assert len(default_ui_manager.get_root_container().elements) == 2
        assert len(default_ui_manager.get_sprite_group().sprites()) == 4
        assert default_ui_manager.get_sprite_group().sprites() == [default_ui_manager.get_root_container(),
                                                                   slider,
                                                                   slider.button_container,
                                                                   slider.sliding_button]
        slider.kill()
        assert len(default_ui_manager.get_root_container().elements) == 0
        assert len(default_ui_manager.get_sprite_group().sprites()) == 1
        assert default_ui_manager.get_sprite_group().sprites() == [default_ui_manager.get_root_container()]

    def test_check_has_moved_recently(self, _init_pygame, default_ui_manager,
                                      _display_surface_return_none):
        slider = UI2DSlider(relative_rect=pygame.Rect(100, 100, 100, 100),
                            start_value_x=50,
                            value_range_x=(0, 100),
                            start_value_y=50,
                            value_range_y=(0, 100),
                            manager=default_ui_manager)

        # move the scroll bar a bit
        slider.sliding_button.held = True
        pygame.mouse.set_pos((slider.sliding_button.get_abs_rect().centerx + 20,
                              slider.sliding_button.get_abs_rect().centery))
        slider.update(0.2)
        assert slider.has_moved_recently is True

    def test_check_update_sliding_bar(self, _init_pygame, default_ui_manager,
                                      _display_surface_return_none):
        slider = UI2DSlider(relative_rect=pygame.Rect(0, 0, 200, 30),
                            start_value_x=50,
                            value_range_x=(0, 100),
                            start_value_y=50,
                            value_range_y=(0, 100),
                            manager=default_ui_manager)

        # scroll down a bit then up again to exercise update
        default_ui_manager.mouse_position = (100, 15)
        slider.sliding_button.held = True
        slider.update(0.3)

        assert slider.grabbed_slider is True

        slider.sliding_button.held = False
        slider.update(0.3)

        assert slider.grabbed_slider is False

        non_y_invert_slider = UI2DSlider(relative_rect=pygame.Rect(0, 0, 200, 30),
                                         start_value_x=50,
                                         value_range_x=(0, 100),
                                         start_value_y=50,
                                         value_range_y=(0, 100),
                                         invert_y=True,
                                         manager=default_ui_manager)

        # scroll down a bit then up again to exercise update
        default_ui_manager.mouse_position = (100, 15)
        non_y_invert_slider.sliding_button.held = True
        non_y_invert_slider.update(0.3)

        assert non_y_invert_slider.grabbed_slider is True

        non_y_invert_slider.sliding_button.held = False
        non_y_invert_slider.update(0.3)

        assert non_y_invert_slider.grabbed_slider is False

    def test_get_current_value(self, _init_pygame, default_ui_manager,
                               _display_surface_return_none):
        slider = UI2DSlider(relative_rect=pygame.Rect(100, 100, 100, 100),
                            start_value_x=50,
                            value_range_x=(0, 100),
                            start_value_y=50,
                            value_range_y=(0, 100),
                            manager=default_ui_manager)

        assert slider.get_current_value() == (50, 50)

    def test_set_current_value_in_range(self, _init_pygame, default_ui_manager,
                                        _display_surface_return_none):
        slider = UI2DSlider(relative_rect=pygame.Rect(100, 100, 100, 100),
                            start_value_x=50,
                            value_range_x=(0, 100),
                            start_value_y=50,
                            value_range_y=(0, 100),
                            manager=default_ui_manager)

        slider.set_current_value(75, 75)
        assert slider.get_current_value() == (75, 75)

        slider = UI2DSlider(relative_rect=pygame.Rect(100, 100, 100, 100),
                            start_value_x=50,
                            value_range_x=(0, 100),
                            start_value_y=50,
                            value_range_y=(0, 100),
                            invert_y=True,
                            manager=default_ui_manager)

        slider.set_current_value(75, 75)
        assert slider.get_current_value() == (75, 75)

    def test_set_current_value_out_of_range(self, _init_pygame, default_ui_manager,
                                            _display_surface_return_none):
        slider = UI2DSlider(relative_rect=pygame.Rect(100, 100, 100, 100),
                            start_value_x=50,
                            value_range_x=(0, 100),
                            start_value_y=50,
                            value_range_y=(0, 100),
                            manager=default_ui_manager)

        with pytest.warns(UserWarning, match='x value not in range'):
            slider.set_current_value(200, 50)

        slider.set_current_value(200, 50, warn=False)

        assert slider.get_current_value() == (100, 50)

        with pytest.warns(UserWarning, match='y value not in range'):
            slider.set_current_value(50, 250)

        slider.set_current_value(50, 250, warn=False)

        assert slider.get_current_value() == (50, 100)

    def test_rebuild_from_theme_data_non_default(self, _init_pygame,
                                                 _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_2d_slider_non_default.json"))

        slider = UI2DSlider(relative_rect=pygame.Rect(100, 100, 100, 100),
                            start_value_x=50,
                            value_range_x=(0, 100),
                            start_value_y=50,
                            value_range_y=(0, 100),
                            manager=manager)
        assert slider.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    @pytest.mark.filterwarnings("ignore:Invalid Theme Colour")
    @pytest.mark.filterwarnings("ignore:Theme validation found")
    @pytest.mark.filterwarnings("ignore:Misc data validation")
    @pytest.mark.filterwarnings("ignore:Font data validation")
    @pytest.mark.filterwarnings("ignore:Image data validation")
    def test_rebuild_from_theme_data_bad_values(self, _init_pygame,
                                                _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests",
                                                     "data",
                                                     "themes",
                                                     "ui_2d_slider_bad_values.json"))

        slider = UI2DSlider(relative_rect=pygame.Rect(100, 100, 100, 100),
                            start_value_x=51,
                            value_range_x=(0, 100),
                            start_value_y=50,
                            value_range_y=(0, 100),
                            manager=manager)
        assert slider.image is not None

    def test_set_position(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        slider = UI2DSlider(relative_rect=pygame.Rect(300, 400, 200, 200),
                            start_value_x=100,
                            value_range_x=(0, 200),
                            start_value_y=100,
                            value_range_y=(0, 200),
                            manager=default_ui_manager)

        slider.set_position((200, 200))

        # try to click on the sliding button
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': 1,
                                                              'pos': (305, 305)}))
        # if we successfully clicked on the moved slider then this button should be True
        assert slider.sliding_button.held is True

    def test_set_relative_position(self, _init_pygame, default_ui_manager,
                                   _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 300),
                                     manager=default_ui_manager)
        slider = UI2DSlider(relative_rect=pygame.Rect(300, 400, 150, 150),
                            start_value_x=75,
                            value_range_x=(0, 150),
                            start_value_y=75,
                            value_range_y=(0, 150),
                            container=test_container,
                            manager=default_ui_manager)

        slider.set_relative_position((150.0, 150.0))

        # try to click on the slider
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': 1,
                                                              'pos': (330, 330)}))

        assert slider.rect.topleft == (250, 250) and slider.sliding_button.held is True

    def test_set_dimensions(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        slider = UI2DSlider(relative_rect=pygame.Rect(0, 0, 150, 150),
                            start_value_x=100,
                            value_range_x=(0, 200),
                            start_value_y=100,
                            value_range_y=(0, 200),
                            manager=default_ui_manager)

        slider.set_dimensions((200, 200))

        # try to click on the slider
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': 1,
                                                              'pos': (105, 105)}))
        # if we successfully clicked on the moved slider then this button should be True
        assert slider.sliding_button.held is True

        slider.set_dimensions((100, 100))

        # try to click on the slider
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': 1,
                                                              'pos': (55, 55)}))
        # if we successfully clicked on the moved slider then this button should be True
        assert slider.sliding_button.held is True

    def test_disable(self, _init_pygame: None, default_ui_manager: UIManager,
                     _display_surface_return_none: None):
        slider = UI2DSlider(relative_rect=pygame.Rect(0, 0, 150, 150),
                            start_value_x=50,
                            value_range_x=(0, 200),
                            start_value_y=50,
                            value_range_y=(0, 200),
                            manager=default_ui_manager)

        slider.disable()

        # process a mouse button down event
        slider.sliding_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1,
                                                        'pos': slider.sliding_button.rect.center}))
        slider.update(0.1)

        pygame.mouse.set_pos((slider.sliding_button.get_abs_rect().centerx + 20,
                              slider.sliding_button.get_abs_rect().centery))
        slider.update(0.1)

        # process a mouse button up event
        slider.sliding_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1,
                                                      'pos': slider.sliding_button.rect.center}))

        assert slider.get_current_value() == (50, 50) and slider.is_enabled is False

    def test_enable(self, _init_pygame: None, default_ui_manager: UIManager,
                    _display_surface_return_none: None):
        slider = UI2DSlider(relative_rect=pygame.Rect(0, 0, 200, 200),
                            start_value_x=100,
                            value_range_x=(0, 200),
                            start_value_y=100,
                            value_range_y=(0, 200),
                            manager=default_ui_manager)

        slider.disable()

        slider.enable()

        assert slider.is_enabled is True

    def test_ints_in_ints_out(self, _init_pygame: None, default_ui_manager: UIManager,
                              _display_surface_return_none: None):
        slider = UI2DSlider(relative_rect=pygame.Rect(0, 0, 150, 150),
                            start_value_x=50,
                            value_range_x=(0, 200),
                            start_value_y=50,
                            value_range_y=(0, 200),
                            manager=default_ui_manager)

        current_value = slider.get_current_value()
        assert isinstance(current_value, tuple)
        assert isinstance(current_value[0], int)
        assert isinstance(current_value[1], int)

        # process a mouse button down event
        slider.sliding_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1,
                                                        'pos': slider.sliding_button.rect.center}))

        pygame.mouse.set_pos((slider.sliding_button.get_abs_rect().centerx + 20,
                              slider.sliding_button.get_abs_rect().centery))
        slider.update(0.1)

        # process a mouse button up event
        slider.sliding_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1,
                                                      'pos': slider.sliding_button.rect.center}))

        current_value = slider.get_current_value()
        assert isinstance(current_value, tuple)
        assert isinstance(current_value[0], int)
        assert isinstance(current_value[1], int)

    def test_floats_in_floats_out(self, _init_pygame: None, default_ui_manager: UIManager,
                                  _display_surface_return_none: None):
        slider = UI2DSlider(relative_rect=pygame.Rect(0, 0, 150, 150),
                            start_value_x=25.0,
                            value_range_x=(0.0, 200.0),
                            start_value_y=25.0,
                            value_range_y=(0.0, 200.0),
                            manager=default_ui_manager)

        current_value = slider.get_current_value()
        assert isinstance(current_value, tuple)
        assert isinstance(current_value[0], float)
        assert isinstance(current_value[1], float)

        # process a mouse button down event
        slider.sliding_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1,
                                                        'pos': slider.sliding_button.rect.center}))

        pygame.mouse.set_pos((slider.sliding_button.get_abs_rect().centerx + 20,
                              slider.sliding_button.get_abs_rect().centery))
        slider.update(0.1)

        # process a mouse button up event
        slider.sliding_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1,
                                                      'pos': slider.sliding_button.rect.center}))

        current_value = slider.get_current_value()
        assert isinstance(current_value, tuple)
        assert isinstance(current_value[0], float)
        assert isinstance(current_value[1], float)

    def test_show(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        slider = UI2DSlider(relative_rect=pygame.Rect(0, 0, 150, 40),
                            start_value_x=50,
                            value_range_x=(0, 200),
                            start_value_y=50,
                            value_range_y=(0, 200),
                            manager=default_ui_manager, visible=0)

        assert slider.visible == 0

        assert slider.sliding_button.visible == 0
        assert slider.button_container.visible == 0

        slider.show()

        assert slider.visible == 1

        assert slider.sliding_button.visible == 1
        assert slider.button_container.visible == 1

    def test_hide(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        slider = UI2DSlider(relative_rect=pygame.Rect(0, 0, 150, 40),
                            start_value_x=50,
                            value_range_x=(0, 200),
                            start_value_y=50,
                            value_range_y=(0, 200),
                            manager=default_ui_manager)

        assert slider.visible == 1

        assert slider.sliding_button.visible == 1
        assert slider.button_container.visible == 1

        slider.hide()

        assert slider.visible == 0

        assert slider.sliding_button.visible == 0
        assert slider.button_container.visible == 0

    def test_show_hide_rendering(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        resolution = (400, 400)
        empty_surface = pygame.Surface(resolution)
        empty_surface.fill(pygame.Color(0, 0, 0))

        surface = empty_surface.copy()
        manager = UIManager(resolution)
        slider = UI2DSlider(relative_rect=pygame.Rect(25, 25, 375, 375),
                            start_value_x=50,
                            value_range_x=(0, 200),
                            start_value_y=50,
                            value_range_y=(0, 200),
                            manager=manager, visible=0)
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        slider.show()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert not compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        slider.hide()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)


if __name__ == '__main__':
    pytest.console_main()
