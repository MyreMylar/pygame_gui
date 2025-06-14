import pygame
import pytest

from pygame_gui.core.drawable_shapes.rounded_rect_drawable_shape import (
    RoundedRectangleShape,
)
from pygame_gui.ui_manager import UIManager
from pygame_gui.core.colour_gradient import ColourGradient


class TestRoundedRectangleShape:
    def test_creation(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        RoundedRectangleShape(
            containing_rect=pygame.Rect(0, 0, 100, 100),
            theming_parameters={
                "text": "test",
                "font": default_ui_manager.get_theme().get_font([]),
                "normal_text": pygame.Color("#FFFFFF"),
                "normal_text_shadow": pygame.Color("#000000"),
                "shadow_width": 0,
                "border_width": 0,
                "normal_border": pygame.Color("#FFFFFF"),
                "normal_bg": pygame.Color("#000000"),
                "shape_corner_radius": [2, 2, 2, 2],
                "text_horiz_alignment": "center",
                "text_vert_alignment": "center",
            },
            states=["normal"],
            manager=default_ui_manager,
        )

    def test_update(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        shape = RoundedRectangleShape(
            containing_rect=pygame.Rect(0, 0, 100, 100),
            theming_parameters={
                "text": "test",
                "font": default_ui_manager.ui_theme.get_font([]),
                "normal_text": pygame.Color("#FFFFFF"),
                "normal_text_shadow": pygame.Color("#000000"),
                "hovered_text": pygame.Color("#A0A0FF"),
                "hovered_text_shadow": pygame.Color("#000000"),
                "shadow_width": 2,
                "border_width": 1,
                "normal_border": pygame.Color("#FFFFFF"),
                "normal_bg": pygame.Color("#000000"),
                "hovered_border": pygame.Color("#000000"),
                "hovered_bg": pygame.Color("#FFFFFF"),
                "shape_corner_radius": [2, 2, 2, 2],
                "text_horiz_alignment": "center",
                "text_vert_alignment": "center",
            },
            states=["normal", "hovered"],
            manager=default_ui_manager,
        )
        shape.update(0.2)
        shape.update(0.4)

    def test_full_rebuild_on_size_change_negative_values(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        with pytest.warns(UserWarning, match=r"Clamping "):
            RoundedRectangleShape(
                containing_rect=pygame.Rect(0, 0, 100, 100),
                theming_parameters={
                    "text": "test",
                    "font": default_ui_manager.ui_theme.get_font([]),
                    "normal_text": pygame.Color("#FFFFFF"),
                    "normal_text_shadow": pygame.Color("#000000"),
                    "shadow_width": -10,
                    "border_width": -10,
                    "normal_border": pygame.Color("#FFFFFF"),
                    "normal_bg": pygame.Color("#000000"),
                    "shape_corner_radius": [-10, -10, -10, -10],
                    "text_horiz_alignment": "center",
                    "text_vert_alignment": "center",
                },
                states=["normal"],
                manager=default_ui_manager,
            )

    def test_full_rebuild_on_size_change_corner_only_negative_values(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        with pytest.warns(UserWarning, match="Clamping shape_corner_radius"):
            RoundedRectangleShape(
                containing_rect=pygame.Rect(0, 0, 100, 100),
                theming_parameters={
                    "text": "test",
                    "font": default_ui_manager.ui_theme.get_font([]),
                    "normal_text": pygame.Color("#FFFFFF"),
                    "normal_text_shadow": pygame.Color("#000000"),
                    "shadow_width": 2,
                    "border_width": 1,
                    "normal_border": pygame.Color("#FFFFFF"),
                    "normal_bg": pygame.Color("#000000"),
                    "shape_corner_radius": [-10, -10, -10, -10],
                    "text_horiz_alignment": "center",
                    "text_vert_alignment": "center",
                },
                states=["normal"],
                manager=default_ui_manager,
            )

    def test_full_rebuild_on_size_change_large(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        with pytest.warns(UserWarning, match="Clamping "):
            RoundedRectangleShape(
                containing_rect=pygame.Rect(0, 0, 25, 25),
                theming_parameters={
                    "text": "test",
                    "font": default_ui_manager.ui_theme.get_font([]),
                    "normal_text": pygame.Color("#FFFFFF"),
                    "normal_text_shadow": pygame.Color("#000000"),
                    "shadow_width": 20,
                    "border_width": 20,
                    "shape_corner_radius": [20, 20, 20, 20],
                    "normal_border": pygame.Color("#FFFFFF"),
                    "normal_bg": pygame.Color("#000000"),
                    "text_horiz_alignment": "center",
                    "text_vert_alignment": "center",
                },
                states=["normal"],
                manager=default_ui_manager,
            )

    def test_full_rebuild_on_size_change_large_corners_only(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        with pytest.warns(UserWarning, match="Clamping shape_corner_radius"):
            RoundedRectangleShape(
                containing_rect=pygame.Rect(0, 0, 50, 50),
                theming_parameters={
                    "text": "test",
                    "font": default_ui_manager.ui_theme.get_font([]),
                    "normal_text": pygame.Color("#FFFFFF"),
                    "normal_text_shadow": pygame.Color("#000000"),
                    "shadow_width": 1,
                    "border_width": 2,
                    "shape_corner_radius": [30, 30, 30, 30],
                    "normal_border": pygame.Color("#FFFFFF"),
                    "normal_bg": pygame.Color("#000000"),
                    "text_horiz_alignment": "center",
                    "text_vert_alignment": "center",
                },
                states=["normal"],
                manager=default_ui_manager,
            )

    def test_full_rebuild_on_size_change_large_corners_no_shadow(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        RoundedRectangleShape(
            containing_rect=pygame.Rect(0, 0, 50, 50),
            theming_parameters={
                "text": "test",
                "font": default_ui_manager.ui_theme.get_font([]),
                "normal_text": pygame.Color("#FFFFFF"),
                "normal_text_shadow": pygame.Color("#000000"),
                "shadow_width": 0,
                "border_width": 2,
                "shape_corner_radius": [30, 30, 30, 30],
                "normal_border": pygame.Color("#FFFFFF"),
                "normal_bg": pygame.Color("#000000"),
                "text_horiz_alignment": "center",
                "text_vert_alignment": "center",
            },
            states=["normal"],
            manager=default_ui_manager,
        )

    def test_full_rebuild_on_size_change_small_surface(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        with pytest.warns(UserWarning, match="Clamping shape_corner_radius"):
            theming_params = {
                "text": "test",
                "font": default_ui_manager.ui_theme.get_font([]),
                "normal_text": pygame.Color("#FFFFFF"),
                "normal_text_shadow": pygame.Color("#000000"),
                "shadow_width": 1,
                "border_width": 0,
                "shape_corner_radius": [3, 3, 3, 3],
                "normal_border": pygame.Color("#FFFFFF"),
                "normal_bg": pygame.Color("#000000"),
                "text_horiz_alignment": "center",
                "text_vert_alignment": "center",
            }
            RoundedRectangleShape(
                containing_rect=pygame.Rect(0, 0, 2, 2),
                theming_parameters=theming_params,
                states=["normal"],
                manager=default_ui_manager,
            )

    def test_collide_point(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        theming_params = {
            "text": "test",
            "font": default_ui_manager.ui_theme.get_font([]),
            "normal_text": pygame.Color("#FFFFFF"),
            "normal_text_shadow": pygame.Color("#000000"),
            "shadow_width": 0,
            "border_width": 0,
            "shape_corner_radius": [40, 40, 40, 40],
            "normal_border": pygame.Color("#FFFFFF"),
            "normal_bg": pygame.Color("#000000"),
            "text_horiz_alignment": "center",
            "text_vert_alignment": "center",
        }
        shape = RoundedRectangleShape(
            containing_rect=pygame.Rect(0, 0, 100, 100),
            theming_parameters=theming_params,
            states=["normal"],
            manager=default_ui_manager,
        )
        assert shape.collide_point((50, 50)) is True
        assert shape.collide_point((5, 50)) is True
        assert shape.collide_point((25, 25)) is True
        assert shape.collide_point((10, 10)) is False
        assert shape.collide_point((5, 5)) is False

    def test_set_position(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        shape = RoundedRectangleShape(
            containing_rect=pygame.Rect(0, 0, 100, 100),
            theming_parameters={
                "text": "test",
                "font": default_ui_manager.ui_theme.get_font([]),
                "normal_text": pygame.Color("#FFFFFF"),
                "normal_text_shadow": pygame.Color("#000000"),
                "shadow_width": 0,
                "border_width": 0,
                "shape_corner_radius": [2, 2, 2, 2],
                "normal_border": pygame.Color("#FFFFFF"),
                "normal_bg": pygame.Color("#000000"),
                "text_horiz_alignment": "center",
                "text_vert_alignment": "center",
            },
            states=["normal"],
            manager=default_ui_manager,
        )
        shape.set_position((50, 50))

    def test_set_dimensions(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        shape = RoundedRectangleShape(
            containing_rect=pygame.Rect(0, 0, 100, 100),
            theming_parameters={
                "text": "test",
                "font": default_ui_manager.ui_theme.get_font([]),
                "normal_text": pygame.Color("#FFFFFF"),
                "normal_text_shadow": pygame.Color("#000000"),
                "shadow_width": 0,
                "border_width": 0,
                "shape_corner_radius": [2, 2, 2, 2],
                "normal_border": pygame.Color("#FFFFFF"),
                "normal_bg": pygame.Color("#000000"),
                "text_horiz_alignment": "center",
                "text_vert_alignment": "center",
            },
            states=["normal"],
            manager=default_ui_manager,
        )
        shape.set_dimensions((50, 50))

    def test_creation_with_gradients(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        RoundedRectangleShape(
            containing_rect=pygame.Rect(0, 0, 100, 100),
            theming_parameters={
                "text": "test",
                "font": default_ui_manager.get_theme().get_font([]),
                "normal_text": pygame.Color("#FFFFFF"),
                "normal_text_shadow": pygame.Color("#000000"),
                "shadow_width": 0,
                "border_width": 0,
                "normal_border": ColourGradient(
                    0, pygame.Color("#000000"), pygame.Color("#FFFFFF")
                ),
                "normal_bg": ColourGradient(
                    0, pygame.Color("#000000"), pygame.Color("#FFFFFF")
                ),
                "shape_corner_radius": [2, 2, 2, 2],
                "text_horiz_alignment": "center",
                "text_vert_alignment": "center",
            },
            states=["normal"],
            manager=default_ui_manager,
        )

    def test_creation_with_filled_bar(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        RoundedRectangleShape(
            containing_rect=pygame.Rect(0, 0, 100, 100),
            theming_parameters={
                "text": "test",
                "font": default_ui_manager.get_theme().get_font([]),
                "normal_text": pygame.Color("#FFFFFF"),
                "normal_text_shadow": pygame.Color("#000000"),
                "shadow_width": 2,
                "border_width": 1,
                "normal_border": ColourGradient(
                    0, pygame.Color("#000000"), pygame.Color("#FFFFFF")
                ),
                "normal_bg": ColourGradient(
                    0, pygame.Color("#000000"), pygame.Color("#FFFFFF")
                ),
                "filled_bar": ColourGradient(
                    0, pygame.Color("#000000"), pygame.Color("#FFFFFF")
                ),
                "filled_bar_width": 50,
                "shape_corner_radius": [2, 2, 2, 2],
                "text_horiz_alignment": "center",
                "text_vert_alignment": "center",
            },
            states=["normal"],
            manager=default_ui_manager,
        )

    def test_creation_with_filled_bar_no_gradient(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        RoundedRectangleShape(
            containing_rect=pygame.Rect(0, 0, 100, 100),
            theming_parameters={
                "text": "test",
                "font": default_ui_manager.get_theme().get_font([]),
                "normal_text": pygame.Color("#FFFFFF"),
                "normal_text_shadow": pygame.Color("#000000"),
                "shadow_width": 2,
                "border_width": 1,
                "normal_border": ColourGradient(
                    0, pygame.Color("#000000"), pygame.Color("#FFFFFF")
                ),
                "normal_bg": ColourGradient(
                    0, pygame.Color("#000000"), pygame.Color("#FFFFFF")
                ),
                "filled_bar": pygame.Color("#000000"),
                "filled_bar_width": 50,
                "shape_corner_radius": [2, 2, 2, 2],
                "text_horiz_alignment": "center",
                "text_vert_alignment": "center",
            },
            states=["normal"],
            manager=default_ui_manager,
        )

    def test_creation_with_filled_bar_no_gradients_at_all(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        RoundedRectangleShape(
            containing_rect=pygame.Rect(0, 0, 100, 100),
            theming_parameters={
                "text": "test",
                "font": default_ui_manager.get_theme().get_font([]),
                "normal_text": pygame.Color("#FFFFFF"),
                "normal_text_shadow": pygame.Color("#000000"),
                "shadow_width": 2,
                "border_width": 1,
                "normal_border": pygame.Color("#FFFFFF"),
                "normal_bg": pygame.Color("#FFFFFF"),
                "filled_bar": pygame.Color("#000000"),
                "filled_bar_width": 50,
                "shape_corner_radius": [2, 2, 2, 2],
                "text_horiz_alignment": "center",
                "text_vert_alignment": "center",
            },
            states=["normal"],
            manager=default_ui_manager,
        )

    def test_clear_and_create_shape_surface(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        shape = RoundedRectangleShape(
            containing_rect=pygame.Rect(0, 0, 100, 100),
            theming_parameters={
                "text": "test",
                "font": default_ui_manager.ui_theme.get_font([]),
                "normal_text": pygame.Color("#FFFFFF"),
                "normal_text_shadow": pygame.Color("#000000"),
                "shadow_width": 0,
                "border_width": 0,
                "shape_corner_radius": [2, 2, 2, 2],
                "normal_border": pygame.Color("#FFFFFF"),
                "normal_bg": pygame.Color("#000000"),
                "text_horiz_alignment": "center",
                "text_vert_alignment": "center",
            },
            states=["normal"],
            manager=default_ui_manager,
        )
        shape.clear_and_create_shape_surface(
            pygame.Surface((100, 100)),
            pygame.Rect(0, 0, 90, 90),
            overlap=0,
            corner_radii=[-1, -1, -1, -1],
            aa_amount=4,
        )

        shape.clear_and_create_shape_surface(
            pygame.Surface((100, 100)),
            pygame.Rect(0, 0, 90, 90),
            overlap=0,
            corner_radii=[50, 50, 50, 50],
            aa_amount=4,
        )

        shape.clear_and_create_shape_surface(
            pygame.Surface((100, 100)),
            pygame.Rect(0, 0, 80, 80),
            overlap=0,
            corner_radii=[40, 40, 40, 40],
            aa_amount=4,
        )

        shape.clear_and_create_shape_surface(
            pygame.Surface((100, 100)),
            pygame.Rect(0, 0, 75, 75),
            overlap=0,
            corner_radii=[40, 40, 40, 40],
            aa_amount=4,
        )

    def test_redraw_state(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        shape = RoundedRectangleShape(
            containing_rect=pygame.Rect(0, 0, 100, 100),
            theming_parameters={
                "text": "test",
                "font": default_ui_manager.ui_theme.get_font([]),
                "normal_text": pygame.Color("#FFFFFF"),
                "normal_text_shadow": pygame.Color("#000000"),
                "hovered_text": pygame.Color("#A0A0FF"),
                "hovered_text_shadow": pygame.Color("#000000"),
                "shadow_width": 2,
                "border_width": 1,
                "normal_border": pygame.Color("#FFFFFF"),
                "normal_bg": pygame.Color("#000000"),
                "hovered_border": pygame.Color("#000000"),
                "hovered_bg": pygame.Color("#FFFFFF"),
                "shape_corner_radius": [2, 2, 2, 2],
                "text_horiz_alignment": "center",
                "text_vert_alignment": "center",
            },
            states=["normal", "hovered"],
            manager=default_ui_manager,
        )

        shape.redraw_state("hovered")
        shape.shadow_width = 3
        shape.redraw_state("hovered")

    def test_clear_and_create_shape_surface_double_call(
        self, _init_pygame, _display_surface_return_none, default_ui_manager: UIManager
    ):
        shape = RoundedRectangleShape(
            containing_rect=pygame.Rect(0, 0, 100, 100),
            theming_parameters={
                "text": "test",
                "font": default_ui_manager.ui_theme.get_font([]),
                "normal_text": pygame.Color("#FFFFFF"),
                "normal_text_shadow": pygame.Color("#000000"),
                "hovered_text": pygame.Color("#A0A0FF"),
                "hovered_text_shadow": pygame.Color("#000000"),
                "shadow_width": 2,
                "border_width": 1,
                "normal_border": pygame.Color("#FFFFFF"),
                "normal_bg": pygame.Color("#000000"),
                "hovered_border": pygame.Color("#000000"),
                "hovered_bg": pygame.Color("#FFFFFF"),
                "shape_corner_radius": [2, 2, 2, 2],
                "text_horiz_alignment": "center",
                "text_vert_alignment": "center",
            },
            states=["normal", "hovered"],
            manager=default_ui_manager,
        )

        bab_surface = pygame.surface.Surface(
            (shape.containing_rect.width * 2, shape.containing_rect.height * 2),
            flags=pygame.SRCALPHA,
            depth=32,
        )

        shape.clear_and_create_shape_surface(
            bab_surface, shape.background_rect, 0, [2, 2, 2, 2], aa_amount=2, clear=True
        )

        shape.clear_and_create_shape_surface(
            bab_surface, shape.background_rect, 0, [2, 2, 2, 2], aa_amount=2, clear=True
        )


if __name__ == "__main__":
    pytest.console_main()
