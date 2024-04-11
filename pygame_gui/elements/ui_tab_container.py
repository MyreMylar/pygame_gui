from typing import List, Dict, Optional, Union, Tuple

import pygame

from pygame_gui.core.interfaces import (Coordinate, IContainerLikeInterface,
                                        IUIManagerInterface, IUIElementInterface)
from pygame_gui._constants import UI_BUTTON_PRESSED
from pygame_gui.core import UIElement, UIContainer, ObjectID
from pygame_gui.elements import UIButton, UIPanel


class UITabContainer(UIElement):
    """
    ** EXPERIMENTAL ** A tab container. The displayed panel can be switched by clicking on the tab.

    :param relative_rect: Normally a rectangle describing the position (relative to its container) and
                          dimensions. Also accepts a position Tuple, or Vector2 where the dimensions
                          will be dynamic depending on the button's contents. Dynamic dimensions can
                          be requested by setting the required dimension to -1.
    :param manager: The UIManager that manages this element. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param container: The container that this element is within. If not provided or set to None
                      will be the root window's container.
    :param starting_height: The height in layers above its container that this element will be
                            placed.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine-tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param visible: Whether the element is visible by default. Warning - container visibility may
                    override this.
    """

    def __init__(self, relative_rect: Union[pygame.Rect, Tuple[int, int, int, int]],
                 manager: Optional[IUIManagerInterface] = None,
                 container: Optional[IContainerLikeInterface] = None,
                 *,
                 starting_height: int = 1,
                 parent_element: Optional[IUIElementInterface] = None,
                 object_id: Union[ObjectID, str, None] = None,
                 anchors: Optional[Dict[str, Union[str, IUIElementInterface]]] = None,
                 visible: int = 1):

        super().__init__(relative_rect, manager, container,
                         starting_height=starting_height,
                         layer_thickness=1,
                         anchors=anchors,
                         visible=visible,
                         parent_element=parent_element,
                         object_id=object_id,
                         element_id=['tab_container'])

        self._root_container = UIContainer(relative_rect=relative_rect,
                                           manager=manager,
                                           starting_height=starting_height,
                                           container=container,
                                           anchors=anchors,
                                           visible=self.visible)

        self.tabs: List[Dict] = []
        self.current_container_index: Optional[int] = None

        self.button_height: int = 30
        self.max_button_width: int = self.rect.width

    @property
    def tab_count(self) -> int:
        return len(self.tabs)

    def switch_current_container(self, index: int):
        current_container = self.get_tab_container()
        if current_container is not None:
            current_container.hide()
        self.current_container_index = index
        self.get_tab_container().show()

    def add_tab(self, title_text: str, title_object_id: str) -> int:
        """
        Create a new tab.

        :return : the integer id of the newly created tab
        """
        self.rebuild(self.tab_count + 1)
        max_button_width = self._calculate_max_button_width(self.tab_count + 1)
        furthest_right = 0
        if len(self.tabs) > 0:
            for tab in self.tabs:
                furthest_right += tab["button"].rect.width
        button_rect = pygame.Rect(furthest_right, 0, -1, self.button_height)
        button = UIButton(button_rect, title_text, manager=self.ui_manager, container=self._root_container,
                          parent_element=self, object_id=ObjectID(title_object_id, '@tab_title_button'),
                          max_dynamic_width=max_button_width)
        container_rect = self._calculate_container_rect_by_layout()
        container = UIPanel(container_rect, manager=self.ui_manager, container=self._root_container, parent_element=self)
        self.tabs.append({"text": title_text, "button": button, "container": container})
        tab_id = self.tab_count - 1
        if self.current_container_index is None:
            self.current_container_index = tab_id
            button.select()
        else:
            container.hide()
        return tab_id

    def get_tab(self, tab_id: Optional[int] = None) -> Optional[Dict]:
        if tab_id is None:
            if self.current_container_index is None:
                return None
            else:
                tab_id = self.current_container_index

        return self.tabs[tab_id]

    def get_title_text(self, tab_id: Optional[int] = None):
        tab = self.get_tab(tab_id)
        if tab is None:
            return None
        else:
            return tab["text"]

    def get_title_button(self, tab_id: Optional[int] = None):
        tab = self.get_tab(tab_id)
        if tab is None:
            return None
        else:
            return tab["button"]

    def get_tab_container(self, tab_id=None) -> Optional[UIPanel]:
        tab = self.get_tab(tab_id)
        if tab is None:
            return None
        else:
            return tab["container"]

    def delete_tab(self, tab_id):
        self.tabs[tab_id]["button"].kill()
        self.tabs[tab_id]["container"].kill()
        del self.tabs[tab_id]
        self.rebuild()

    def _calculate_max_button_width(self, count: Optional[int] = None):
        width = self._root_container.rect.width
        if count is None:
            count = self.tab_count

        if count == 0:
            button_width = self.max_button_width
        else:
            button_width = width // count
            button_width = min(button_width, self.max_button_width)

        return button_width

    def _calculate_container_rect_by_layout(self) -> pygame.Rect:
        return pygame.Rect(0, self.button_height, self._root_container.rect.width,
                           self.rect.height - self.button_height)

    def disable(self):
        """
        Disables the window and it's contents so it is no longer interactive.
        """
        super().disable()
        if self.is_enabled:
            self._root_container.disable()

    def enable(self):
        """
        Enables the window and it's contents so it is interactive again.
        """
        super().enable()
        if not self.is_enabled:
            self._root_container.enable()

    def show(self):
        """
        In addition to the base UIElement.show() - show the _window_root_container which will
        propagate and show all the children.
        """
        super().show()
        self._root_container.show()

    def hide(self):
        """
        In addition to the base UIElement.hide() - hide the _window_root_container which will
        propagate and hide all the children.
        """
        super().hide()
        if self._root_container is not None:
            self._root_container.hide()

    def set_dimensions(self, dimensions: Coordinate, clamp_to_container: bool = False):
        """
        Set the size of this tab container.

        :param dimensions: The new dimensions to set.
        :param clamp_to_container: Whether we should clamp the dimensions to the
                                    dimensions of the container or not.

        """
        super().set_dimensions(dimensions)
        self._root_container.set_dimensions(dimensions)
        self.rebuild()

    def rebuild(self, count: Optional[int] = None):
        """
        Rebuilds the tab container.

        """
        super().rebuild()
        if count is None:
            count = self.tab_count
        max_button_width = self._calculate_max_button_width(count)
        current_right = 0
        for i, tab in enumerate(self.tabs, 0):
            button: UIButton = tab["button"]
            if i >= count:
                continue
            button.max_dynamic_width = max_button_width
            button.rebuild()
            button.set_relative_position((current_right, 0))
            current_right += button.rect.width

            container = tab["container"]
            if i == self.current_container_index:
                container.show()
                button.select()
            else:
                container.hide()

    def process_event(self, event: pygame.Event):
        """
        Handles various interactions with the tab container.

        :param event: The event to process.

        :return: Return True if we want to consume this event, so it is not passed on to the
                 rest of the UI.

        """
        consumed_event = False

        if event.type == UI_BUTTON_PRESSED:
            for i, tab in enumerate(self.tabs, 0):
                tab_title_button: UIButton = tab["button"]
                if event.ui_element == tab_title_button:
                    self.switch_current_container(i)
                    consumed_event = True
                    tab_title_button.select()
                elif tab_title_button.is_selected:
                    tab_title_button.unselect()

        return consumed_event

    def kill(self):
        """
        Overrides the basic kill() method of a pygame sprite so that we also kill all the UI
        elements in this panel.

        """
        self._root_container.kill()
        super().kill()
