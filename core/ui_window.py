import pygame
from pygame_gui.core.ui_container import UIContainer


class UIWindow(pygame.sprite.Sprite):
    def __init__(self, rect, ui_manager, element_ids=None, object_id=None):
        self._layer = 0
        if element_ids is None:
            new_element_ids = ["window"]
        else:
            new_element_ids = element_ids.copy()
            new_element_ids.append("window")
        self.layer_thickness = 1
        self.ui_manager = ui_manager
        super().__init__(self.ui_manager.get_sprite_group())

        self.element_ids = new_element_ids
        self.object_id = object_id

        self.window_container = UIContainer(rect.copy(), ui_manager, None, self.element_ids, self.object_id)

        self.window_stack = self.ui_manager.get_window_stack()
        self.window_stack.add_new_window(self)

        self.image = self.image = pygame.Surface((0, 0))
        self.rect = rect

    def process_event(self, event):
        pass

    def check_clicked_inside(self, event):
        event_handled = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = event.pos
                if self.rect.collidepoint(mouse_x, mouse_y):
                    self.window_stack.move_window_to_front(self)
                    event_handled = True
        return event_handled

    def update(self, time_delta):
        if self.get_container().layer_thickness + 1 != self.layer_thickness:
            self.layer_thickness = self.get_container().layer_thickness + 1

    def get_container(self):
        return self.window_container

    # noinspection PyUnusedLocal
    def check_hover(self, time_delta, hovered_higher_element):
        pass

    def get_top_layer(self):
        return self._layer + self.layer_thickness

    def change_window_layer(self, new_layer):
        if new_layer != self._layer:
            self._layer = new_layer
            self.ui_manager.get_sprite_group().change_layer(self, new_layer)
            self.window_container.change_container_layer(new_layer+1)

    def kill(self):
        self.window_stack.remove_window(self)
        self.window_container.kill()
        super().kill()

    def select(self):
        pass

    def unselect(self):
        pass
