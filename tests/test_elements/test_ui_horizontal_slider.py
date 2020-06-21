import os
import pytest
import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager
from tests.shared_fixtures import default_display_surface, _display_surface_return_none
from tests.shared_comparators import compare_surfaces

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_horizontal_slider import UIHorizontalSlider
from pygame_gui.core.ui_container import UIContainer
from pygame_gui.core.interfaces import IUIManagerInterface


class TestUIHorizontalSlider:

    def test_creation(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                      _display_surface_return_none):
        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(100, 100, 200, 30),
                                        start_value=50,
                                        value_range=(0, 100),
                                        manager=default_ui_manager)
        assert scroll_bar.image is not None

    def test_rebuild(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                     _display_surface_return_none):
        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(100, 100, 200, 30),
                                        start_value=50,
                                        value_range=(0, 100),
                                        manager=default_ui_manager)
        scroll_bar.rebuild()
        assert scroll_bar.image is not None

    def test_kill(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                  _display_surface_return_none):
        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(100, 100, 200, 30),
                                        start_value=50,
                                        value_range=(0, 100),
                                        manager=default_ui_manager)

        assert len(default_ui_manager.get_root_container().elements) == 2
        assert len(default_ui_manager.get_sprite_group().sprites()) == 6
        assert default_ui_manager.get_sprite_group().sprites() == [default_ui_manager.get_root_container(),
                                                                   scroll_bar,
                                                                   scroll_bar.button_container,
                                                                   scroll_bar.left_button,
                                                                   scroll_bar.right_button,
                                                                   scroll_bar.sliding_button]
        scroll_bar.kill()
        assert len(default_ui_manager.get_root_container().elements) == 0
        assert len(default_ui_manager.get_sprite_group().sprites()) == 1
        assert default_ui_manager.get_sprite_group().sprites() == [default_ui_manager.get_root_container()]

    def test_check_has_moved_recently(self, _init_pygame, default_ui_manager,
                                      _display_surface_return_none):
        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(100, 100, 200, 30),
                                        start_value=50,
                                        value_range=(0, 100),
                                        manager=default_ui_manager)

        # move the scroll bar a bit
        scroll_bar.left_button.held = True
        scroll_bar.update(0.2)
        assert scroll_bar.has_moved_recently is True

    def test_check_update_buttons(self, _init_pygame, default_ui_manager,
                                  _display_surface_return_none):
        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(100, 100, 200, 30),
                                        start_value=50,
                                        value_range=(0, 100),
                                        manager=default_ui_manager)

        # scroll down a bit then up again to exercise update
        scroll_bar.get_current_value()  # Clear has moved this turn
        scroll_bar.left_button.held = True
        scroll_bar.update(0.3)
        scroll_bar.left_button.held = False
        scroll_bar.right_button.held = True
        scroll_bar.update(0.3)

        assert scroll_bar.has_moved_recently is True

    def test_check_update_sliding_bar(self, _init_pygame, default_ui_manager,
                                      _display_surface_return_none):
        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(0, 0, 200, 30),
                                        start_value=50,
                                        value_range=(0, 100),
                                        manager=default_ui_manager)

        # scroll down a bit then up again to exercise update
        default_ui_manager.mouse_position = (100, 15)
        scroll_bar.sliding_button.held = True
        scroll_bar.update(0.3)

        assert scroll_bar.grabbed_slider is True

        scroll_bar.sliding_button.held = False
        scroll_bar.update(0.3)

        assert scroll_bar.grabbed_slider is False

    def test_get_current_value(self, _init_pygame, default_ui_manager,
                               _display_surface_return_none):
        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(100, 100, 200, 30),
                                        start_value=50,
                                        value_range=(0, 100),
                                        manager=default_ui_manager)

        assert scroll_bar.get_current_value() == 50

    def test_set_current_value_in_range(self, _init_pygame, default_ui_manager,
                                        _display_surface_return_none):
        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(100, 100, 200, 30),
                                        start_value=50,
                                        value_range=(0, 100),
                                        manager=default_ui_manager)

        scroll_bar.set_current_value(75)
        assert scroll_bar.get_current_value() == 75

    def test_set_current_value_out_of_range(self, _init_pygame, default_ui_manager,
                                            _display_surface_return_none):
        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(100, 100, 200, 30),
                                        start_value=50,
                                        value_range=(0, 100),
                                        manager=default_ui_manager)

        with pytest.warns(UserWarning, match='value not in range'):
            scroll_bar.set_current_value(200)

    def test_rebuild_from_theme_data_non_default(self, _init_pygame,
                                                 _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_horizontal_slider_non_default.json"))

        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(100, 100, 200, 30),
                                        start_value=50,
                                        value_range=(0, 100),
                                        manager=manager)
        assert scroll_bar.image is not None

    def test_rebuild_from_theme_data_no_arrow_buttons(self, _init_pygame,
                                                      _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests",
                                                     "data",
                                                     "themes",
                                                     "ui_horizontal_slider_no_arrows.json"))

        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(100, 100, 200, 30),
                                        start_value=50,
                                        value_range=(0, 100),
                                        manager=manager)

        assert scroll_bar.left_button is None
        assert scroll_bar.right_button is None
        assert scroll_bar.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    def test_rebuild_from_theme_data_bad_values(self, _init_pygame,
                                                _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests",
                                                     "data",
                                                     "themes",
                                                     "ui_horizontal_slider_bad_values.json"))

        scroll_bar = UIHorizontalSlider(relative_rect=pygame.Rect(100, 100, 200, 30),
                                        start_value=51,
                                        value_range=(0, 100),
                                        manager=manager)
        assert scroll_bar.image is not None

    def test_set_position(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        slider = UIHorizontalSlider(relative_rect=pygame.Rect(300, 400, 150, 40), start_value=50,
                                    value_range=(0, 200), manager=default_ui_manager)

        slider.set_position((200, 200))

        # try to click on the slider
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': 1,
                                                              'pos': (205, 205)}))
        # if we successfully clicked on the moved slider then this button should be True
        assert slider.left_button.held is True

    def test_set_relative_position(self, _init_pygame, default_ui_manager,
                                   _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60),
                                     manager=default_ui_manager)
        slider = UIHorizontalSlider(relative_rect=pygame.Rect(300, 400, 150, 40),
                                    start_value=50,
                                    container=test_container,
                                    value_range=(0, 200), manager=default_ui_manager)

        slider.set_relative_position((150.0, 30.0))

        # try to click on the slider
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': 1,
                                                              'pos': (260, 150)}))

        assert slider.rect.topleft == (250, 130) and slider.left_button.held is True

    def test_set_dimensions(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        slider = UIHorizontalSlider(relative_rect=pygame.Rect(0, 0, 150, 40), start_value=50,
                                    value_range=(0, 200), manager=default_ui_manager)

        slider.set_dimensions((200, 60))

        # try to click on the slider
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': 1,
                                                              'pos': (195, 50)}))
        # if we successfully clicked on the moved slider then this button should be True
        assert slider.right_button.held is True
        assert slider.right_button.rect.top == (slider.shadow_width + slider.border_width)
        assert slider.right_button.rect.bottom == 60 - (slider.shadow_width + slider.border_width)
        assert slider.right_button.rect.right == 200 - (slider.shadow_width + slider.border_width)

        slider.set_dimensions((100, 30))

        # try to click on the slider
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': 1,
                                                              'pos': (95, 15)}))
        # if we successfully clicked on the moved slider then this button should be True
        assert slider.right_button.held is True
        assert slider.right_button.rect.top == (slider.shadow_width + slider.border_width)
        assert slider.right_button.rect.bottom == 30 - (slider.shadow_width + slider.border_width)
        assert slider.right_button.rect.right == 100 - (slider.shadow_width + slider.border_width)

        slider.set_dimensions((150, 45))

        # try to click on the slider
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': 1,
                                                              'pos': (145, 22)}))
        # if we successfully clicked on the moved slider then this button should be True
        assert slider.right_button.held is True
        assert slider.right_button.rect.top == (slider.shadow_width + slider.border_width)
        assert slider.right_button.rect.bottom == 45 - (slider.shadow_width + slider.border_width)
        assert slider.right_button.rect.right == 150 - (slider.shadow_width + slider.border_width)

    def test_disable(self, _init_pygame: None, default_ui_manager: UIManager,
                     _display_surface_return_none: None):
        slider = UIHorizontalSlider(relative_rect=pygame.Rect(0, 0, 150, 40), start_value=50,
                                    value_range=(0, 200), manager=default_ui_manager)

        slider.disable()

        # process a mouse button down event
        slider.left_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1,
                                                        'pos': slider.left_button.rect.center}))

        slider.update(0.1)

        # process a mouse button up event
        slider.left_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1,
                                                      'pos': slider.left_button.rect.center}))

        assert slider.get_current_value() == 50 and slider.is_enabled is False

    def test_enable(self, _init_pygame: None, default_ui_manager: UIManager,
                    _display_surface_return_none: None):
        slider = UIHorizontalSlider(relative_rect=pygame.Rect(0, 0, 150, 40), start_value=50,
                                    value_range=(0, 200), manager=default_ui_manager)

        slider.disable()

        slider.enable()

        # process a mouse button down event
        slider.left_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1,
                                                        'pos': slider.left_button.rect.center}))

        slider.update(0.1)

        # process a mouse button up event
        slider.left_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1,
                                                      'pos': slider.left_button.rect.center}))

        assert slider.get_current_value() != 50 and slider.is_enabled is True

    def test_ints_in_ints_out(self, _init_pygame: None, default_ui_manager: UIManager,
                              _display_surface_return_none: None):
        slider = UIHorizontalSlider(relative_rect=pygame.Rect(0, 0, 150, 40), start_value=50,
                                    value_range=(0, 200), manager=default_ui_manager)

        assert isinstance(slider.get_current_value(), int)
        # process a mouse button down event
        slider.left_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1,
                                                        'pos': slider.left_button.rect.center}))

        slider.update(0.1)

        # process a mouse button up event
        slider.left_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1,
                                                      'pos': slider.left_button.rect.center}))

        assert isinstance(slider.get_current_value(), int)

    def test_floats_in_floats_out(self, _init_pygame: None, default_ui_manager: UIManager,
                                  _display_surface_return_none: None):
        slider = UIHorizontalSlider(relative_rect=pygame.Rect(0, 0, 150, 40), start_value=25.0,
                                    value_range=(0.0, 200.0), manager=default_ui_manager)

        assert isinstance(slider.get_current_value(), float)
        # process a mouse button down event
        slider.left_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1,
                                                        'pos': slider.left_button.rect.center}))

        slider.update(0.1)

        # process a mouse button up event
        slider.left_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1,
                                                      'pos': slider.left_button.rect.center}))

        assert isinstance(slider.get_current_value(), float)

    def test_show(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        slider = UIHorizontalSlider(relative_rect=pygame.Rect(0, 0, 150, 40), start_value=50,
                                    value_range=(0, 200), manager=default_ui_manager, visible=0)

        assert slider.visible == 0
        assert slider.dirty == 1

        assert slider.sliding_button.visible == 0
        assert slider.button_container.visible == 0
        assert slider.left_button.visible == 0
        assert slider.right_button.visible == 0

        slider.show()

        assert slider.visible == 1
        assert slider.dirty == 2

        assert slider.sliding_button.visible == 1
        assert slider.button_container.visible == 1
        assert slider.left_button.visible == 1
        assert slider.right_button.visible == 1

    def test_hide(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        slider = UIHorizontalSlider(relative_rect=pygame.Rect(0, 0, 150, 40), start_value=50,
                                    value_range=(0, 200), manager=default_ui_manager)

        assert slider.visible == 1
        assert slider.dirty == 2

        assert slider.sliding_button.visible == 1
        assert slider.button_container.visible == 1
        assert slider.left_button.visible == 1
        assert slider.right_button.visible == 1

        slider.hide()

        assert slider.visible == 0
        assert slider.dirty == 1

        assert slider.sliding_button.visible == 0
        assert slider.button_container.visible == 0
        assert slider.left_button.visible == 0
        assert slider.right_button.visible == 0

    def test_show_hide_rendering(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        resolution = (400, 400)
        empty_surface = pygame.Surface(resolution)
        empty_surface.fill(pygame.Color(0, 0, 0))

        surface = empty_surface.copy()
        manager = UIManager(resolution)
        slider = UIHorizontalSlider(relative_rect=pygame.Rect(25, 25, 375, 150), start_value=50,
                                    value_range=(0, 200), manager=manager, visible=0)

        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        slider.show()
        manager.draw_ui(surface)
        assert not compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        slider.hide()
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)
