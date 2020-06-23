import os
import pytest
import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager
from tests.shared_fixtures import default_display_surface , _display_surface_return_none

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_horizontal_scroll_bar import UIHorizontalScrollBar
from pygame_gui.core.ui_container import UIContainer
from pygame_gui.core.interfaces import IUIManagerInterface

try:
    pygame.MOUSEWHEEL
except AttributeError:
    pygame.MOUSEWHEEL = -1


class TestUIHorizontalScrollBar:

    def test_creation(self, _init_pygame, default_ui_manager,
                      _display_surface_return_none):
        scroll_bar = UIHorizontalScrollBar(relative_rect=pygame.Rect(100, 100, 150, 30),
                                           visible_percentage=0.7,
                                           manager=default_ui_manager)
        assert scroll_bar.image is not None

    def test_rebuild(self, _init_pygame, default_ui_manager,
                     _display_surface_return_none):
        scroll_bar = UIHorizontalScrollBar(relative_rect=pygame.Rect(100, 100, 150, 30),
                                           visible_percentage=0.7,
                                           manager=default_ui_manager)
        scroll_bar.rebuild()
        assert scroll_bar.image is not None

    def test_check_has_moved_recently(self, _init_pygame, default_ui_manager,
                                      _display_surface_return_none):
        scroll_bar = UIHorizontalScrollBar(relative_rect=pygame.Rect(100, 100, 150, 30),
                                           visible_percentage=0.7,
                                           manager=default_ui_manager)

        # move the scroll bar a bit
        scroll_bar.right_button.held = True
        scroll_bar.update(0.2)
        assert scroll_bar.check_has_moved_recently() is True

    def test_check_update_buttons(self, _init_pygame, default_ui_manager,
                                  _display_surface_return_none):
        scroll_bar = UIHorizontalScrollBar(relative_rect=pygame.Rect(100, 100, 150, 30),
                                           visible_percentage=0.7,
                                           manager=default_ui_manager)

        # scroll down a bit then up again to exercise update
        scroll_bar.right_button.held = True
        scroll_bar.update(0.3)
        scroll_bar.right_button.held = False
        scroll_bar.left_button.held = True
        scroll_bar.update(0.3)

        assert scroll_bar.check_has_moved_recently() is True

    def test_check_update_sliding_bar(self, _init_pygame, default_ui_manager,
                                      _display_surface_return_none):
        scroll_bar = UIHorizontalScrollBar(relative_rect=pygame.Rect(0, 0, 150, 30),
                                           visible_percentage=0.7,
                                           manager=default_ui_manager)

        # scroll down a bit then up again to exercise update
        default_ui_manager.mouse_position = (100, 15)
        scroll_bar.sliding_button.held = True
        scroll_bar.update(0.3)

        assert scroll_bar.grabbed_slider is True

        scroll_bar.sliding_button.held = False
        scroll_bar.update(0.3)

        assert scroll_bar.grabbed_slider is False

    def test_redraw_scroll_bar(self, _init_pygame, default_ui_manager,
                               _display_surface_return_none):
        scroll_bar = UIHorizontalScrollBar(relative_rect=pygame.Rect(100, 100, 150, 30),
                                           visible_percentage=0.7,
                                           manager=default_ui_manager)
        scroll_bar.redraw_scrollbar()
        assert scroll_bar.sliding_button is not None

    def test_reset_scroll_position(self, _init_pygame, default_ui_manager,
                                   _display_surface_return_none):
        scroll_bar = UIHorizontalScrollBar(relative_rect=pygame.Rect(100, 100, 150, 30),
                                           visible_percentage=0.7,
                                           manager=default_ui_manager)
        scroll_bar.reset_scroll_position()
        assert scroll_bar.scroll_position == 0.0 and scroll_bar.start_percentage == 0.0

    def test_set_visible_percentage(self, _init_pygame, default_ui_manager,
                                    _display_surface_return_none):
        scroll_bar = UIHorizontalScrollBar(relative_rect=pygame.Rect(100, 100, 150, 30),
                                           visible_percentage=0.7,
                                           manager=default_ui_manager)
        scroll_bar.start_percentage = 0.9
        scroll_bar.set_visible_percentage(0.2)
        assert scroll_bar.visible_percentage == 0.2

        scroll_bar.set_visible_percentage(-0.2)
        assert scroll_bar.visible_percentage == 0.0

        scroll_bar.set_visible_percentage(1.9)
        assert scroll_bar.visible_percentage == 1.0

    def test_kill(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                  _display_surface_return_none):
        scroll_bar = UIHorizontalScrollBar(relative_rect=pygame.Rect(100, 100, 150, 30),
                                           visible_percentage=0.7,
                                           manager=default_ui_manager)

        assert len(default_ui_manager.get_root_container().elements) == 2
        assert len(default_ui_manager.get_sprite_group().sprites()) == 6
        scroll_bar_sprites = [default_ui_manager.get_root_container(),
                              scroll_bar,
                              scroll_bar.button_container,
                              scroll_bar.left_button,
                              scroll_bar.right_button,
                              scroll_bar.sliding_button]
        assert default_ui_manager.get_sprite_group().sprites() == scroll_bar_sprites
        scroll_bar.kill()
        assert len(default_ui_manager.get_root_container().elements) == 0
        assert len(default_ui_manager.get_sprite_group().sprites()) == 1
        empty_sprites = [default_ui_manager.get_root_container()]
        assert default_ui_manager.get_sprite_group().sprites() == empty_sprites

    def test_process_event(self, _init_pygame, default_ui_manager,
                           _display_surface_return_none):
        scroll_bar = UIHorizontalScrollBar(relative_rect=pygame.Rect(100, 100, 150, 30),
                                           visible_percentage=0.7,
                                           manager=default_ui_manager)
        scroll_bar.hovered = True
        assert scroll_bar.process_event(pygame.event.Event(pygame.MOUSEWHEEL, {'x': 0.5})) is True

        assert scroll_bar.process_event(pygame.event.Event(pygame.MOUSEWHEEL, {'x': -0.5})) is True

    def test_rebuild_from_theme_data_non_default(self, _init_pygame,
                                                 _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_horizontal_scroll_bar_non_default.json"))

        scroll_bar = UIHorizontalScrollBar(relative_rect=pygame.Rect(100, 100, 150, 30),
                                           visible_percentage=0.1,
                                           manager=manager)
        assert scroll_bar.image is not None

    def test_rebuild_from_theme_data_no_arrow_buttons(self, _init_pygame,
                                                      _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_horizontal_scroll_bar_no_arrows.json"))

        scroll_bar = UIHorizontalScrollBar(relative_rect=pygame.Rect(100, 100, 150, 30),
                                           visible_percentage=0.1,
                                           manager=manager)

        assert scroll_bar.left_button is None
        assert scroll_bar.right_button is None
        assert scroll_bar.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    def test_rebuild_from_theme_data_bad_values(self, _init_pygame,
                                                _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_horizontal_scroll_bar_bad_values.json"))

        scroll_bar = UIHorizontalScrollBar(relative_rect=pygame.Rect(100, 100, 150, 30),
                                           visible_percentage=1.0,
                                           manager=manager)
        assert scroll_bar.image is not None

    def test_set_position(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        scroll_bar = UIHorizontalScrollBar(relative_rect=pygame.Rect(80, 100, 200, 30),
                                           visible_percentage=0.25, manager=default_ui_manager)

        scroll_bar.set_position((200, 200))

        # try to click on the scroll bar's left button
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': 1, 'pos': (205, 215)}))
        # if we successfully clicked on the moved scroll bar then this button should be True
        assert scroll_bar.left_button.held is True

        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': 1, 'pos': (395, 215)}))
        # if we successfully clicked on the moved scroll bar then this button should be True
        assert scroll_bar.right_button.held is True

        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': 1, 'pos': (250, 215)}))
        # if we successfully clicked on the moved scroll bar then this button should be True
        assert scroll_bar.sliding_button.held is True

    def test_set_relative_position(self, _init_pygame, default_ui_manager,
                                   _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(50, 50, 300, 250),
                                     manager=default_ui_manager)
        scroll_bar = UIHorizontalScrollBar(relative_rect=pygame.Rect(80, 100, 200, 30),
                                           visible_percentage=0.25, manager=default_ui_manager,
                                           container=test_container)

        scroll_bar.set_relative_position((50, 50))

        # try to click on the scroll bar's left button
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': 1, 'pos': (105, 115)}))
        # if we successfully clicked on the moved scroll bar then this button should be True
        assert scroll_bar.left_button.held is True

        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': 1, 'pos': (295, 115)}))
        # if we successfully clicked on the moved scroll bar then this button should be True
        assert scroll_bar.right_button.held is True

        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': 1, 'pos': (150, 115)}))
        # if we successfully clicked on the moved scroll bar then this button should be True
        assert scroll_bar.sliding_button.held is True

    def test_set_dimensions(self, _init_pygame, default_ui_manager,
                            _display_surface_return_none):
        scroll_bar = UIHorizontalScrollBar(relative_rect=pygame.Rect(100, 0, 200, 30),
                                           visible_percentage=0.25, manager=default_ui_manager)

        scroll_bar.set_dimensions((100, 60))

        # try to click on the slider
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': 1, 'pos': (195, 40)}))
        # if we successfully clicked on the moved slider then this button should be True
        assert scroll_bar.right_button.held is True

    def test_disable(self, _init_pygame: None, default_ui_manager: UIManager,
                     _display_surface_return_none: None):
        scroll_bar = UIHorizontalScrollBar(relative_rect=pygame.Rect(0, 0, 200, 30),
                                           visible_percentage=0.25, manager=default_ui_manager)

        scroll_bar.disable()

        # process a mouse button down event
        scroll_bar.right_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                               {'button': 1, 'pos': scroll_bar.right_button.rect.center}))

        scroll_bar.update(0.1)

        # process a mouse button up event
        scroll_bar.right_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP,
                               {'button': 1, 'pos': scroll_bar.right_button.rect.center}))

        assert scroll_bar.scroll_position == 0.0 and scroll_bar.is_enabled is False

    def test_enable(self, _init_pygame: None, default_ui_manager: UIManager,
                    _display_surface_return_none: None):
        scroll_bar = UIHorizontalScrollBar(relative_rect=pygame.Rect(0, 0, 200, 30),
                                           visible_percentage=0.25, manager=default_ui_manager)

        scroll_bar.disable()
        scroll_bar.enable()

        # process a mouse button down event
        scroll_bar.right_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                               {'button': 1, 'pos': scroll_bar.right_button.rect.center}))

        scroll_bar.update(0.1)

        # process a mouse button up event
        scroll_bar.right_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP,
                               {'button': 1, 'pos': scroll_bar.right_button.rect.center}))

        assert scroll_bar.scroll_position != 0.0 and scroll_bar.is_enabled is True

    def test_show(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        scroll_bar = UIHorizontalScrollBar(relative_rect=pygame.Rect(100, 0, 200, 30),
                                           visible_percentage=0.25, manager=default_ui_manager,
                                           visible=0)

        assert scroll_bar.visible == 0

        assert scroll_bar.button_container.visible == 0
        assert scroll_bar.sliding_button.visible == 0
        assert scroll_bar.left_button.visible == 0
        assert scroll_bar.right_button.visible == 0

        scroll_bar.show()

        assert scroll_bar.visible == 1

        assert scroll_bar.button_container.visible == 1
        assert scroll_bar.sliding_button.visible == 1
        assert scroll_bar.left_button.visible == 1
        assert scroll_bar.right_button.visible == 1

    def test_hide(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        scroll_bar = UIHorizontalScrollBar(relative_rect=pygame.Rect(100, 0, 200, 30),
                                           visible_percentage=0.25, manager=default_ui_manager)

        assert scroll_bar.visible == 1

        assert scroll_bar.button_container.visible == 1
        assert scroll_bar.sliding_button.visible == 1
        assert scroll_bar.left_button.visible == 1
        assert scroll_bar.right_button.visible == 1

        scroll_bar.hide()

        assert scroll_bar.visible == 0

        assert scroll_bar.button_container.visible == 0
        assert scroll_bar.sliding_button.visible == 0
        assert scroll_bar.left_button.visible == 0
        assert scroll_bar.right_button.visible == 0
