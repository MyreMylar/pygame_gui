import pytest
import pygame

from pygame_gui.elements.ui_auto_resizing_container import UIAutoResizingContainer
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIVerticalScrollBar


class TestUIContainer:
    def test_creation(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        UIAutoResizingContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)

    def test_get_container(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                           _display_surface_return_none):
        container = UIAutoResizingContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)
        assert container.get_container() == container

    def test_add_element(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                         _display_surface_return_none):
        container = UIAutoResizingContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)

        button = UIButton(relative_rect=pygame.Rect(0, 0, 50, 50), text="",
                          manager=default_ui_manager)
        default_ui_manager.get_root_container().remove_element(button)
        container.add_element(button)
        container.update(0.4)
        assert len(container.elements) == 1

        button_right = UIButton(relative_rect=pygame.Rect(300, 50, 50, 50), text="",
                                manager=default_ui_manager)
        default_ui_manager.get_root_container().remove_element(button_right)
        container.add_element(button_right)
        container.update(0.4)
        assert len(container.elements) == 2

        button_left = UIButton(relative_rect=pygame.Rect(-100, 50, 50, 50), text="",
                               manager=default_ui_manager)
        default_ui_manager.get_root_container().remove_element(button_left)
        container.add_element(button_left)
        container.update(0.4)
        assert len(container.elements) == 3

        button_top = UIButton(relative_rect=pygame.Rect(100, -50, 50, 50), text="",
                              manager=default_ui_manager)
        default_ui_manager.get_root_container().remove_element(button_top)
        container.add_element(button_top)
        container.update(0.4)
        assert len(container.elements) == 4

        button_bottom = UIButton(relative_rect=pygame.Rect(100, 400, 50, 50), text="",
                                 manager=default_ui_manager)
        default_ui_manager.get_root_container().remove_element(button_bottom)
        container.add_element(button_bottom)
        container.update(0.4)
        assert len(container.elements) == 5

    def test_remove_element(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                            _display_surface_return_none):
        container = UIAutoResizingContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)

        button = UIButton(relative_rect=pygame.Rect(0, 0, 50, 50), text="",
                          manager=default_ui_manager,
                          container=container)

        container.remove_element(button)

        button_right = UIButton(relative_rect=pygame.Rect(300, 50, 50, 50), text="",
                                manager=default_ui_manager,
                                container=container)
        container.remove_element(button_right)
        button_left = UIButton(relative_rect=pygame.Rect(-100, 50, 50, 50), text="",
                               manager=default_ui_manager,
                               container=container)
        container.remove_element(button_left)
        button_top = UIButton(relative_rect=pygame.Rect(100, -50, 50, 50), text="",
                              manager=default_ui_manager,
                              container=container)
        container.remove_element(button_top)
        button_bottom = UIButton(relative_rect=pygame.Rect(100, 400, 50, 50), text="",
                                 manager=default_ui_manager,
                                 container=container)
        container.remove_element(button_bottom)

        container.update(0.4)
        assert len(container.elements) == 0

    def test_recalculate_container_layer_thickness(self, _init_pygame,
                                                   default_ui_manager: IUIManagerInterface,
                                                   _display_surface_return_none):
        container = UIAutoResizingContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)
        UIButton(relative_rect=pygame.Rect(0, 0, 50, 50), text="",
                 manager=default_ui_manager,
                 container=container)

        container.recalculate_container_layer_thickness()

        assert container.layer_thickness == 2

    def test_change_container_layer(self, _init_pygame, default_ui_manager,
                                    _display_surface_return_none):
        container = UIAutoResizingContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)

        UIButton(relative_rect=pygame.Rect(0, 0, 50, 50), text="",
                 manager=default_ui_manager, container=container)
        container.change_layer(2)
        assert container.get_top_layer() == 4

    def test_get_top_layer(self, _init_pygame, default_ui_manager,
                           _display_surface_return_none):
        container = UIAutoResizingContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)

        UIButton(relative_rect=pygame.Rect(0, 0, 50, 50), text="",
                 manager=default_ui_manager, container=container)
        assert container.get_top_layer() == 3

    def test_update_containing_rect_position(self, _init_pygame, default_ui_manager,
                                             _display_surface_return_none):
        container = UIAutoResizingContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)
        container_2 = UIAutoResizingContainer(pygame.Rect(50, 50, 50, 50), manager=default_ui_manager,
                                              container=container)

        button = UIButton(relative_rect=pygame.Rect(20, 20, 30, 20), text="X",
                          manager=default_ui_manager, container=container_2)

        container.set_position((0, 0))

        container_2.update_containing_rect_position()

        assert button.rect.topleft == (70, 70)

    def test_set_position(self, _init_pygame, default_ui_manager,
                          _display_surface_return_none):
        container = UIAutoResizingContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)

        container.set_position((50, 50))

        assert container.rect.topleft == (50, 50)

    def test_set_relative_position(self, _init_pygame, default_ui_manager,
                                   _display_surface_return_none):
        container = UIAutoResizingContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)
        container_2 = UIAutoResizingContainer(pygame.Rect(50, 50, 50, 50), manager=default_ui_manager,
                                              container=container)

        container_2.set_relative_position((25, 25))

        assert container_2.rect.topleft == (125, 125)

    def test_set_dimensions(self, _init_pygame, default_ui_manager,
                            _display_surface_return_none):
        container = UIAutoResizingContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)

        container.set_dimensions((50, 50))

        assert container.rect.size == (50, 50)

    def test_kill(self, _init_pygame, default_ui_manager,
                  _display_surface_return_none):
        container = UIAutoResizingContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)
        container_2 = UIAutoResizingContainer(pygame.Rect(50, 50, 50, 50), manager=default_ui_manager,
                                              container=container)

        button = UIButton(relative_rect=pygame.Rect(20, 20, 30, 20), text="X",
                          manager=default_ui_manager, container=container_2)

        container.kill()

        assert not button.alive()
        assert not container_2.alive()
        assert not container.alive()

    def test_clear(self, _init_pygame, default_ui_manager,
                   _display_surface_return_none):
        container = UIAutoResizingContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)
        container_2 = UIAutoResizingContainer(pygame.Rect(50, 50, 50, 50), manager=default_ui_manager,
                                              container=container)

        button = UIButton(relative_rect=pygame.Rect(20, 20, 30, 20), text="X",
                          manager=default_ui_manager, container=container_2)

        container.clear()

        assert not button.alive()
        assert not container_2.alive()
        assert len(container.elements) == 0

    def test_check_hover_when_not_able_to_hover(self, _init_pygame, default_ui_manager,
                                                _display_surface_return_none):
        container = UIAutoResizingContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager)
        default_ui_manager.mouse_position = (150, 150)
        assert container.check_hover(0.5, False) is True  # already hovering
        container.kill()
        assert container.check_hover(0.5, False) is False  # dead so can't hover anymore

    def test_resizing_with_anchors(self, _init_pygame, default_ui_manager,
                                   _display_surface_return_none):
        container = UIAutoResizingContainer(relative_rect=pygame.Rect(0, 0, 300, 300),
                                            manager=default_ui_manager)

        scroll_bar = UIVerticalScrollBar(
            relative_rect=pygame.Rect(-20, 0, 20, 300),
            visible_percentage=0.5,
            manager=default_ui_manager,
            container=container,
            anchors={'left': 'right',
                     'right': 'right',
                     'top': 'top',
                     'bottom': 'bottom'})

        assert scroll_bar.top_button.rect.width == 14
        container.set_dimensions((400, 400))
        assert scroll_bar.top_button.rect.width == 14

    def test_container_show(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                            _display_surface_return_none):
        container = UIAutoResizingContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager, visible=0)
        assert container.visible == 0
        container.show()
        assert container.visible == 1

    def test_container_hide(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                            _display_surface_return_none):
        container = UIAutoResizingContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager, visible=1)
        assert container.visible == 1
        container.hide()
        assert container.visible == 0

    def test_container_children_inheriting_hidden_status(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                                                         _display_surface_return_none):
        container = UIAutoResizingContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager, visible=0)
        button = UIButton(relative_rect=pygame.Rect(0, 0, 50, 50), text="",
                          manager=default_ui_manager, container=container, visible=1)
        assert container.visible == 0
        assert button.visible == 0

    def test_hidden_container_children_behaviour_on_show(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                                                         _display_surface_return_none):
        container = UIAutoResizingContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager, visible=0)
        button = UIButton(relative_rect=pygame.Rect(0, 0, 50, 50), text="",
                          manager=default_ui_manager, container=container)
        assert container.visible == 0
        assert button.visible == 0
        container.show()
        assert container.visible == 1
        assert button.visible == 1

    def test_visible_container_children_behaviour_on_show(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                                                          _display_surface_return_none):
        container = UIAutoResizingContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager, visible=1)
        button = UIButton(relative_rect=pygame.Rect(0, 0, 50, 50), text="",
                          manager=default_ui_manager, container=container, visible=0)
        assert container.visible == 1
        assert button.visible == 0
        container.show()
        assert container.visible == 1
        assert button.visible == 0

    def test_visible_container_children_behaviour_on_hide(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                                                          _display_surface_return_none):
        container = UIAutoResizingContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager, visible=1)
        button = UIButton(relative_rect=pygame.Rect(0, 0, 50, 50), text="",
                          manager=default_ui_manager, container=container)
        assert container.visible == 1
        assert button.visible == 1
        container.hide()
        assert container.visible == 0
        assert button.visible == 0

    def test_hidden_container_children_behaviour_on_hide(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                                                         _display_surface_return_none):
        container = UIAutoResizingContainer(pygame.Rect(100, 100, 200, 200), manager=default_ui_manager, visible=0)
        button = UIButton(relative_rect=pygame.Rect(0, 0, 50, 50), text="",
                          manager=default_ui_manager, container=container)
        button.show()
        assert container.visible == 0
        assert button.visible == 1
        container.hide()
        assert container.visible == 0
        assert button.visible == 1


if __name__ == '__main__':
    pytest.console_main()
