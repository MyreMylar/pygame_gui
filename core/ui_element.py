import pygame


class UIElement(pygame.sprite.Sprite):
    def __init__(self, relative_rect, ui_manager, ui_container,
                 starting_height, layer_thickness, object_id=None, element_ids=None):
        self._layer = 0
        self.ui_manager = ui_manager
        super().__init__(self.ui_manager.get_sprite_group())
        self.relative_rect = relative_rect
        self.ui_group = self.ui_manager.get_sprite_group()
        self.ui_theme = self.ui_manager.get_theme()
        self.object_id = object_id
        self.element_ids = element_ids

        self.layer_thickness = layer_thickness
        self.starting_height = starting_height
        self.top_layer = self._layer + self.layer_thickness

        if ui_container is None:
            root_window = self.ui_manager.get_window_stack().get_root_window()
            if root_window is not None:
                ui_container = root_window.get_container()
            else:
                ui_container = self

        self.ui_container = ui_container
        if self.ui_container is not None and self.ui_container is not self:
            self.ui_container.add_element(self)

        if self.ui_container is self:
            self.rect = pygame.Rect((relative_rect.x,
                                    relative_rect.y),
                                    relative_rect.size)
        else:
            self.rect = pygame.Rect((self.ui_container.rect.x + relative_rect.x,
                                     self.ui_container.rect.y + relative_rect.y),
                                    relative_rect.size)

        self.image = None

        self.is_enabled = True
        self.hovered = False
        self.hover_time = 0.0

    def update_containing_rect_position(self):
        self.rect = pygame.Rect((self.ui_container.rect.x + self.relative_rect.x,
                                 self.ui_container.rect.y + self.relative_rect.y),
                                self.relative_rect.size)

    def change_layer(self, new_layer):
        self.ui_group.change_layer(self, new_layer)
        self._layer = new_layer
        self.top_layer = new_layer + self.layer_thickness

    def kill(self):
        self.ui_container.remove_element(self)
        super().kill()

    def check_hover(self, time_delta, hovered_higher_element):
        if self.alive() and self.can_hover():
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_pos = pygame.math.Vector2(mouse_x, mouse_y)

            if self.is_enabled and self.hover_point(mouse_x, mouse_y) and not hovered_higher_element:
                if not self.hovered:
                    self.hovered = True
                    self.on_hovered()

                hovered_higher_element = True
                self.while_hovering(time_delta, mouse_pos)

            else:
                if self.hovered:
                    self.hovered = False
                    self.on_unhovered()
        elif self.hovered:
            self.hovered = False
        return hovered_higher_element

    def on_hovered(self):
        pass

    def while_hovering(self, time_delta, mouse_pos):
        pass

    def hover_point(self, x, y):
        return self.rect.collidepoint(x, y)

    def on_unhovered(self):
        pass

    def can_hover(self):
        return True

    def process_event(self, event):
        if self is not None:
            return False

    def select(self):
        pass

    def unselect(self):
        pass
