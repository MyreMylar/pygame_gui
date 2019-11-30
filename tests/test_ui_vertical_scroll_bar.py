import os
import pytest
import pygame

from tests.shared_fixtures import _init_pygame, default_ui_manager, default_display_surface, _display_surface_return_none

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_vertical_scroll_bar import UIVerticalScrollBar


class TestUIVerticalScrollBar:

    def test_creation(self, _init_pygame, default_ui_manager):
        scroll_bar = UIVerticalScrollBar(relative_rect=pygame.Rect(100, 100, 30, 150),
                                         visible_percentage=0.7,
                                         manager=default_ui_manager)
        assert scroll_bar.image is not None

    def test_rebuild(self, _init_pygame, default_ui_manager):
        scroll_bar = UIVerticalScrollBar(relative_rect=pygame.Rect(100, 100, 30, 150),
                                         visible_percentage=0.7,
                                         manager=default_ui_manager)
        scroll_bar.rebuild()
        assert scroll_bar.image is not None

    def test_check_has_moved_recently(self, _init_pygame, default_ui_manager):
        scroll_bar = UIVerticalScrollBar(relative_rect=pygame.Rect(100, 100, 30, 150),
                                         visible_percentage=0.7,
                                         manager=default_ui_manager)

        # move the scroll bar a bit
        scroll_bar.bottom_button.held = True
        scroll_bar.update(0.2)
        assert scroll_bar.check_has_moved_recently() is True

    def test_check_update_buttons(self, _init_pygame, default_ui_manager):
        scroll_bar = UIVerticalScrollBar(relative_rect=pygame.Rect(100, 100, 30, 150),
                                         visible_percentage=0.7,
                                         manager=default_ui_manager)

        # scroll down a bit then up again to exercise update
        scroll_bar.bottom_button.held = True
        scroll_bar.update(0.3)
        scroll_bar.bottom_button.held = False
        scroll_bar.top_button.held = True
        scroll_bar.update(0.3)

        assert scroll_bar.check_has_moved_recently() is True

    def test_check_update_sliding_bar(self, _init_pygame, default_ui_manager):
        scroll_bar = UIVerticalScrollBar(relative_rect=pygame.Rect(0, 0, 30, 150),
                                         visible_percentage=0.7,
                                         manager=default_ui_manager)

        # scroll down a bit then up again to exercise update
        pygame.mouse.set_pos((15, 100))
        scroll_bar.sliding_button.held = True
        scroll_bar.update(0.3)

        assert scroll_bar.grabbed_slider is True

        scroll_bar.sliding_button.held = False
        scroll_bar.update(0.3)

        assert scroll_bar.grabbed_slider is False

    def test_redraw_scroll_bar(self, _init_pygame, default_ui_manager):
        scroll_bar = UIVerticalScrollBar(relative_rect=pygame.Rect(100, 100, 30, 150),
                                         visible_percentage=0.7,
                                         manager=default_ui_manager)
        scroll_bar.redraw_scrollbar()
        assert scroll_bar.sliding_button is not None

    def test_set_visible_percentage(self, _init_pygame, default_ui_manager):
        scroll_bar = UIVerticalScrollBar(relative_rect=pygame.Rect(100, 100, 30, 150),
                                         visible_percentage=0.7,
                                         manager=default_ui_manager)
        scroll_bar.start_percentage = 0.9
        scroll_bar.set_visible_percentage(0.2)
        assert scroll_bar.visible_percentage == 0.2

        scroll_bar.set_visible_percentage(-0.2)
        assert scroll_bar.visible_percentage == 0.0

        scroll_bar.set_visible_percentage(1.9)
        assert scroll_bar.visible_percentage == 1.0

    def test_kill(self, _init_pygame, default_ui_manager):
        scroll_bar = UIVerticalScrollBar(relative_rect=pygame.Rect(100, 100, 30, 150),
                                         visible_percentage=0.7,
                                         manager=default_ui_manager)

        # should kill everything
        scroll_bar.kill()

        assert scroll_bar.alive() is False and scroll_bar.sliding_button.alive() is False

    def test_process_event(self, _init_pygame, default_ui_manager):
        scroll_bar = UIVerticalScrollBar(relative_rect=pygame.Rect(100, 100, 30, 150),
                                         visible_percentage=0.7,
                                         manager=default_ui_manager)
        scroll_bar.select()
        assert scroll_bar.process_event(pygame.event.Event(pygame.MOUSEWHEEL, {'y': 0.5})) is True

        assert scroll_bar.process_event(pygame.event.Event(pygame.MOUSEWHEEL, {'y': -0.5})) is True

        del pygame.MOUSEWHEEL

        scroll_bar.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'y': -0.5}))

        assert pygame.MOUSEWHEEL == -1


    def test_rebuild_from_theme_data_non_default(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_vertical_scroll_bar_non_default.json"))

        scroll_bar = UIVerticalScrollBar(relative_rect=pygame.Rect(100, 100, 30, 150),
                                         visible_percentage=0.1,
                                         manager=manager)
        assert scroll_bar.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    def test_rebuild_from_theme_data_bad_values(self, _init_pygame):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes", "ui_vertical_scroll_bar_bad_values.json"))

        scroll_bar = UIVerticalScrollBar(relative_rect=pygame.Rect(100, 100, 30, 150),
                                         visible_percentage=1.0,
                                         manager=manager)
        assert scroll_bar.image is not None
