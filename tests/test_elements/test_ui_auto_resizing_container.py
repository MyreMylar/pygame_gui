import pytest
import pygame

from pygame_gui.elements.ui_auto_resizing_container import UIAutoResizingContainer
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIVerticalScrollBar


class TestUIAutoResizingContainer:
    def test_creation(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        UIAutoResizingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )

    def test_get_container(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        container = UIAutoResizingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )
        assert container.get_container() == container

    def test_add_element(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        container = UIAutoResizingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )

        button = UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50), text="", manager=default_ui_manager
        )
        default_ui_manager.get_root_container().remove_element(button)
        container.add_element(button)
        container.update(0.4)
        assert len(container.elements) == 1

        button_right = UIButton(
            relative_rect=pygame.Rect(300, 50, 50, 50),
            text="",
            manager=default_ui_manager,
        )
        default_ui_manager.get_root_container().remove_element(button_right)
        container.add_element(button_right)
        container.update(0.4)
        assert len(container.elements) == 2

        button_left = UIButton(
            relative_rect=pygame.Rect(-100, 50, 50, 50),
            text="",
            manager=default_ui_manager,
        )
        default_ui_manager.get_root_container().remove_element(button_left)
        container.add_element(button_left)
        container.update(0.4)
        assert len(container.elements) == 3

        button_top = UIButton(
            relative_rect=pygame.Rect(100, -50, 50, 50),
            text="",
            manager=default_ui_manager,
        )
        default_ui_manager.get_root_container().remove_element(button_top)
        container.add_element(button_top)
        container.update(0.4)
        assert len(container.elements) == 4

        button_bottom = UIButton(
            relative_rect=pygame.Rect(100, 400, 50, 50),
            text="",
            manager=default_ui_manager,
        )
        default_ui_manager.get_root_container().remove_element(button_bottom)
        container.add_element(button_bottom)
        container.update(0.4)
        assert len(container.elements) == 5

    def test_remove_element(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        container = UIAutoResizingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )

        button = UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            text="",
            manager=default_ui_manager,
            container=container,
        )

        container.remove_element(button)

        button_right = UIButton(
            relative_rect=pygame.Rect(300, 50, 50, 50),
            text="",
            manager=default_ui_manager,
            container=container,
        )
        container.remove_element(button_right)
        button_left = UIButton(
            relative_rect=pygame.Rect(-100, 50, 50, 50),
            text="",
            manager=default_ui_manager,
            container=container,
        )
        container.remove_element(button_left)
        button_top = UIButton(
            relative_rect=pygame.Rect(100, -50, 50, 50),
            text="",
            manager=default_ui_manager,
            container=container,
        )
        container.remove_element(button_top)
        button_bottom = UIButton(
            relative_rect=pygame.Rect(100, 400, 50, 50),
            text="",
            manager=default_ui_manager,
            container=container,
        )
        container.remove_element(button_bottom)

        container.update(0.4)
        assert len(container.elements) == 0

    def test_recalculate_container_layer_thickness(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        container = UIAutoResizingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )
        UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            text="",
            manager=default_ui_manager,
            container=container,
        )

        container.recalculate_container_layer_thickness()

        assert container.layer_thickness == 2

    def test_change_container_layer(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        container = UIAutoResizingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )

        UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            text="",
            manager=default_ui_manager,
            container=container,
        )
        container.change_layer(2)
        assert container.get_top_layer() == 4

    def test_get_top_layer(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        container = UIAutoResizingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )

        UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            text="",
            manager=default_ui_manager,
            container=container,
        )
        assert container.get_top_layer() == 3

    def test_update_containing_rect_position(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        container = UIAutoResizingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )
        container_2 = UIAutoResizingContainer(
            pygame.Rect(50, 50, 50, 50), manager=default_ui_manager, container=container
        )

        button = UIButton(
            relative_rect=pygame.Rect(20, 20, 30, 20),
            text="X",
            manager=default_ui_manager,
            container=container_2,
        )

        container.set_position((0, 0))

        container_2.update_containing_rect_position()

        assert button.rect.topleft == (70, 70)

    def test_set_position(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        container = UIAutoResizingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )

        container.set_position((50, 50))

        assert container.rect.topleft == (50, 50)

    def test_set_relative_position(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        container = UIAutoResizingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )
        container_2 = UIAutoResizingContainer(
            pygame.Rect(50, 50, 50, 50), manager=default_ui_manager, container=container
        )

        container_2.set_relative_position((25, 25))

        assert container_2.rect.topleft == (125, 125)

    def test_set_dimensions(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        container = UIAutoResizingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )

        container.set_dimensions((50, 50))

        assert container.rect.size == (50, 50)

    def test_kill(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        container = UIAutoResizingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )
        container_2 = UIAutoResizingContainer(
            pygame.Rect(50, 50, 50, 50), manager=default_ui_manager, container=container
        )

        button = UIButton(
            relative_rect=pygame.Rect(20, 20, 30, 20),
            text="X",
            manager=default_ui_manager,
            container=container_2,
        )

        container.kill()

        assert not button.alive()
        assert not container_2.alive()
        assert not container.alive()

    def test_clear(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        container = UIAutoResizingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )
        container_2 = UIAutoResizingContainer(
            pygame.Rect(50, 50, 50, 50), manager=default_ui_manager, container=container
        )

        button = UIButton(
            relative_rect=pygame.Rect(20, 20, 30, 20),
            text="X",
            manager=default_ui_manager,
            container=container_2,
        )

        container.clear()

        assert not button.alive()
        assert not container_2.alive()
        assert len(container.elements) == 0

    def test_check_hover_when_not_able_to_hover(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        container = UIAutoResizingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )
        default_ui_manager.mouse_position = (150, 150)
        assert container.check_hover(0.5, False) is True  # already hovering
        container.kill()
        assert container.check_hover(0.5, False) is False  # dead so can't hover anymore

    def test_resizing_with_anchors(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        container = UIAutoResizingContainer(
            relative_rect=pygame.Rect(0, 0, 300, 300), manager=default_ui_manager
        )

        scroll_bar = UIVerticalScrollBar(
            relative_rect=pygame.Rect(-20, 0, 20, 300),
            visible_percentage=0.5,
            manager=default_ui_manager,
            container=container,
            anchors={
                "left": "right",
                "right": "right",
                "top": "top",
                "bottom": "bottom",
            },
        )

        assert scroll_bar.top_button.rect.width == 14
        container.set_dimensions((400, 400))
        assert scroll_bar.top_button.rect.width == 14

    def test_container_show(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        container = UIAutoResizingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager, visible=0
        )
        assert container.visible == 0
        container.show()
        assert container.visible == 1

    def test_container_hide(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        container = UIAutoResizingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager, visible=1
        )
        assert container.visible == 1
        container.hide()
        assert container.visible == 0

    def test_container_children_inheriting_hidden_status(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        container = UIAutoResizingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager, visible=0
        )
        button = UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            text="",
            manager=default_ui_manager,
            container=container,
            visible=1,
        )
        assert container.visible == 0
        assert button.visible == 0

    def test_hidden_container_children_behaviour_on_show(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        container = UIAutoResizingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager, visible=0
        )
        button = UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            text="",
            manager=default_ui_manager,
            container=container,
        )
        assert container.visible == 0
        assert button.visible == 0
        container.show()
        assert container.visible == 1
        assert button.visible == 1

    def test_visible_container_children_behaviour_on_show(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        container = UIAutoResizingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager, visible=1
        )
        button = UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            text="",
            manager=default_ui_manager,
            container=container,
            visible=0,
        )
        assert container.visible == 1
        assert button.visible == 0
        container.show()
        assert container.visible == 1
        assert button.visible == 0

    def test_visible_container_children_behaviour_on_hide(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        container = UIAutoResizingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager, visible=1
        )
        button = UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            text="",
            manager=default_ui_manager,
            container=container,
        )
        assert container.visible == 1
        assert button.visible == 1
        container.hide()
        assert container.visible == 0
        assert button.visible == 0

    def test_hidden_container_children_behaviour_on_hide(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        container = UIAutoResizingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager, visible=0
        )
        button = UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            text="",
            manager=default_ui_manager,
            container=container,
        )
        button.show()
        assert container.visible == 0
        assert button.visible == 1
        container.hide()
        assert container.visible == 0
        assert button.visible == 1

    def test_auto_resize_on_element_add(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        """Test that the container properly resizes when elements are added at different positions."""
        container = UIAutoResizingContainer(
            pygame.Rect(100, 100, 100, 100), manager=default_ui_manager
        )
        initial_rect = container.get_abs_rect().copy()

        # Add element to the right - should expand right
        right_button = UIButton(
            relative_rect=pygame.Rect(120, 20, 50, 50),
            text="",
            manager=default_ui_manager,
            container=container,
        )
        container.update(0.1)
        expanded_right_rect = container.get_abs_rect()
        assert expanded_right_rect.width > initial_rect.width
        assert expanded_right_rect.right >= right_button.get_abs_rect().right
        assert (
            expanded_right_rect.left == initial_rect.left
        )  # Left edge should not move

        # Add element to the left - should expand left
        left_button = UIButton(
            relative_rect=pygame.Rect(-30, 20, 50, 50),
            text="",
            manager=default_ui_manager,
            container=container,
        )
        container.update(0.1)
        expanded_left_rect = container.get_abs_rect()
        assert expanded_left_rect.left <= left_button.get_abs_rect().left
        assert (
            expanded_left_rect.right == expanded_right_rect.right
        )  # Right edge should not move
        assert (
            expanded_left_rect.width >= expanded_right_rect.width
        )  # Width should be at least as large

        # Add element to the bottom - should expand down
        bottom_button = UIButton(
            relative_rect=pygame.Rect(20, 120, 50, 50),
            text="",
            manager=default_ui_manager,
            container=container,
        )
        container.update(0.1)
        expanded_bottom_rect = container.get_abs_rect()
        assert expanded_bottom_rect.height > initial_rect.height
        assert expanded_bottom_rect.bottom >= bottom_button.get_abs_rect().bottom
        assert (
            expanded_bottom_rect.top == expanded_left_rect.top
        )  # Top edge should not move

        # Add element to the top - should expand up
        top_button = UIButton(
            relative_rect=pygame.Rect(20, -30, 50, 50),
            text="",
            manager=default_ui_manager,
            container=container,
        )
        container.update(0.1)
        final_rect = container.get_abs_rect()
        assert final_rect.top <= top_button.get_abs_rect().top
        assert (
            final_rect.bottom == expanded_bottom_rect.bottom
        )  # Bottom edge should not move
        assert (
            final_rect.height >= expanded_bottom_rect.height
        )  # Height should be at least as large

    def test_auto_resize_on_element_remove(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        """Test that the container properly resizes when elements are removed."""
        container = UIAutoResizingContainer(
            pygame.Rect(100, 100, 100, 100), manager=default_ui_manager
        )

        # Add elements to expand the container
        right_button = UIButton(
            relative_rect=pygame.Rect(120, 20, 50, 50),
            text="right",
            manager=default_ui_manager,
            container=container,
        )
        left_button = UIButton(
            relative_rect=pygame.Rect(-30, 20, 50, 50),
            text="left",
            manager=default_ui_manager,
            container=container,
        )
        bottom_button = UIButton(
            relative_rect=pygame.Rect(20, 120, 50, 50),
            text="bottom",
            manager=default_ui_manager,
            container=container,
        )
        top_button = UIButton(
            relative_rect=pygame.Rect(20, -30, 50, 50),
            text="top",
            manager=default_ui_manager,
            container=container,
        )
        container.update(0.1)
        expanded_rect = container.get_abs_rect().copy()

        # Remove right element - should contract from right
        container.remove_element(right_button)
        container.update(0.1)
        right_removed_rect = container.get_abs_rect()
        assert right_removed_rect.width < expanded_rect.width
        assert (
            right_removed_rect.left == expanded_rect.left
        )  # Left edge should not move

        # Remove left element - should contract from left
        container.remove_element(left_button)
        container.update(0.1)
        left_removed_rect = container.get_abs_rect()
        assert left_removed_rect.left > expanded_rect.left
        assert (
            left_removed_rect.right == right_removed_rect.right
        )  # Right edge should not move

        # Remove bottom element - should contract from bottom
        container.remove_element(bottom_button)
        container.update(0.1)
        bottom_removed_rect = container.get_abs_rect()
        assert bottom_removed_rect.height < expanded_rect.height
        assert bottom_removed_rect.top == expanded_rect.top  # Top edge should not move

        # Remove top element - should contract from top
        container.remove_element(top_button)
        container.update(0.1)
        final_rect = container.get_abs_rect()
        assert final_rect.top > expanded_rect.top
        assert (
            final_rect.bottom == bottom_removed_rect.bottom
        )  # Bottom edge should not move

    def test_min_max_edges_constraints(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        """Test that the container respects min_edges_rect and max_edges_rect constraints during auto-resizing."""
        min_rect = pygame.Rect(100, 100, 100, 100)
        max_rect = pygame.Rect(50, 50, 200, 200)
        container = UIAutoResizingContainer(
            relative_rect=min_rect.copy(),
            min_edges_rect=min_rect,
            max_edges_rect=max_rect,
            manager=default_ui_manager,
        )

        # Test auto-resizing respects constraints
        # Add element that would push beyond max_edges_rect
        far_right_button = UIButton(
            relative_rect=pygame.Rect(220, 20, 50, 50),
            text="",
            manager=default_ui_manager,
            container=container,
        )
        container.update(0.1)
        assert (
            container.get_abs_rect().width == 200
        )  # Should be capped at maximum width

        # Add element that would push beyond min_edges_rect
        far_left_button = UIButton(
            relative_rect=pygame.Rect(-70, 20, 50, 50),
            text="",
            manager=default_ui_manager,
            container=container,
        )
        container.update(0.1)
        assert (
            container.get_abs_rect().left == min_rect.left
        )  # Should not move left beyond minimum

        # Test updating min/max edges rect
        new_min_rect = pygame.Rect(120, 120, 150, 150)
        container.update_min_edges_rect(new_min_rect)
        container.update(0.1)
        assert container.get_abs_rect().size >= (
            150,
            150,
        )  # Should expand to new minimum size

        new_max_rect = pygame.Rect(100, 100, 175, 175)
        container.update_max_edges_rect(new_max_rect)
        container.update(0.1)
        assert container.get_abs_rect().size <= (
            175,
            175,
        )  # Should contract to new maximum size

    def test_manual_dimension_constraints(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        """Test that the container respects min_edges_rect and max_edges_rect constraints when manually setting dimensions."""
        min_rect = pygame.Rect(100, 100, 100, 100)
        max_rect = pygame.Rect(50, 50, 200, 200)
        container = UIAutoResizingContainer(
            relative_rect=min_rect.copy(),
            min_edges_rect=min_rect,
            max_edges_rect=max_rect,
            manager=default_ui_manager,
        )

        # Test minimum size constraint
        container.set_dimensions((50, 50))  # Try to shrink below minimum
        container.update(0.1)
        assert container.get_abs_rect().size >= (
            100,
            100,
        )  # Should not go below minimum size

        # Test maximum size constraint
        container.set_dimensions((250, 250))  # Try to expand beyond maximum
        container.update(0.1)
        assert container.get_abs_rect().size <= (
            200,
            200,
        )  # Should not exceed maximum size


if __name__ == "__main__":
    pytest.console_main()
