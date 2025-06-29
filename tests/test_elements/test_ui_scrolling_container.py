import pytest
import pygame

from tests.shared_comparators import compare_surfaces

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_scrolling_container import UIScrollingContainer
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.core.interfaces import IUIManagerInterface


class TestUIScrollingContainer:
    def test_creation(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        UIScrollingContainer(
            relative_rect=pygame.Rect(100, 100, 400, 400), manager=default_ui_manager
        )

    def test_get_container(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        container = UIScrollingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )
        assert container.get_container() == container.scrollable_container

    def test_add_element(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        container = UIScrollingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )

        button = UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50), text="", manager=default_ui_manager
        )
        default_ui_manager.get_root_container().remove_element(button)
        container.get_container().add_element(button)
        assert len(container.get_container().elements) == 1

    def test_remove_element(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        container = UIScrollingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )

        button = UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            text="",
            manager=default_ui_manager,
            container=container,
        )

        container.get_container().remove_element(button)
        assert len(container.get_container().elements) == 0

    def test_set_position(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        container = UIScrollingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )

        container.set_position((50, 50))

        assert container.rect.topleft == (50, 50)
        assert container._root_container.rect.size == (200, 200)

    def test_set_relative_position(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        container = UIScrollingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )
        container_2 = UIScrollingContainer(
            pygame.Rect(50, 50, 50, 50), manager=default_ui_manager, container=container
        )

        container_2.set_relative_position((25, 25))

        assert container_2.rect.topleft == (125, 125)

    def test_set_dimensions(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        container = UIScrollingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )

        container.set_dimensions((50, 50))

        assert container.rect.size == (50, 50)

        container.set_scrollable_area_dimensions((500, 600))

        container.set_dimensions((400, 500))

        assert container.rect.size == (400, 500)

        container.set_dimensions((500, 600))

        assert container.rect.size == (500, 600)

    def test_kill(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        container = UIScrollingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )
        container_2 = UIScrollingContainer(
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

    def test_set_scrollable_area_dimensions(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        container = UIScrollingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )

        container.set_scrollable_area_dimensions((500, 600))

        assert container.vert_scroll_bar is not None
        assert container.horiz_scroll_bar is not None
        assert container.scrollable_container.rect.size == (500, 600)
        assert container._view_container.rect.size == (
            200 - container.vert_scroll_bar.rect.width,
            200 - container.horiz_scroll_bar.rect.height,
        )

    def test_set_scrollable_area_dimensions_constrained_x_axis(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        container = UIScrollingContainer(
            pygame.Rect(100, 100, 200, 200),
            manager=default_ui_manager,
            allow_scroll_x=False,
        )

        assert container.vert_scroll_bar is not None
        assert container.vert_scroll_bar.rect.width == 0
        assert not container.horiz_scroll_bar.is_enabled
        assert container.scrollable_container.rect.size == (200, 200)

        container.set_scrollable_area_dimensions((200, 600))

        assert container.vert_scroll_bar is not None
        assert container.vert_scroll_bar.rect.width != 0
        assert not container.horiz_scroll_bar.is_enabled
        assert container._view_container.rect.size == (
            200 - container.vert_scroll_bar.rect.width,
            200,
        )
        assert container.scrollable_container.rect.size == (
            200 - container.vert_scroll_bar.rect.width,
            600,
        )

    def test_set_scrollable_area_dimensions_constrained_y_axis(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        container = UIScrollingContainer(
            pygame.Rect(100, 100, 200, 200),
            manager=default_ui_manager,
            allow_scroll_y=False,
        )

        assert not container.vert_scroll_bar.is_enabled
        assert container.horiz_scroll_bar is not None
        assert container.horiz_scroll_bar.rect.height == 0
        assert container.scrollable_container.rect.size == (200, 200)

        container.set_scrollable_area_dimensions((600, 200))

        assert not container.vert_scroll_bar.is_enabled
        assert container.horiz_scroll_bar is not None
        assert container.horiz_scroll_bar.rect.height != 0
        assert container._view_container.rect.size == (
            200,
            200 - container.horiz_scroll_bar.rect.height,
        )
        assert container.scrollable_container.rect.size == (
            600,
            200 - container.horiz_scroll_bar.rect.height,
        )

    def test_update(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        container = UIScrollingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )

        container.set_scrollable_area_dimensions((500, 600))

        container.horiz_scroll_bar.scroll_wheel_moved = True
        container.horiz_scroll_bar.scroll_wheel_amount = -1.0
        container.horiz_scroll_bar.update(0.02)

        container.update(0.02)

        print(
            "horiz_scroll_wheel_amount:", container.horiz_scroll_bar.scroll_wheel_amount
        )
        print(
            "horiz_visible_percentage:", container.horiz_scroll_bar.visible_percentage
        )
        print("horiz_scroll_position:", container.get_container().get_relative_rect().x)

        assert container.get_container().get_relative_rect().x == -15

        container.vert_scroll_bar.scroll_wheel_moved = True
        container.vert_scroll_bar.scroll_wheel_amount = -1.0
        container.vert_scroll_bar.update(0.02)

        container.update(0.02)

        assert container.get_container().get_relative_rect().y == -11

        container.horiz_scroll_bar.scroll_wheel_moved = True
        container.horiz_scroll_bar.scroll_wheel_amount = -5.0
        container.horiz_scroll_bar.update(0.02)
        container.horiz_scroll_bar.start_percentage = 0.6
        container.update(0.02)
        container.horiz_scroll_bar.scroll_wheel_moved = True
        container.horiz_scroll_bar.scroll_wheel_amount = -5.0
        container.horiz_scroll_bar.update(0.02)
        container.update(0.02)
        container.horiz_scroll_bar.scroll_wheel_moved = True
        container.horiz_scroll_bar.scroll_wheel_amount = -5.0
        container.horiz_scroll_bar.update(0.02)
        container.scrolling_right = container._view_container.rect.right - 1
        container.update(0.02)

        container.horiz_scroll_bar.scroll_wheel_moved = True
        container.horiz_scroll_bar.scroll_wheel_amount = 5.0
        container.horiz_scroll_bar.update(0.02)
        container.update(0.02)
        container.horiz_scroll_bar.scroll_wheel_moved = True
        container.horiz_scroll_bar.scroll_wheel_amount = 5.0
        container.horiz_scroll_bar.update(0.02)
        container.update(0.02)
        container.horiz_scroll_bar.scroll_wheel_moved = True
        container.horiz_scroll_bar.scroll_wheel_amount = 5.0
        container.horiz_scroll_bar.update(0.02)
        container.update(0.02)

        container.scrollable_container.set_dimensions((150, 600))
        container.horiz_scroll_bar.scroll_wheel_moved = True
        container.horiz_scroll_bar.scroll_wheel_amount = 5.0
        container.horiz_scroll_bar.update(0.02)
        container.update(0.02)

        container.vert_scroll_bar.scroll_wheel_moved = True
        container.vert_scroll_bar.scroll_wheel_amount = -5.0
        container.vert_scroll_bar.update(0.02)
        container.update(0.02)
        container.vert_scroll_bar.scroll_wheel_moved = True
        container.vert_scroll_bar.scroll_wheel_amount = -5.0
        container.vert_scroll_bar.update(0.02)
        container.update(0.02)
        container.vert_scroll_bar.scroll_wheel_moved = True
        container.vert_scroll_bar.scroll_wheel_amount = -5.0
        container.vert_scroll_bar.update(0.02)
        container.update(0.02)

        container.vert_scroll_bar.scroll_wheel_moved = True
        container.vert_scroll_bar.scroll_wheel_amount = 5.0
        container.vert_scroll_bar.update(0.02)
        container.update(0.02)
        container.vert_scroll_bar.scroll_wheel_moved = True
        container.vert_scroll_bar.scroll_wheel_amount = 5.0
        container.vert_scroll_bar.update(0.02)
        container.update(0.02)
        container.vert_scroll_bar.scroll_wheel_moved = True
        container.vert_scroll_bar.scroll_wheel_amount = 5.0
        container.vert_scroll_bar.update(0.02)
        container.update(0.02)

        container.scrollable_container.set_dimensions((150, 150))

        container.update(0.02)
        container.update(0.02)
        container.update(0.02)

        container = UIScrollingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )

        container.set_scrollable_area_dimensions((500, 600))

        container.vert_scroll_bar.scroll_wheel_moved = True
        container.vert_scroll_bar.scroll_wheel_amount = 5.0
        container.vert_scroll_bar.update(0.02)

        container.scrollable_container.rect.top = (
            -500
        )  # scroll it too high and then update
        container.update(0.02)

    def test_disable(
        self,
        _init_pygame: None,
        default_ui_manager: UIManager,
        _display_surface_return_none: None,
    ):
        container = UIScrollingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )
        button_1 = UIButton(
            relative_rect=pygame.Rect(10, 10, 150, 30),
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            container=container,
        )

        button_2 = UIButton(
            relative_rect=pygame.Rect(10, 50, 150, 30),
            text="Test Button 2",
            manager=default_ui_manager,
            container=container,
        )

        container.disable()

        assert container.is_enabled is False
        assert button_1.is_enabled is False
        assert button_2.is_enabled is False

        # process a mouse button down event
        button_1.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": button_1.rect.center}
            )
        )

        # process a mouse button up event
        button_1.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONUP, {"button": 1, "pos": button_1.rect.center}
            )
        )

        button_1.update(0.01)

        assert button_1.check_pressed() is False

    def test_enable(
        self,
        _init_pygame: None,
        default_ui_manager: UIManager,
        _display_surface_return_none: None,
    ):
        container = UIScrollingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )
        button_1 = UIButton(
            relative_rect=pygame.Rect(10, 10, 150, 30),
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            container=container,
        )

        button_2 = UIButton(
            relative_rect=pygame.Rect(10, 50, 150, 30),
            text="Test Button 2",
            manager=default_ui_manager,
            container=container,
        )

        container.disable()
        container.enable()

        assert container.is_enabled is True
        assert button_1.is_enabled is True
        assert button_2.is_enabled is True

        # process a mouse button down event
        button_1.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": button_1.rect.center}
            )
        )

        # process a mouse button up event
        button_1.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONUP, {"button": 1, "pos": button_1.rect.center}
            )
        )

        button_1.update(0.01)

        assert button_1.check_pressed() is True

    def test_show(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        container = UIScrollingContainer(
            relative_rect=pygame.Rect(100, 100, 400, 400),
            manager=default_ui_manager,
            visible=0,
        )
        container.set_scrollable_area_dimensions((500, 600))

        assert container.visible == 0

        assert container._root_container.visible == 0
        assert container._view_container.visible == 0
        assert container.horiz_scroll_bar.visible == 0
        assert container.vert_scroll_bar.visible == 0
        assert container.scrollable_container.visible == 0

        container.show()

        assert container.visible == 1

        assert container._root_container.visible == 1
        assert container._view_container.visible == 1
        assert container.horiz_scroll_bar.visible == 1
        assert container.vert_scroll_bar.visible == 1
        assert container.scrollable_container.visible == 1

    def test_hide(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        container = UIScrollingContainer(
            relative_rect=pygame.Rect(100, 100, 400, 400), manager=default_ui_manager
        )
        container.set_scrollable_area_dimensions((500, 600))

        assert container.visible == 1

        assert container._root_container.visible == 1
        assert container._view_container.visible == 1
        assert container.horiz_scroll_bar.visible == 1
        assert container.vert_scroll_bar.visible == 1
        assert container.scrollable_container.visible == 1

        container.hide()

        assert container.visible == 0

        assert container._root_container.visible == 0
        assert container._view_container.visible == 0
        assert container.horiz_scroll_bar.visible == 0
        assert container.vert_scroll_bar.visible == 0
        assert container.scrollable_container.visible == 0

    def test_show_hide_rendering(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        resolution = (400, 400)
        empty_surface = pygame.Surface(resolution)
        empty_surface.fill(pygame.Color(0, 0, 0))

        surface = empty_surface.copy()
        manager = UIManager(resolution)

        container = UIScrollingContainer(
            relative_rect=pygame.Rect(100, 100, 200, 100),
            manager=manager,
            visible=0,
            should_grow_automatically=True,
        )
        button_1 = UIButton(
            relative_rect=pygame.Rect(300, 100, 150, 30),
            text="Test Button",
            tool_tip_text="This is a test of the button's tool tip functionality.",
            manager=default_ui_manager,
            container=container,
        )
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        container.show()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert not compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        container.hide()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

    def test_iteration(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        container = UIScrollingContainer(
            pygame.Rect(100, 100, 200, 200), manager=default_ui_manager
        )
        button_1 = UIButton(
            relative_rect=pygame.Rect(50, 50, 50, 50),
            text="1",
            manager=default_ui_manager,
            container=container,
        )
        button_2 = UIButton(
            relative_rect=pygame.Rect(150, 50, 50, 50),
            text="2",
            manager=default_ui_manager,
            container=container,
        )

        assert button_1 in container
        assert button_2 in container
        count = 0
        for button in container:
            button.get_relative_rect()
            count += 1
        assert count == 2

    def test_are_contents_hovered(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        manager = UIManager((800, 600))
        container = UIScrollingContainer(
            pygame.Rect(100, 100, 200, 200), manager=manager
        )
        container.set_scrollable_area_dimensions((400, 400))
        button_1 = UIButton(
            relative_rect=pygame.Rect(50, 50, 50, 50),
            text="1",
            manager=manager,
            container=container,
        )
        button_2 = UIButton(
            relative_rect=pygame.Rect(50, 300, 50, 50),
            text="2",
            manager=manager,
            container=container,
        )
        manager.mouse_position = (155, 155)
        button_1.check_hover(0.1, False)
        button_2.check_hover(0.1, False)

        assert container.are_contents_hovered()
        assert container.vert_scroll_bar is not None

        container.vert_scroll_bar.process_event(
            pygame.event.Event(pygame.MOUSEWHEEL, {"y": -0.5, "x": 0.0})
        )

        assert container.vert_scroll_bar.scroll_wheel_moved

        assert container.horiz_scroll_bar is not None

        container.horiz_scroll_bar.process_event(
            pygame.event.Event(pygame.MOUSEWHEEL, {"x": -0.5, "y": 0.0})
        )

        assert container.horiz_scroll_bar.scroll_wheel_moved

    def test_scrolls_while_hovering_non_scrolling_contents(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        manager = UIManager((800, 600))
        container = UIScrollingContainer(
            pygame.Rect(100, 100, 250, 300), manager=manager
        )
        container.set_scrollable_area_dimensions((250, 600))

        text_box_inside_scrolling_container = UITextBox(
            html_text="Some text inside a text box, itself"
            " inside a container that scrolls",
            relative_rect=pygame.Rect(20, 20, 150, 200),
            container=container,
            manager=manager,
        )
        manager.mouse_position = text_box_inside_scrolling_container.rect.center
        text_box_inside_scrolling_container.check_hover(0.1, False)

        assert container.are_contents_hovered()
        assert container.vert_scroll_bar is not None

        manager.process_events(
            pygame.event.Event(pygame.MOUSEWHEEL, {"y": -0.5, "x": 0.0})
        )

        assert container.vert_scroll_bar.scroll_wheel_moved

    def test_does_not_scroll_while_hovering_scrolling_contents(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        manager = UIManager((800, 600))
        container = UIScrollingContainer(
            pygame.Rect(100, 100, 250, 300), manager=manager
        )
        container.set_scrollable_area_dimensions((250, 600))

        text_box_inside_scrolling_container = UITextBox(
            html_text="Some text inside a scrolling text box, itself"
            " inside a container that scrolls. "
            "scrolling should work correctly with the mousewheel, "
            "depending on whether we are hovering this text box, or"
            " whether we are hovering other stuff in the "
            "scrolling container",
            relative_rect=pygame.Rect(20, 20, 180, 200),
            container=container,
            manager=manager,
        )
        manager.mouse_position = text_box_inside_scrolling_container.rect.center
        text_box_inside_scrolling_container.check_hover(0.1, False)

        assert container.are_contents_hovered()
        assert container.vert_scroll_bar is not None

        manager.process_events(
            pygame.event.Event(pygame.MOUSEWHEEL, {"y": -0.5, "x": 0.0})
        )

        assert not container.vert_scroll_bar.scroll_wheel_moved

    def test_scroll_while_hovering_nested_contents(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        manager = UIManager((800, 600))
        container = UIScrollingContainer(
            pygame.Rect(100, 100, 250, 300), manager=manager
        )
        container.set_scrollable_area_dimensions((250, 600))

        container_2 = UIScrollingContainer(
            pygame.Rect(10, 10, 230, 280),
            manager=manager,
            container=container,
            should_grow_automatically=False,
        )

        text_box_inside_two_scrolling_containers = UITextBox(
            html_text="Some text",
            relative_rect=pygame.Rect(10, 10, 210, 260),
            container=container_2,
            manager=manager,
        )
        manager.mouse_position = text_box_inside_two_scrolling_containers.rect.center
        text_box_inside_two_scrolling_containers.check_hover(0.1, False)

        assert container.are_contents_hovered()
        assert container.vert_scroll_bar is not None

        manager.process_events(
            pygame.event.Event(pygame.MOUSEWHEEL, {"y": -0.5, "x": 0.0})
        )

        assert container.vert_scroll_bar.scroll_wheel_moved

    def test_set_anchors(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        panel = UIScrollingContainer(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            manager=default_ui_manager,
            anchors={"left": "left", "right": "left", "top": "top", "bottom": "top"},
        )
        panel.set_anchors(
            anchors={"left": "right", "right": "right", "top": "top", "bottom": "top"}
        )
        assert panel.get_anchors()["left"] == "right"
        assert panel.get_anchors()["right"] == "right"

    def test_vertical_scroll_only_when_needed(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        """Test that vertical scroll bar only appears when content exceeds container height"""
        container = UIScrollingContainer(
            pygame.Rect(100, 100, 200, 200),
            manager=default_ui_manager,
            should_grow_automatically=True,
            allow_scroll_x=False,  # Disable horizontal scrolling
        )

        # Add content that exceeds container height but not width
        UIButton(
            relative_rect=pygame.Rect(10, 400, 100, 50),  # Height > container height
            text="Test Button",
            manager=default_ui_manager,
            container=container,
        )

        default_ui_manager.update(0.1)
        default_ui_manager.update(0.1)

        # Check that vertical scroll bar has width but that the horizontal scroll bar has no height
        assert container.vert_scroll_bar.rect.width == container.scroll_bar_width
        assert container.horiz_scroll_bar.rect.height == 0
        assert container.horiz_scroll_bar.is_enabled is False
        assert container.scrollable_container.rect.height > container.rect.height

    def test_no_unnecessary_horizontal_scroll(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        """Test that horizontal scroll bar doesn't appear when content fits width"""
        container = UIScrollingContainer(
            pygame.Rect(100, 100, 200, 200),
            manager=default_ui_manager,
            should_grow_automatically=True,
        )

        # Add content that fits within container width
        UIButton(
            relative_rect=pygame.Rect(10, 400, 100, 30),  # Width < container width
            text="Test Button",
            manager=default_ui_manager,
            container=container,
        )

        # Check that horizontal scroll bar doesn't exist (width should be 0)
        assert container.horiz_scroll_bar.rect.height == 0
        assert container.scrollable_container.rect.width <= container.rect.width

    def test_scroll_container_dimensions_stable(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        """Test that container dimensions remain stable during scrolling"""
        container = UIScrollingContainer(
            pygame.Rect(100, 100, 200, 200),
            manager=default_ui_manager,
            should_grow_automatically=True,
        )

        # Add content that exceeds container height
        button = UIButton(
            relative_rect=pygame.Rect(10, 10, 150, 300),
            text="Test Button",
            manager=default_ui_manager,
            container=container,
        )

        initial_scrollable_height = container.scrollable_container.rect.height
        initial_scrollable_width = container.scrollable_container.rect.width

        # Simulate scrolling down
        container.vert_scroll_bar.scroll_wheel_moved = True
        container.vert_scroll_bar.scroll_wheel_amount = -1.0
        container.vert_scroll_bar.update(0.02)
        container.update(0.02)

        # Check dimensions haven't changed
        assert container.scrollable_container.rect.height == initial_scrollable_height
        assert container.scrollable_container.rect.width == initial_scrollable_width

        # Scroll to bottom
        container.vert_scroll_bar.start_percentage = 1.0
        container.update(0.02)

        # Check dimensions still haven't changed
        assert container.scrollable_container.rect.height == initial_scrollable_height
        assert container.scrollable_container.rect.width == initial_scrollable_width

    def test_scroll_container_content_position(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        """Test that content position is correctly maintained during scrolling"""
        container = UIScrollingContainer(
            pygame.Rect(100, 100, 200, 200),
            manager=default_ui_manager,
        )

        # Add content that exceeds container height
        button = UIButton(
            relative_rect=pygame.Rect(10, 10, 150, 300),
            text="Test Button",
            manager=default_ui_manager,
            container=container,
        )

        initial_button_pos = button.relative_rect.topleft

        # Scroll down
        container.vert_scroll_bar.scroll_wheel_moved = True
        container.vert_scroll_bar.scroll_wheel_amount = -1.0
        container.vert_scroll_bar.update(0.02)
        container.update(0.02)

        # Button should maintain its relative position within scrollable container
        assert button.relative_rect.topleft == initial_button_pos

        # Scroll to bottom
        container.vert_scroll_bar.start_percentage = 1.0
        container.update(0.02)

        # Button should still maintain its relative position
        assert button.relative_rect.topleft == initial_button_pos


if __name__ == "__main__":
    pytest.console_main()
