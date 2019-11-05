import pygame
import pygame.gfxdraw
from typing import Union, Tuple

from pygame_gui import ui_manager
from pygame_gui.core.ui_element import UIElement
from pygame_gui.elements import ui_text_box


class UITooltip(UIElement):
    """
    A tool tip is a floating block of text that gives additional information after a user hovers over an interactive
    part of a GUI for a short time. In Pygame GUI the tooltip's text is style-able with HTML.

    At the moment the tooltips are only available as an option on UIButton elements.

    Tooltips also don't allow a container as they are designed to overlap normal UI boundaries and be contained only
    within the 'root' window/container, which is synonymous with the pygame display surface.

    :param html_text: Text styled with HTML, to be displayed on the tooltip.
    :param hover_distance: Distance in pixels between the tooltip and the thing being hovered.
    :param manager: The UIManager that manages this element.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    """
    def __init__(self, html_text: str, hover_distance: Tuple[int, int],
                 manager: ui_manager.UIManager,
                 parent_element: UIElement = None,
                 object_id: Union[str, None] = None):

        new_element_ids, new_object_ids = self.create_valid_ids(parent_element=parent_element,
                                                                object_id=object_id,
                                                                element_id='tool_tip')
        super().__init__(relative_rect=pygame.Rect((0, 0), (-1, -1)),
                         manager=manager,
                         container=None,
                         starting_height=manager.get_sprite_group().get_top_layer(),
                         layer_thickness=1,
                         element_ids=new_element_ids,
                         object_ids=new_object_ids)

        rect_width = 170
        rect_width_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'rect_width')
        if rect_width_string is not None:
            rect_width = int(rect_width_string)

        self.hover_distance_from_target = hover_distance
        self.text_block = ui_text_box.UITextBox(html_text,
                                                pygame.Rect(0, 0, rect_width, -1),
                                                manager=self.ui_manager,
                                                layer_starting_height=self._layer+1,
                                                parent_element=self)

        self.relative_rect.height = self.text_block.rect.height
        self.relative_rect.width = self.text_block.rect.width
        self.rect.width = self.text_block.rect.width
        self.rect.height = self.text_block.rect.height
        # Get a shadow from the shadow generator
        self.image = pygame.Surface((0, 0))

    def kill(self):
        """
        Overrides the UIElement's default kill method to also kill the text block element that helps make up the
        complete tool tip.
        """
        self.text_block.kill()
        super().kill()

    def find_valid_position(self, position: pygame.math.Vector2) -> bool:
        """
        Finds a valid position for the tool tip inside the root container of the UI.

        The algorithm starts from the position of the target we are providing a tool tip for then it
        tries to fit the rectangle for the tool tip onto the screen by moving it above, below, to the left and to the
        right, until we find a position that fits the whole tooltip rectangle on the screen at once.

        If we fail to manage this then the method will return False. Otherwise it returns True and set the position
        of the tool tip to our valid position.

        :param position: A 2D vector representing the position of the target this tool tip is for.
        :return bool: returns True if we find a valid (visible) position and False if we do not.
        """

        window_rect = self.ui_manager.get_window_stack().get_root_window().get_container().rect

        self.rect.centerx = position.x
        self.rect.top = position.y + self.hover_distance_from_target[1]

        if window_rect.contains(self.rect):
            self.text_block.rect.x = self.rect.x
            self.text_block.rect.y = self.rect.y
            return True
        else:
            if self.rect.bottom > window_rect.bottom:
                self.rect.bottom = position.y - self.hover_distance_from_target[1]
            if self.rect.right > window_rect.right:
                self.rect.right = window_rect.right - self.hover_distance_from_target[0]
            if self.rect.left < window_rect.left:
                self.rect.left = window_rect.left + self.hover_distance_from_target[0]

        if window_rect.contains(self.rect):
            self.text_block.rect.x = self.rect.x
            self.text_block.rect.y = self.rect.y
            return True
        else:
            return False
