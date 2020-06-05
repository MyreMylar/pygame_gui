import warnings
from typing import Union, Tuple, Dict

import pygame

from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core import ColourGradient, UIElement
from pygame_gui.core.utility import render_white_text_alpha_black_bg, apply_colour_to_surface
from pygame_gui.core.utility import basic_blit


class UILabel(UIElement):
    """
    A label lets us display a single line of text with a single font style. It's a quick to
    rebuild and simple alternative to the text box element.

    :param relative_rect: The rectangle that contains and positions the label relative to it's
                          container.
    :param text: The text to display in the label.
    :param manager: The UIManager that manages this label.
    :param container: The container that this element is within. If set to None will be the root
                      window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param visible: Whether the element is visible by default. Warning - container visibility may override this.
    """

    def __init__(self, relative_rect: pygame.Rect,
                 text: str,
                 manager: IUIManagerInterface,
                 container: Union[IContainerLikeInterface, None] = None,
                 parent_element: UIElement = None,
                 object_id: Union[str, None] = None,
                 anchors: Dict[str, str] = None,
                 visible: int = 1):

        super().__init__(relative_rect, manager, container,
                         starting_height=1,
                         layer_thickness=1,
                         anchors=anchors,
                         visible=visible)

        self._create_valid_ids(container=container,
                               parent_element=parent_element,
                               object_id=object_id,
                               element_id='label')
        self.text = text

        # initialise theme params
        self.font = None

        self.bg_colour = None
        self.text_colour = None
        self.text_shadow_colour = None

        self.text_shadow = False
        self.text_shadow_size = 1
        self.text_shadow_offset = (0, 0)

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
        Re-render the text to the label's underlying sprite image. This allows us to change what
        the displayed text is or remake it with different theming (if the theming has changed).
        """

        text_size = self.font.size(self.text)
        if text_size[1] > self.relative_rect.height or text_size[0] > self.relative_rect.width:
            width_overlap = self.relative_rect.width - text_size[0]
            height_overlap = self.relative_rect.height - text_size[1]
            warn_text = ('Label Rect is too small for text: '
                         '' + self.text + ' - size diff: ' + str((width_overlap, height_overlap)))
            warnings.warn(warn_text, UserWarning)

        new_image = pygame.Surface(self.relative_rect.size, flags=pygame.SRCALPHA, depth=32)

        if isinstance(self.bg_colour, ColourGradient):
            new_image.fill(pygame.Color('#FFFFFFFF'))
            self.bg_colour.apply_gradient_to_surface(new_image)
            text_render = render_white_text_alpha_black_bg(self.font, self.text)
            if isinstance(self.text_colour, ColourGradient):
                self.text_colour.apply_gradient_to_surface(text_render)
            else:
                apply_colour_to_surface(self.text_colour, text_render)
        elif isinstance(self.text_colour, ColourGradient):
            new_image.fill(self.bg_colour)
            text_render = render_white_text_alpha_black_bg(self.font, self.text)
            self.text_colour.apply_gradient_to_surface(text_render)
        else:
            new_image.fill(self.bg_colour)
            if self.bg_colour.a != 255 or self.text_shadow:
                text_render = render_white_text_alpha_black_bg(self.font, self.text)
                apply_colour_to_surface(self.text_colour, text_render)
            else:
                text_render = self.font.render(self.text, True, self.text_colour, self.bg_colour)
                text_render = text_render.convert_alpha()
        text_render_rect = text_render.get_rect(centerx=int(self.rect.width / 2),
                                                centery=int(self.rect.height / 2))

        if self.text_shadow:
            shadow_text_render = render_white_text_alpha_black_bg(self.font, self.text)
            apply_colour_to_surface(self.text_shadow_colour, shadow_text_render)

            for y_pos in range(-self.text_shadow_size, self.text_shadow_size + 1):
                shadow_text_rect = pygame.Rect((text_render_rect.x + self.text_shadow_offset[0],
                                                text_render_rect.y + self.text_shadow_offset[1]
                                                + y_pos),
                                               text_render_rect.size)
                basic_blit(new_image, shadow_text_render, shadow_text_rect)

            for x_pos in range(-self.text_shadow_size, self.text_shadow_size + 1):
                shadow_text_rect = pygame.Rect((text_render_rect.x + self.text_shadow_offset[0]
                                                + x_pos,
                                                text_render_rect.y + self.text_shadow_offset[1]),
                                               text_render_rect.size)
                basic_blit(new_image, shadow_text_render, shadow_text_rect)

            for x_and_y in range(-self.text_shadow_size, self.text_shadow_size + 1):
                shadow_text_rect = pygame.Rect(
                    (text_render_rect.x + self.text_shadow_offset[0] + x_and_y,
                     text_render_rect.y + self.text_shadow_offset[1] + x_and_y),
                    text_render_rect.size)
                basic_blit(new_image, shadow_text_render, shadow_text_rect)

            for x_and_y in range(-self.text_shadow_size, self.text_shadow_size + 1):
                shadow_text_rect = pygame.Rect(
                    (text_render_rect.x + self.text_shadow_offset[0] - x_and_y,
                     text_render_rect.y + self.text_shadow_offset[1] + x_and_y),
                    text_render_rect.size)
                basic_blit(new_image, shadow_text_render, shadow_text_rect)

        basic_blit(new_image, text_render, text_render_rect)

        self.set_image(new_image)

    def rebuild_from_changed_theme_data(self):
        """
        Checks if any theming parameters have changed, and if so triggers a full rebuild of
        the element.

        """
        super().rebuild_from_changed_theme_data()
        any_changed = False

        font = self.ui_theme.get_font(self.combined_element_ids)
        if font != self.font:
            self.font = font
            any_changed = True

        text_colour = self.ui_theme.get_colour_or_gradient('normal_text', self.combined_element_ids)
        if text_colour != self.text_colour:
            self.text_colour = text_colour
            any_changed = True

        bg_colour = self.ui_theme.get_colour_or_gradient('dark_bg', self.combined_element_ids)
        if bg_colour != self.bg_colour:
            self.bg_colour = bg_colour
            any_changed = True

        text_shadow_colour = self.ui_theme.get_colour('text_shadow', self.combined_element_ids)
        if text_shadow_colour != self.text_shadow_colour:
            self.text_shadow_colour = text_shadow_colour
            any_changed = True

        def parse_to_bool(str_data: str):
            return bool(int(str_data))

        if self._check_misc_theme_data_changed(attribute_name='text_shadow',
                                               default_value=False,
                                               casting_func=parse_to_bool):
            any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='text_shadow_size',
                                               default_value=1,
                                               casting_func=int):
            any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='text_shadow_size',
                                               default_value=1,
                                               casting_func=int):
            any_changed = True

        def tuple_extract(str_data: str) -> Tuple[int, int]:
            return int(str_data.split(',')[0]), int(str_data.split(',')[1])

        if self._check_misc_theme_data_changed(attribute_name='text_shadow_offset',
                                               default_value=(0, 0),
                                               casting_func=tuple_extract):
            any_changed = True

        if any_changed:
            self.rebuild()

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2,
                                               Tuple[int, int],
                                               Tuple[float, float]]):
        """
        Method to directly set the dimensions of a label.

        :param dimensions: The new dimensions to set.

        """
        super().set_dimensions(dimensions)

        if dimensions[0] >= 0 and dimensions[1] >= 0:
            self.rebuild()
