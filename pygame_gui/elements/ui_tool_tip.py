import pygame
import pygame.gfxdraw

from ..core.ui_element import UIElement
from ..elements import ui_text_box


class UITooltip(UIElement):

    def __init__(self, html_text, hover_distance, manager, element_ids=None, object_id=None):
        width = 170
        if element_ids is None:
            new_element_ids = ['tool_tip']
        else:
            new_element_ids = element_ids.copy()
            new_element_ids.append('tool_tip')
        super().__init__(relative_rect=pygame.Rect((0, 0), (width, -1)),
                         manager=manager,
                         container=None,
                         starting_height=manager.get_sprite_group().get_top_layer(),
                         layer_thickness=1,
                         element_ids=new_element_ids,
                         object_id=object_id)

        self.horiz_shadow_spacing = 2
        self.vert_shadow_spacing = 2
        self.hover_distance_from_target = hover_distance
        self.text_block = ui_text_box.UITextBox(html_text,
                                                pygame.Rect(self.horiz_shadow_spacing,
                                                            self.vert_shadow_spacing,
                                                            width - (2 * self.horiz_shadow_spacing), -1),
                                                manager=self.ui_manager,
                                                layer_starting_height=self._layer+1,
                                                element_ids=self.element_ids,
                                                object_id=self.object_id)

        height = self.text_block.rect.height + (2 * self.vert_shadow_spacing)

        self.rect.height = height
        # should load this image elsewhere in a real program
        self.image = self.ui_manager.get_shadow(self.rect.size)

    def kill(self):
        self.text_block.kill()
        super().kill()

    def find_valid_position(self, position):
        """
        Finds a valid position for the tool tip inside the root container of the UI.
        :param position:
        :return:
        """

        window_rect = self.ui_manager.get_window_stack().get_root_window().get_container().rect

        self.rect.centerx = position.x
        self.rect.top = position.y + self.hover_distance_from_target[1]

        if window_rect.contains(self.rect):
            self.text_block.rect.x = self.rect.x + self.horiz_shadow_spacing
            self.text_block.rect.y = self.rect.y + self.vert_shadow_spacing
            return True
        else:
            if self.rect.bottom > window_rect.bottom:
                self.rect.bottom = position.y - self.hover_distance_from_target[1]
            if self.rect.right > window_rect.right:
                self.rect.right = window_rect.right - self.hover_distance_from_target[0]
            if self.rect.left < window_rect.left:
                self.rect.left = window_rect.left + self.hover_distance_from_target[0]

        if window_rect.contains(self.rect):
            self.text_block.rect.x = self.rect.x + self.horiz_shadow_spacing
            self.text_block.rect.y = self.rect.y + self.vert_shadow_spacing
            return True
        else:
            return False
