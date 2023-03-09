import warnings
from typing import Union, Tuple, Dict, Optional, Any

import pygame
from pygame_gui.core.utility import translate

from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core.interfaces import IUITextOwnerInterface
from pygame_gui.core import UIElement
from pygame_gui.core.drawable_shapes import RectDrawableShape

from pygame_gui._constants import UITextEffectType, TEXT_EFFECT_TYPING_APPEAR
from pygame_gui._constants import TEXT_EFFECT_FADE_IN, TEXT_EFFECT_FADE_OUT
from pygame_gui.core.text.text_effects import TypingAppearEffect, FadeInEffect, FadeOutEffect
from pygame_gui.core.text import TextLineChunkFTFont


class UILabel(UIElement, IUITextOwnerInterface):
    """
    A label lets us display a single line of text with a single font style. It's a quick to
    rebuild and simple alternative to the text box element.

    :param relative_rect: The rectangle that contains and positions the label relative to it's
                          container.
    :param text: The text to display in the label.
    :param manager: The UIManager that manages this label. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param container: The container that this element is within. If not provided or set to None
                      will be the root window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    :param text_kwargs: a dictionary of variable arguments to pass to the translated string
                        useful when you have multiple translations that need variables inserted
                        in the middle.
    """

    def __init__(self, relative_rect: pygame.Rect,
                 text: str,
                 manager: Optional[IUIManagerInterface] = None,
                 container: Optional[IContainerLikeInterface] = None,
                 parent_element: Optional[UIElement] = None,
                 object_id: Optional[Union[ObjectID, str]] = None,
                 anchors: Optional[Dict[str, Union[str, UIElement]]] = None,
                 visible: int = 1,
                 *,
                 text_kwargs: Optional[Dict[str, str]] = None):

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
        self.text_kwargs = {}
        if text_kwargs is not None:
            self.text_kwargs = text_kwargs

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

        self.active_text_effect = None

        self.rebuild_from_changed_theme_data()

    def set_text(self, text: str, *, text_kwargs: Optional[Dict[str, str]] = None):
        """
        Changes the string displayed by the label element. Labels do not support HTML styling.

        :param text: the text to set the label to.
        :param text_kwargs: a dictionary of variable arguments to pass to the translated string
                            useful when you have multiple translations that need variables inserted
                            in the middle.

        """
        any_changed = False
        if text != self.text:
            self.text = text
            any_changed = True
        if text_kwargs is not None:
            if text_kwargs != self.text_kwargs:
                self.text_kwargs = text_kwargs
                any_changed = True
        elif self.text_kwargs != {}:
            self.text_kwargs = {}
            any_changed = True

        if any_changed:
            if self.dynamic_width:
                self.rebuild()
            else:
                self.drawable_shape.set_text(translate(self.text, **self.text_kwargs))

    def rebuild(self):
        """
        Re-render the text to the label's underlying sprite image. This allows us to change what
        the displayed text is or remake it with different theming (if the theming has changed).
        """

        self.rect.width = -1 if self.dynamic_width else self.rect.width
        self.relative_rect.width = -1 if self.dynamic_width else self.relative_rect.width

        self.rect.height = -1 if self.dynamic_height else self.rect.height
        self.relative_rect.height = -1 if self.dynamic_height else self.relative_rect.height

        text_size = self.font.size(translate(self.text, **self.text_kwargs))
        if ((self.rect.height != -1 and text_size[1] > self.relative_rect.height) or
                (self.rect.width != -1 and text_size[0] > self.relative_rect.width)):
            width_overlap = self.relative_rect.width - text_size[0]
            height_overlap = self.relative_rect.height - text_size[1]
            warn_text = ('Label Rect is too small for text: '
                         '' + translate(self.text, **self.text_kwargs) + ' - size diff: ' + str((width_overlap,
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
                              'text': translate(self.text, **self.text_kwargs),
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

        if self._check_misc_theme_data_changed(attribute_name='text_shadow_offset',
                                               default_value=(0, 0),
                                               casting_func=self.tuple_extract):
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
                self.drawable_shape.set_text(translate(self.text, **self.text_kwargs))

    def update(self, time_delta: float):
        """
        Called once every update loop of the UI Manager.

        :param time_delta: The time in seconds between calls to update. Useful for timing things.

        """
        super().update(time_delta)
        self.update_text_effect(time_delta)

    # -------------------------------------------------
    # The Text owner interface
    # -------------------------------------------------
    def set_text_alpha(self, alpha: int, sub_chunk: Optional[TextLineChunkFTFont] = None):
        self.drawable_shape.set_text_alpha(alpha)

    def set_text_offset_pos(self, offset: Tuple[int, int],
                            sub_chunk: Optional[TextLineChunkFTFont] = None):
        pass

    def set_text_rotation(self, rotation: int,
                          sub_chunk: Optional[TextLineChunkFTFont] = None):
        pass

    def set_text_scale(self, scale: int,
                       sub_chunk: Optional[TextLineChunkFTFont] = None):
        pass

    def clear_text_surface(self, sub_chunk: Optional[TextLineChunkFTFont] = None):
        self.drawable_shape.text_box_layout.clear_final_surface()
        self.drawable_shape.text_box_layout.finalise_to_new()
        self.drawable_shape.redraw_active_state_no_text()

    def get_text_letter_count(self, sub_chunk: Optional[TextLineChunkFTFont] = None) -> int:
        return self.drawable_shape.text_box_layout.letter_count

    def update_text_end_position(self, end_pos: int,
                                 sub_chunk: Optional[TextLineChunkFTFont] = None):
        self.drawable_shape.text_box_layout.current_end_pos = end_pos
        self.drawable_shape.text_box_layout.finalise_to_new()
        self.drawable_shape.finalise_text_onto_active_state()

    def set_active_effect(self, effect_type: Optional[UITextEffectType],
                          params: Optional[Dict[str, Any]] = None,
                          effect_tag: Optional[str] = None):
        if effect_tag is not None:
            warnings.warn('UILabels do not support effect tags', category=UserWarning)

        if self.active_text_effect is not None:
            self.clear_all_active_effects()
        if effect_type is None:
            self.active_text_effect = None
        elif isinstance(effect_type, UITextEffectType):
            if effect_type == TEXT_EFFECT_TYPING_APPEAR:
                effect = TypingAppearEffect(self, params)
                self.active_text_effect = effect
            elif effect_type == TEXT_EFFECT_FADE_IN:
                effect = FadeInEffect(self, params)
                self.active_text_effect = effect
            elif effect_type == TEXT_EFFECT_FADE_OUT:
                effect = FadeOutEffect(self, params)
                self.active_text_effect = effect
            else:
                warnings.warn('Unsupported effect name: ' + str(effect_type) + ' for label', category=UserWarning)
        else:
            warnings.warn('Unsupported effect name: ' + str(effect_type) + ' for label', category=UserWarning)

        if self.active_text_effect is not None:
            self.active_text_effect.text_changed = True
            self.update_text_effect(0.0)

    def stop_finished_effect(self, sub_chunk: Optional[TextLineChunkFTFont] = None):
        self.active_text_effect = None

    def clear_all_active_effects(self, sub_chunk: Optional[TextLineChunkFTFont] = None):
        self.drawable_shape.text_box_layout.clear_effects()
        self.active_text_effect = None
        self.rebuild()

    def update_text_effect(self, time_delta: float):
        if self.active_text_effect is not None:
            self.active_text_effect.update(time_delta)
            # update can set effect to None
            if (self.active_text_effect is not None and
                    self.active_text_effect.has_text_changed()):
                self.active_text_effect.apply_effect()
                self.on_fresh_drawable_shape_ready()

    def get_object_id(self) -> str:
        return self.most_specific_combined_id
