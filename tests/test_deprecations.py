import pygame
import pytest


from pygame_gui.elements.ui_button import UIButton
from pygame_gui._constants import UI_BUTTON_DOUBLE_CLICKED


class TestDeprecations:
    """
    Testing for functionality that gets deprecated
    """

    def test_set_image_deprecation(
        self, _init_pygame, _display_surface_return_none, default_ui_manager
    ):
        """
        Remove this test in version 0.8.0
        """
        button = UIButton(
            relative_rect=pygame.Rect(100, 100, 200, 30),
            text="Test",
            manager=default_ui_manager,
        )

        with pytest.warns(
            DeprecationWarning,
            match="This method will be removed for " "most elements from version 0.8.0",
        ):
            button.set_image(pygame.Surface((64, 64)))

    def test_event_user_type_deprecation(
        self, _init_pygame, _display_surface_return_none, default_ui_manager
    ):
        """
        Remove this test in version 0.8.0
        """
        button = UIButton(
            relative_rect=pygame.Rect(10, 10, 150, 30),
            text="Test Button",
            manager=default_ui_manager,
            allow_double_clicks=True,
        )

        # process a mouse button down event
        button.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": button.rect.center},
            )
        )

        button.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": pygame.BUTTON_LEFT, "pos": button.rect.center},
            )
        )

        with pytest.warns(
            DeprecationWarning,
            match="Pygame GUI event types can now "
            "be used directly as event.type "
            "rather than event.user_type. This old style user_type event will "
            "go away in version 0.8.0",
        ):
            for event in pygame.event.get():
                if (
                    event.type == pygame.USEREVENT
                    and event.user_type == UI_BUTTON_DOUBLE_CLICKED
                ):
                    pass
