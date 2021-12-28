import warnings
from typing import Union, Tuple, Dict

import pygame
from pygame_gui.core.utility import translate

from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core import UIElement
from pygame_gui.core.drawable_shapes import RectDrawableShape


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
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    """

    def __init__(self, relative_rect: pygame.Rect,
                 text: str,
                 manager: IUIManagerInterface,
                 container: Union[IContainerLikeInterface, None] = None,
                 parent_element: UIElement = None,
                 object_id: Union[ObjectID, str, None] = None,
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

        self.dynamic_width = False
        self.dynamic_height = False
        self.dynamic_dimensions_orig_top_left = relative_rect.topleft

        self.text = text

        # initialise theme params
        self.font = None

        self.bg_colour = None
        self.text_colour = None
        self.disabled_text_colour = None
        self.text_shadow_colour = None

        self.text_shadow_size = 0
        self.text_shadow_offset = (0, 0)

        self.text_horiz_alignment = 'center'
        self.text_vert_alignment = 'center'
        self.text_horiz_alignment_padding = 0
        self.text_vert_alignment_padding = 0

        self.rebuild_from_changed_theme_data()

    def set_text(self, text: str):
        """
        Changes the string displayed by the label element. Labels do not support HTML styling.

        :param text: the text to set the label to.

        """
        if text != self.text:
            self.text = text
            if self.dynamic_width:
                self.rebuild()
            else:
                self.drawable_shape.set_text(translate(self.text))

    def rebuild(self):
        """
        Re-render the text to the label's underlying sprite image. This allows us to change what
        the displayed text is or remake it with different theming (if the theming has changed).
        """

        self.rect.width = -1 if self.dynamic_width else self.rect.width
        self.relative_rect.width = -1 if self.dynamic_width else self.relative_rect.width

        self.rect.height = -1 if self.dynamic_height else self.rect.height
        self.relative_rect.height = -1 if self.dynamic_height else self.relative_rect.height

        text_size = self.font.get_rect(translate(self.text)).size
        if ((self.rect.height != -1 and text_size[1] > self.relative_rect.height) or
                (self.rect.width != -1 and text_size[0] > self.relative_rect.width)):
            width_overlap = self.relative_rect.width - text_size[0]
            height_overlap = self.relative_rect.height - text_size[1]
            warn_text = ('Label Rect is too small for text: '
                         '' + translate(self.text) + ' - size diff: ' + str((width_overlap,
                                                                             height_overlap)))
            warnings.warn(warn_text, UserWarning)

        theming_parameters = {'normal_bg': self.bg_colour,
                              'normal_text': self.text_colour,
                              'normal_text_shadow': self.text_shadow_colour,
                              'normal_border': self.bg_colour,
                              'disabled_text': self.disabled_text_colour,
                              'disabled_text_shadow': self.text_shadow_colour,
                              'disabled_border': self.bg_colour,
                              'disabled_bg': self.bg_colour,
                              'border_width': 0,
                              'shadow_width': 0,
                              'font': self.font,
                              'text': translate(self.text),
                              'text_shadow': (self.text_shadow_size,
                                              self.text_shadow_offset[0],
                                              self.text_shadow_offset[1],
                                              self.text_shadow_colour,
                                              False),
                              'text_horiz_alignment': self.text_horiz_alignment,
                              'text_vert_alignment': self.text_vert_alignment,
                              'text_horiz_alignment_padding': self.text_horiz_alignment_padding,
                              'text_vert_alignment_padding': self.text_vert_alignment_padding}

        self.drawable_shape = RectDrawableShape(self.rect, theming_parameters,
                                                ['normal', 'disabled'], self.ui_manager)
        self.on_fresh_drawable_shape_ready()

        if self.relative_rect.width == -1 or self.relative_rect.height == -1:
            self.dynamic_width = self.relative_rect.width == -1
            self.dynamic_height = self.relative_rect.height == -1

            self.set_dimensions(self.image.get_size())

            # if we have anchored the left side of our button to the right of it's container then
            # changing the width is going to mess up the horiz position as well.
            new_left = self.relative_rect.left
            new_top = self.relative_rect.top
            if self.anchors['left'] == 'right' and self.dynamic_width:
                left_offset = self.dynamic_dimensions_orig_top_left[0]
                new_left = left_offset - self.relative_rect.width
            # if we have anchored the top side of our button to the bottom of it's container then
            # changing the height is going to mess up the vert position as well.
            if self.anchors['top'] == 'bottom' and self.dynamic_height:
                top_offset = self.dynamic_dimensions_orig_top_left[1]
                new_top = top_offset - self.relative_rect.height

            self.set_relative_position((new_left, new_top))

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

        disabled_text_colour = self.ui_theme.get_colour_or_gradient('disabled_text',
                                                                    self.combined_element_ids)
        if disabled_text_colour != self.disabled_text_colour:
            self.disabled_text_colour = disabled_text_colour
            any_changed = True

        bg_colour = self.ui_theme.get_colour_or_gradient('dark_bg', self.combined_element_ids)
        if bg_colour != self.bg_colour:
            self.bg_colour = bg_colour
            any_changed = True

        text_shadow_colour = self.ui_theme.get_colour('text_shadow', self.combined_element_ids)
        if text_shadow_colour != self.text_shadow_colour:
            self.text_shadow_colour = text_shadow_colour
            any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='text_shadow_size',
                                               default_value=0,
                                               casting_func=int):
            any_changed = True

        def tuple_extract(str_data: str) -> Tuple[int, int]:
            return int(str_data.split(',')[0]), int(str_data.split(',')[1])

        if self._check_misc_theme_data_changed(attribute_name='text_shadow_offset',
                                               default_value=(0, 0),
                                               casting_func=tuple_extract):
            any_changed = True

        if self._check_text_alignment_theming():
            any_changed = True

        if any_changed:
            self.rebuild()

    def _check_text_alignment_theming(self) -> bool:
        """
        Checks for any changes in the theming data related to text alignment.

        :return: True if changes found.

        """
        has_any_changed = False

        if self._check_misc_theme_data_changed(attribute_name='text_horiz_alignment',
                                               default_value='center',
                                               casting_func=str):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='text_horiz_alignment_padding',
                                               default_value=0,
                                               casting_func=int):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='text_vert_alignment',
                                               default_value='center',
                                               casting_func=str):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name='text_vert_alignment_padding',
                                               default_value=0,
                                               casting_func=int):
            has_any_changed = True

        return has_any_changed

    def disable(self):
        """
        Disables the label so that its text changes to the disabled colour.
        """
        if self.is_enabled:
            self.is_enabled = False
            self.drawable_shape.set_active_state('disabled')

    def enable(self):
        """
        Re-enables the label so that its text changes to the normal colour
        """
        if not self.is_enabled:
            self.is_enabled = True
            self.drawable_shape.set_active_state('normal')

    def on_locale_changed(self):
        font = self.ui_theme.get_font(self.combined_element_ids)
        if font != self.font:
            self.font = font
            self.rebuild()
        else:
            if self.dynamic_width:
                self.rebuild()
            else:
                self.drawable_shape.set_text(translate(self.text))
