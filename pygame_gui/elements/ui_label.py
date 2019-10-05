from ..core.ui_element import UIElement
import pygame
import warnings


class UILabel(UIElement):
    def __init__(self, relative_rect, text, manager,
                 container=None, element_ids=None, object_id=None):
        if element_ids is None:
            new_element_ids = ['label']
        else:
            new_element_ids = element_ids.copy()
            new_element_ids.append('label')
        super().__init__(relative_rect, manager, container,
                         starting_height=1,
                         layer_thickness=1,
                         object_id=object_id,
                         element_ids=new_element_ids)
        self.text = text
        self.redraw()

    def set_text(self, text):
        self.text = text
        self.redraw()

    def redraw(self):
        font = self.ui_theme.get_font(self.object_id, self.element_ids)
        text_colour = self.ui_theme.get_colour(self.object_id, self.element_ids, 'normal_text')
        bg_colour = self.ui_theme.get_colour(self.object_id, self.element_ids, 'dark_bg')
        text_size = font.size(self.text)
        if text_size[1] > self.rect.height or text_size[0] > self.rect.width:
            width_overlap = self.rect.width - text_size[0]
            height_overlap = self.rect.height - text_size[1]
            warn_text = 'Label Rect is too small for text: ' + self.text + ' - size diff: ' + str((width_overlap,
                                                                                                   height_overlap))
            warnings.warn(warn_text, UserWarning)
        text_render = font.render(self.text, True, text_colour, bg_colour)
        text_render_rect = text_render.get_rect(centery=self.rect.height/2)
        self.image = pygame.Surface(self.rect.size).convert_alpha()
        self.image.fill(bg_colour)
        self.image.blit(text_render, text_render_rect)
