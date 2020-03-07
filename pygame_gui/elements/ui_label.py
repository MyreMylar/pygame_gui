import pygame
import warnings
from typing import Union, Tuple, Dict

from pygame_gui.core.interfaces import IContainerInterface, IUIManagerInterface
from pygame_gui.core import ColourGradient, UIElement


class UILabel(UIElement):
    """
    A label lets us display a single line of text with a single font style. It's a quick to rebuild and simple
    alternative to the text box element.

    :param relative_rect: The rectangle that contains and positions the label relative to it's container.
    :param text: The text to display in the label.
    :param manager: The UIManager that manages this label.
    :param container: The container that this element is within. If set to None will be the root window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    """
    def __init__(self, relative_rect: pygame.Rect,
                 text: str,
                 manager: IUIManagerInterface,
                 container: Union[IContainerInterface, None] = None,
                 parent_element: UIElement = None,
                 object_id: Union[str, None] = None,
                 anchors: Dict[str, str] = None):

        new_element_ids, new_object_ids = self.create_valid_ids(container=container,
                                                                parent_element=parent_element,
                                                                object_id=object_id,
                                                                element_id='label')
        super().__init__(relative_rect, manager, container,
                         starting_height=1,
                         layer_thickness=1,
                         object_ids=new_object_ids,
                         element_ids=new_element_ids,
                         anchors=anchors)
        self.text = text

        # initialise theme params
        self.font = None

        self.bg_colour = None
        self.text_colour = None
        self.text_shadow_colour = None

        self.shadow_enabled = False
        self.shadow_size = 1
        self.shadow_offset = [0, 0]

        self.rebuild_from_changed_theme_data()

    def set_text(self, text: str):
        """
        Changes the string displayed by the label element. Labels do not support HTML styling.

        :param text: the text to set the label to.
        """
        if text != self.text:
            self.text = text
            self.rebuild()

    def rebuild(self):
        """
        Re-render the text to the label's underlying sprite image. This allows us to change what the displayed text is
        or remake it with different theming (if the theming has changed).
        """

        text_size = self.font.size(self.text)
        if text_size[1] > self.relative_rect.height or text_size[0] > self.relative_rect.width:
            width_overlap = self.relative_rect.width - text_size[0]
            height_overlap = self.relative_rect.height - text_size[1]
            warn_text = 'Label Rect is too small for text: ' + self.text + ' - size diff: ' + str((width_overlap,
                                                                                                   height_overlap))
            warnings.warn(warn_text, UserWarning)

        new_image = pygame.Surface(self.relative_rect.size, flags=pygame.SRCALPHA, depth=32)

        if type(self.bg_colour) == ColourGradient:
            new_image.fill(pygame.Color('#FFFFFFFF'))
            self.bg_colour.apply_gradient_to_surface(new_image)
            if type(self.text_colour) == ColourGradient:
                text_render = self.font.render(self.text, True, pygame.Color('#FFFFFFFF'))
                self.text_colour.apply_gradient_to_surface(text_render)

            else:
                text_render = self.font.render(self.text, True, self.text_colour)
        elif type(self.text_colour) == ColourGradient:
            new_image.fill(self.bg_colour)
            text_render = self.font.render(self.text, True, pygame.Color('#FFFFFFFF'))
            self.text_colour.apply_gradient_to_surface(text_render)
        else:
            new_image.fill(self.bg_colour)
            if self.bg_colour.a != 255 or self.shadow_enabled:
                text_render = self.font.render(self.text, True, self.text_colour)
            else:
                text_render = self.font.render(self.text, True, self.text_colour, self.bg_colour)
        text_render_rect = text_render.get_rect(centerx=int(self.rect.width / 2),
                                                centery=int(self.rect.height / 2))

        if self.shadow_enabled:
            shadow_text_render = self.font.render(self.text, True, self.text_shadow_colour)

            for y in range(-self.shadow_size, self.shadow_size+1):
                shadow_text_render_rect = pygame.Rect((text_render_rect.x + self.shadow_offset[0],
                                                       text_render_rect.y + self.shadow_offset[1] + y),
                                                      text_render_rect.size)
                new_image.blit(shadow_text_render, shadow_text_render_rect)

            for x in range(-self.shadow_size, self.shadow_size+1):
                shadow_text_render_rect = pygame.Rect((text_render_rect.x + self.shadow_offset[0] + x,
                                                       text_render_rect.y + self.shadow_offset[1]),
                                                      text_render_rect.size)
                new_image.blit(shadow_text_render, shadow_text_render_rect)

            for x_and_y in range(-self.shadow_size, self.shadow_size+1):
                shadow_text_render_rect = pygame.Rect((text_render_rect.x + self.shadow_offset[0] + x_and_y,
                                                       text_render_rect.y + self.shadow_offset[1] + x_and_y),
                                                      text_render_rect.size)
                new_image.blit(shadow_text_render, shadow_text_render_rect)

            for x_and_y in range(-self.shadow_size, self.shadow_size+1):
                shadow_text_render_rect = pygame.Rect((text_render_rect.x + self.shadow_offset[0] - x_and_y,
                                                       text_render_rect.y + self.shadow_offset[1] + x_and_y),
                                                      text_render_rect.size)
                new_image.blit(shadow_text_render, shadow_text_render_rect)

        new_image.blit(text_render, text_render_rect)

        self.set_image(new_image)

    def rebuild_from_changed_theme_data(self):
        any_changed = False

        font = self.ui_theme.get_font(self.object_ids, self.element_ids)
        if font != self.font:
            self.font = font
            any_changed = True

        text_colour = self.ui_theme.get_colour_or_gradient(self.object_ids, self.element_ids, 'normal_text')
        if text_colour != self.text_colour:
            self.text_colour = text_colour
            any_changed = True

        bg_colour = self.ui_theme.get_colour_or_gradient(self.object_ids, self.element_ids, 'dark_bg')
        if bg_colour != self.bg_colour:
            self.bg_colour = bg_colour
            any_changed = True

        text_shadow_colour = self.ui_theme.get_colour(self.object_ids, self.element_ids, 'text_shadow')
        if text_shadow_colour != self.text_shadow_colour:
            self.text_shadow_colour = text_shadow_colour
            any_changed = True

        shadow_enable_param = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'text_shadow')
        if shadow_enable_param is not None:
            try:
                shadow_enabled = bool(int(shadow_enable_param))
            except ValueError:
                shadow_enabled = False
            if shadow_enabled != self.shadow_enabled:
                self.shadow_enabled = shadow_enabled
                any_changed = True

        shadow_size_param = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'text_shadow_size')
        if shadow_size_param is not None:
            try:
                shadow_size = int(shadow_size_param)
            except ValueError:
                shadow_size = 1
            if shadow_size != self.shadow_size:
                self.shadow_size = shadow_size
                any_changed = True

        shadow_offset_param = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'text_shadow_offset')
        if shadow_offset_param is not None:
            offset_string_list = shadow_offset_param.split(',')
            if len(offset_string_list) == 2:
                try:
                    shadow_offset = [int(offset_string_list[0]), int(offset_string_list[1])]
                except ValueError:
                    shadow_offset = [1, 1]
                if shadow_offset != self.shadow_offset:
                    self.shadow_offset = shadow_offset
                    any_changed = True

        if any_changed:
            self.rebuild()

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        """
        Method to directly set the dimensions of a label.

        :param dimensions: The new dimensions to set.
        """
        self.rect.width = int(dimensions[0])
        self.rect.height = int(dimensions[1])
        self.relative_rect.size = self.rect.size

        self.rebuild()
