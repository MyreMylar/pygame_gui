import pygame
from pygame_gui.core.ui_element import UIElement


class UIContainer(UIElement):
    def __init__(self, relative_rect, ui_manager,
                 ui_container=None, element_ids=None, object_id=None):
        self._layer = 0
        self.ui_manager = ui_manager
        if element_ids is None:
            new_element_ids = ['container']
        else:
            new_element_ids = element_ids.copy()
            new_element_ids.append('container')
        super().__init__(relative_rect, ui_manager, ui_container,
                         object_id=object_id,
                         element_ids=new_element_ids,
                         starting_height=1,
                         layer_thickness=1)

        self.sprite_group = self.ui_manager.get_sprite_group()
        self.image = pygame.Surface((0, 0))
        self.elements = []
        self.layer_thickness = 1

        self.hovered = False

    def add_element(self, element):
        element.change_layer(self._layer + element.starting_height)
        self.elements.append(element)
        self.recalculate_container_layer_thickness()

    def remove_element(self, element):
        if element in self.elements:
            self.elements.remove(element)
        self.recalculate_container_layer_thickness()

    def recalculate_container_layer_thickness(self):
        """
        This function will iterate through the elements in our container and determine the maximum 'height'
        that they reach in the layer stack. We then use that to determine the overall 'thickness' of this container.
        The thickness value is used to determine where to place overlapping windows in the layers
        :return:
        """
        max_element_top_layer = 0
        for element in self.elements:
            if element.top_layer > max_element_top_layer:
                max_element_top_layer = element.top_layer

        self.layer_thickness = max_element_top_layer - self._layer

    def change_container_layer(self, new_layer):
        if new_layer != self._layer:
            self._layer = new_layer
            self.sprite_group.change_layer(self, self._layer)
            for element in self.elements:
                element.change_layer(self._layer + element.starting_height)

    def update_containing_rect_position(self):
        super().update_containing_rect_position()
        for element in self.elements:
            element.update_containing_rect_position()

    def get_top_layer(self):
        return self._layer + self.layer_thickness

    def kill(self):
        while len(self.elements) > 0:
            self.elements.pop().kill()
        super().kill()

    # noinspection PyUnusedLocal
    def check_hover(self, time_delta, hovered_higher_element):
        if self.alive():
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if self.rect.collidepoint(mouse_x, mouse_y) and not hovered_higher_element:
                if not self.hovered:
                    self.hovered = True
                hovered_higher_element = True

            else:
                if self.hovered:
                    self.hovered = False

        elif self.hovered:
            self.hovered = False
        return hovered_higher_element
