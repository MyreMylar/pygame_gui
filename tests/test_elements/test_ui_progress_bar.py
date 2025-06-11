import os
import pytest
import pygame

from tests.shared_comparators import compare_surfaces

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_progress_bar import UIProgressBar


class TestUIProgressBar:
    def test_creation(
        self, _init_pygame, _display_surface_return_none, default_ui_manager
    ):
        progress_bar = UIProgressBar(
            relative_rect=pygame.Rect(100, 100, 150, 30), manager=default_ui_manager
        )
        assert progress_bar.image is not None

    def test_update(
        self, _init_pygame, _display_surface_return_none, default_ui_manager
    ):
        progress_bar = UIProgressBar(
            relative_rect=pygame.Rect(100, 100, 150, 30), manager=default_ui_manager
        )
        progress_bar.current_progress = 50.0
        progress_bar.update(0.01)
        assert (
            progress_bar.image is not None and progress_bar.progress_percentage == 0.5
        )

    def test_set_current_progress(
        self, _init_pygame, _display_surface_return_none, default_ui_manager
    ):
        progress_bar = UIProgressBar(
            relative_rect=pygame.Rect(100, 100, 150, 30), manager=default_ui_manager
        )

        progress_bar.set_current_progress(75)

        assert progress_bar.progress_percentage == 0.75

    def test_status_text(
        self, _init_pygame, _display_surface_return_none, default_ui_manager
    ):
        progress_bar = UIProgressBar(
            relative_rect=pygame.Rect(100, 100, 150, 30), manager=default_ui_manager
        )

        progress_bar.set_current_progress(75)

        assert progress_bar.status_text() == "75.0/100.0"


if __name__ == "__main__":
    pytest.console_main()
