from turtle import update
from typing import Union, Tuple, List

import pygame

from pygame_gui._constants import UI_BUTTON_PRESSED
from pygame_gui.core import UIElement, UIContainer
from pygame_gui.core.interfaces import IContainerLikeInterface
from pygame_gui.elements import UIButton, UIPanel

class UITabContainer(UIElement):
    """
    A tab container. The displayed panel can be switched by clicking on the tab.

    :param relative_rect: Normally a rectangle describing the position (relative to its container) and
                          dimensions. Also accepts a position Tuple, or Vector2 where the dimensions
                          will be dynamic depending on the button's contents. Dynamic dimensions can
                          be requested by setting the required dimension to -1.
    :param manager: The UIManager that manages this element. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param container: The container that this element is within. If not provided or set to None
                      will be the root window's container.
    :param starting_height: The height in layers above it's container that this element will be
                            placed.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param visible: Whether the element is visible by default. Warning - container visibility may
                    override this.
    """
    def __init__(self, relative_rect: pygame.Rect,
                 manager,
                 container = None,
                 *,
                 starting_height: int = 1,
                 parent_element = None,
                 object_id = None,
                 anchors = None,
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
        self.tabs = []
        self.current_container_index = None
        
        self.button_height = 30
        self.max_button_width = 100
        
    @property
    def tab_count(self):
        return len(self.tabs)
       
    def switch_current_container(self, index):
        current_container = self.get_container()
        if current_container is not None:
            current_container.hide()
        self.current_container_index = index
        self.get_container().show()
       
    def add_tab(self, text:str):
        """
        Create a new tab.
        """
        self.rebuild(self.tab_count + 1)
        button_rects = self._calculate_button_rect_by_layout(self.tab_count + 1)
        button_rect = button_rects[self.tab_count]
        button = UIButton(button_rect, text, manager=self.ui_manager, container=self._root_container)
        
        container_rect = self._calculate_container_rect_by_layout()
        container = UIPanel(container_rect, manager=self.ui_manager, container=self._root_container)
        self.tabs.append({"text":text, "button":button, "container":container})
        tab_id = self.tab_count - 1
        if self.current_container_index is None:
            self.current_container_index = tab_id
        else:
            container.hide()
        return tab_id
        
    def get_tab(self, tab_id=None):
        if tab_id is None:
            if self.current_container_index is None:
                return None
            else:
                tab_id = self.current_container_index
        
        return self.tabs[tab_id]
        
    def get_text(self, tab_id=None):
        tab = self.get_tab(tab_id)
        if tab is None:
            return None
        else:
            return tab["text"]
        
    def get_button(self, tab_id=None):
        tab = self.get_tab(tab_id)
        if tab is None:
            return None
        else:
            return tab["button"]
       
    def get_container(self, tab_id=None):
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
        
    def _calculate_button_rect_by_layout(self, count:int=None):
        width = self._root_container.rect.width
        if count is None:
            count = self.tab_count

        if count == 0:
            button_width = self.max_button_width
        else:
            button_width = width // count
            button_width = min(button_width, self.max_button_width)
            
        button_rects = []
        for i in range(count):
            rect = pygame.Rect(button_width * i, 0, button_width, self.button_height)
            button_rects.append(rect)
        
        return button_rects
        
    def _calculate_container_rect_by_layout(self):
        return pygame.Rect(0, self.button_height, self._root_container.rect.width, self.rect.height - self.button_height)

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
        if self._window_root_container is not None:
            self._window_root_container.hide()
        
    def set_dimensions(self, dimensions: Union[pygame.math.Vector2,
                                            Tuple[int, int],
                                            Tuple[float, float]],
                    clamp_to_container: bool = False):
        """
        Set the size of this tab container.

        :param dimensions: The new dimensions to set.
        :param clamp_to_container: Whether we should clamp the dimensions to the
                                    dimensions of the container or not.

        """
        super().set_dimensions(dimensions)
        self._root_container.set_dimensions(dimensions)
        self.rebuild()

    def rebuild(self, count=None):
        """
        Rebuilds the tab container.

        """
        super().rebuild()
        if count is None:
            count = self.tab_count

        button_rects = self._calculate_button_rect_by_layout(count)
        for i, tab in enumerate(self.tabs, 0):
            button = tab["button"]
            if i >= count:
                continue
            button.set_dimensions((button_rects[i].width, button_rects[i].height))
            button.set_relative_position((button_rects[i].left, button_rects[i].top))
            
            container = tab["container"]
            if i == self.current_container_index:
                container.show()
            else:
                container.hide()
        
    def rebuild_from_changed_theme_data(self):
        """
        Checks if any theming parameters have changed, and if so triggers a full rebuild of the
        button's drawable shape.
        """
        super().rebuild_from_changed_theme_data()
        has_any_changed = False

        if self._check_misc_theme_data_changed(attribute_name='shape',
                                               default_value='rectangle',
                                               casting_func=str,
                                               allowed_values=['rectangle',
                                                               'rounded_rectangle']):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='tool_tip_delay',
                                               default_value=1.0,
                                               casting_func=float):
            has_any_changed = True

        if self._check_shape_theming_changed(defaults={'border_width': 1,
                                                       'shadow_width': 15,
                                                       'shape_corner_radius': 2}):
            has_any_changed = True

        background_colour = self.ui_theme.get_colour_or_gradient('dark_bg',
                                                                 self.combined_element_ids)
        if background_colour != self.background_colour:
            self.background_colour = background_colour
            has_any_changed = True

        border_colour = self.ui_theme.get_colour_or_gradient('normal_border',
                                                             self.combined_element_ids)
        if border_colour != self.border_colour:
            self.border_colour = border_colour
            has_any_changed = True

        if self._check_title_bar_theming_changed():
            has_any_changed = True

        if has_any_changed:
            self.rebuild()
                
    def process_event(self, event: pygame.Event):
        """
        Handles various interactions with the tab container.

        :param event: The event to process.

        :return: Return True if we want to consume this event so it is not passed on to the
                 rest of the UI.

        """
        consumed_event = False
        
        if event.type == UI_BUTTON_PRESSED:
            for i, tab in enumerate(self.tabs, 0):
                if event.ui_element == tab["button"]:
                    self.switch_current_container(i)
                    consumed_event = True
                    
        return consumed_event
                
    def kill(self):
        """
        Overrides the basic kill() method of a pygame sprite so that we also kill all the UI
        elements in this panel.

        """
        self._root_container.kill()
        super().kill()