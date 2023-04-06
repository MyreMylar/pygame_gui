import warnings

from typing import Union, Tuple, Dict, Optional

import pygame

from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IUIManagerInterface, IUITooltipInterface, IUIElementInterface
from pygame_gui.core.ui_element import UIElement

from pygame_gui.elements.ui_text_box import UITextBox


class UITooltip(UIElement, IUITooltipInterface):
    """
    A tool tip is a floating block of text that gives additional information after a user hovers
    over an interactive part of a GUI for a short time. In Pygame GUI the tooltip's text is
    style-able with HTML.

    At the moment the tooltips are only available as an option on UIButton elements.

    Tooltips also don't allow a container as they are designed to overlap normal UI boundaries and
    be contained only within the 'root' window/container, which is synonymous with the pygame
    display surface.

    :param html_text: Text styled with HTML, to be displayed on the tooltip.
    :param hover_distance: Distance in pixels between the tooltip and the thing being hovered.
    :param manager: The UIManager that manages this element. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param text_kwargs: a dictionary of variable arguments to pass to the translated text
                        useful when you have multiple translations that need variables inserted
                        in the middle.

    """
    def __init__(self,
                 html_text: str,
                 hover_distance: Tuple[int, int],
                 manager: Optional[IUIManagerInterface] = None,
                 parent_element: Optional[IUIElementInterface] = None,
                 object_id: Optional[Union[ObjectID, str]] = None,
                 anchors: Optional[Dict[str, Union[str, UIElement]]] = None,
                 *,
                 text_kwargs: Dict[str, str] = None):

        super().__init__(relative_rect=pygame.Rect((0, 0), (-1, -1)),
                         manager=manager,
                         container=None,
                         starting_height=manager.get_sprite_group().get_top_layer()+1,
                         layer_thickness=1,
                         anchors=anchors)

        self._create_valid_ids(container=None,
                               parent_element=parent_element,
                               object_id=object_id,
                               element_id='tool_tip')

        self.text_block = None
        self.rect_width = None  # type: Optional[int]
        self.hover_distance_from_target = hover_distance

        self.rebuild_from_changed_theme_data()

        self.text_block = UITextBox(html_text,
                                    pygame.Rect(0, 0, self.rect_width, -1),
                                    manager=self.ui_manager,
                                    starting_height=self._layer,
                                    parent_element=self,
                                    text_kwargs=text_kwargs)

        self.rect_width = self.text_block.rect.size[0]
        super().set_dimensions(self.text_block.rect.size)

        self._set_image(self.ui_manager.get_universal_empty_surface())

    def rebuild(self):
        """
        Rebuild anything that might need rebuilding.

        """
        self._set_image(self.ui_manager.get_universal_empty_surface())

        if self.text_block is not None:
            self.text_block.set_dimensions((self.rect_width, -1))

            self.relative_rect.height = self.text_block.rect.height
            self.relative_rect.width = self.text_block.rect.width
            self.rect.width = self.text_block.rect.width
            self.rect.height = self.text_block.rect.height

    def kill(self):
        """
        Overrides the UIElement's default kill method to also kill the text block element that
        helps make up the complete tool tip.
        """
        self.text_block.kill()
        super().kill()

    def find_valid_position(self, position: pygame.math.Vector2) -> bool:
        """
        Finds a valid position for the tool tip inside the root container of the UI.

        The algorithm starts from the position of the target we are providing a tool tip for then it
        tries to fit the rectangle for the tool tip onto the screen by moving it above, below, to
        the left and to the right, until we find a position that fits the whole tooltip rectangle
        on the screen at once.

        If we fail to manage this then the method will return False. Otherwise it returns True and
        set the position of the tool tip to our valid position.

        :param position: A 2D vector representing the position of the target this tool tip is for.

        :return: returns True if we find a valid (visible) position and False if we do not.

        """

        window_rect = self.ui_manager.get_root_container().get_rect()

        if window_rect.contains(pygame.Rect(int(position[0]), int(position[1]), 1, 1)):
            self.rect.left = int(position.x)
            self.rect.top = int(position.y + self.hover_distance_from_target[1])

            if window_rect.contains(self.rect):
                self.relative_rect = self.rect.copy()
                self.text_block.set_position(self.rect.topleft)
                return True
            else:
                if self.rect.bottom > window_rect.bottom:
                    self.rect.bottom = int(position.y - self.hover_distance_from_target[1])
                if self.rect.right > window_rect.right:
                    self.rect.right = window_rect.right - self.hover_distance_from_target[0]
                if self.rect.left < window_rect.left:
                    self.rect.left = window_rect.left + self.hover_distance_from_target[0]

            if window_rect.contains(self.rect):
                self.relative_rect = self.rect.copy()
                self.text_block.set_position(self.rect.topleft)
                return True
            else:
                self.relative_rect = self.rect.copy()
                warnings.warn("Unable to fit tool tip on screen")
                return False
        else:
            self.relative_rect = self.rect.copy()
            warnings.warn("initial position for tool tip is off screen,"
                          " unable to find valid position")
            return False

    def rebuild_from_changed_theme_data(self):
        """
        Called by the UIManager to check the theming data and rebuild whatever needs rebuilding for
        this element when the theme data has changed.
        """
        super().rebuild_from_changed_theme_data()
        has_any_changed = False

        if self._check_misc_theme_data_changed(attribute_name='rect_width',
                                               default_value=170,
                                               casting_func=int):
            has_any_changed = True

        if has_any_changed:
            self.rebuild()

    def set_position(self, position: Union[pygame.math.Vector2,
                                           Tuple[int, int],
                                           Tuple[float, float]]):
        """
        Sets the absolute screen position of this tool tip, updating it's subordinate text box at
        the same time.

        :param position: The absolute screen position to set.

        """
        super().set_position(position)
        self.text_block.set_position(position)

    def set_relative_position(self, position: Union[pygame.math.Vector2,
                                                    Tuple[int, int],
                                                    Tuple[float, float]]):
        """
        Sets the relative screen position of this tool tip, updating it's subordinate text box at
        the same time.

        :param position: The relative screen position to set.

        """
        super().set_relative_position(position)
        self.text_block.set_relative_position(position)

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2,
                                               Tuple[int, int],
                                               Tuple[float, float]]):
        """
        Directly sets the dimensions of this tool tip. This will overwrite the normal theming.

        :param dimensions: The new dimensions to set

        """
        self.rect_width = dimensions[0]

        super().set_dimensions(dimensions)
        self.text_block.set_dimensions(dimensions)

    def show(self):
        """
        This is a base method show() of a UIElement, but since it's not intended to be used on a
        UIToolTip - display a warning.
        """
        super().show()

        warnings.warn("Use of show() and hide() methods of UIToolTip objects is not supported.")

    def hide(self):
        """
        This is a base method hide() of a UIElement, but since it's not intended to be used
        on a UIToolTip - display a warning.
        """
        super().hide()

        warnings.warn("Use of show() and hide() methods of UIToolTip objects is not supported.")
