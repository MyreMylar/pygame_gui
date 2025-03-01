import warnings
from typing import Union, Tuple, Dict, Optional

import pygame

from pygame_gui._constants import UI_BUTTON_PRESSED, UI_HORIZONTAL_SLIDER_MOVED
from pygame_gui._constants import UI_COLOUR_PICKER_COLOUR_PICKED, UI_TEXT_ENTRY_FINISHED, UI_2D_SLIDER_MOVED
from pygame_gui._constants import UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED, OldType

from pygame_gui.core.interfaces import IUIManagerInterface, IContainerLikeInterface
from pygame_gui.core.gui_type_hints import Coordinate, RectLike
from pygame_gui.core import UIElement, UIContainer, ObjectID

from pygame_gui.elements import UIWindow, UIButton, UIImage
from pygame_gui.elements import UI2DSlider, UIHorizontalSlider, UILabel, UITextEntryLine


class UIColourChannelEditor(UIElement):
    """
    This colour picker specific element lets us edit a single colour channel (Red, Green, Blue,
    Hue etc.). It's bundled along with the colour picker class because I don't see much use for it
    outside a colour picker, but it still seemed sensible to make a class for a pattern in the
    colour picker that is repeated six times.

    :param relative_rect: The relative rectangle for sizing and positioning the element, relative
                          to the anchors.
    :param name: Name for this colour channel, (e.g 'R:' or 'B:'). Used for the label.
    :param channel_index: Index for the colour channel (e.g. red is 0, blue is 1, hue is also 0,
                          saturation is 1)
    :param value_range: Range of values for this channel (0 to 255 for R,G,B - 0 to 360 for hue, 0
                        to 100 for the rest)
    :param initial_value: Starting value for this colour channel.
    :param manager: The UI manager for the UI system. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param container: UI container for this element.
    :param parent_element: An element to parent this element, used for theming hierarchies and
                           events.
    :param object_id: A specific theming/event ID for this element.
    :param anchors: A dictionary of anchors used for setting up what this element's relative_rect
                    is relative to.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    """
    def __init__(self,
                 relative_rect: RectLike,
                 name: str,
                 channel_index: int,
                 value_range: Tuple[int, int],
                 initial_value: int,
                 manager: Optional[IUIManagerInterface] = None,
                 container: Optional[IContainerLikeInterface] = None,
                 parent_element: Optional[UIElement] = None,
                 object_id: Optional[Union[ObjectID, str]] = None,
                 anchors: Optional[Dict[str, Union[str, UIElement]]] = None,
                 visible: int = 1):
        # Need to move some declarations early as they are indirectly referenced via the ui element
        # constructor when hiding on creation
        self.element_container = None

        super().__init__(relative_rect,
                         manager,
                         container,
                         starting_height=1,
                         layer_thickness=1,
                         anchors=anchors,
                         visible=visible,
                         parent_element=parent_element,
                         object_id=object_id,
                         element_id=['colour_channel_editor'])

        self.range = value_range
        self.current_value = initial_value
        self.channel_index = channel_index

        self._set_image(self.ui_manager.get_universal_empty_surface())

        self.element_container = UIContainer(self.relative_rect,
                                             self.ui_manager,
                                             container=self.ui_container,
                                             parent_element=self,
                                             anchors=anchors,
                                             visible=self.visible)

        default_sizes = {'space_between': 3,
                         'label_width': 17,
                         'entry_width': 43,
                         'line_height': 29,
                         'slider_height': 21,
                         'slider_vert_space': 4}

        self.label = UILabel(pygame.Rect(0, 0,
                                         -1,
                                         default_sizes['line_height']),
                             text=name,
                             manager=self.ui_manager,
                             container=self.element_container,
                             parent_element=self,
                             anchors={'left': 'left',
                                      'right': 'left',
                                      'top': 'top',
                                      'bottom': 'bottom'})

        self.entry = UITextEntryLine(pygame.Rect(-default_sizes['entry_width'],
                                                 0,
                                                 default_sizes['entry_width'],
                                                 default_sizes['line_height']),
                                     manager=self.ui_manager,
                                     container=self.element_container,
                                     parent_element=self,
                                     anchors={'left': 'right',
                                              'right': 'right',
                                              'top': 'top',
                                              'bottom': 'bottom'})

        slider_width = (self.entry.rect.left -
                        self.label.rect.right) - (2 * default_sizes['space_between'])

        self.slider = UIHorizontalSlider(pygame.Rect((self.label.get_abs_rect().width +
                                                      default_sizes['space_between']),
                                                     default_sizes['slider_vert_space'],
                                                     slider_width,
                                                     default_sizes['slider_height']),
                                         start_value=initial_value,
                                         value_range=value_range,
                                         manager=self.ui_manager,
                                         container=self.element_container,
                                         parent_element=self,
                                         anchors={'left': 'left',
                                                  'right': 'right',
                                                  'top': 'top',
                                                  'bottom': 'bottom'})

        self.entry.set_allowed_characters('numbers')
        self.entry.set_text(str(initial_value))
        self.entry.set_text_length_limit(3)

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Handles events that this UI element is interested in. In this case we are responding to the
        slider being moved and the user finishing entering text in the text entry element.

        :param event: The pygame Event to process.

        :return: True if event is consumed by this element and should not be passed on to other
                 elements.

        """
        consumed_event = super().process_event(event)
        if event.type == UI_TEXT_ENTRY_FINISHED and event.ui_element == self.entry:
            int_value = self.current_value
            try:
                int_value = int(self.entry.get_text())
            except ValueError:
                int_value = 0
            finally:
                self._set_value_from_entry(int_value)

        if event.type == UI_HORIZONTAL_SLIDER_MOVED and event.ui_element == self.slider:
            # slider get current value can only return an int or a float so safe to assume cast works
            self._set_value_from_slider(int(self.slider.get_current_value()))

        return consumed_event

    def _set_value_from_slider(self, new_value: int):
        """
        For updating the value in the text entry element when we've moved the slider. Also sends
        out an event for the color picker.

        :param new_value: The new value to set.

        """
        clipped_value = min(self.range[1], max(self.range[0], new_value))

        if clipped_value != self.current_value:
            self.entry.set_text(str(clipped_value))
            self._set_value_and_post_event(clipped_value)

    def _set_value_and_post_event(self, clipped_value):
        self.current_value = clipped_value
        # old event - to be removed in 0.8.0
        event_data = {'user_type': OldType(UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED),
                      'value': self.current_value,
                      'channel_index': self.channel_index,
                      'ui_element': self,
                      'ui_object_id': self.most_specific_combined_id}
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))
        # new event
        event_data = {'value': self.current_value,
                      'channel_index': self.channel_index,
                      'ui_element': self,
                      'ui_object_id': self.most_specific_combined_id}
        pygame.event.post(pygame.event.Event(UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED,
                                             event_data))

    def _set_value_from_entry(self, new_value: int):
        """
        For updating the value the slider element is set to when we've edited the text entry. The
        slider may have much less precision than the text entry depending on its available width,
        so we need to be careful to make the change one way. Also sends out an event for the color
        picker and clips the value to within the allowed value range.

        :param new_value: The new value to set.

        """
        clipped_value = min(self.range[1], max(self.range[0], new_value))
        if clipped_value != new_value:
            self.entry.set_text(str(clipped_value))
        if clipped_value != self.current_value:
            self._change_slider_value_and_fire_event(clipped_value)

    def _change_slider_value_and_fire_event(self, clipped_value):
        self.slider.set_current_value(clipped_value)
        self._set_value_and_post_event(clipped_value)

    def set_value(self, new_value: int):
        """
        For when we need to set the value of the colour channel from outside, usually from
        adjusting the colour elsewhere in the colour picker. Makes sure the new value is within the
        allowed range.

        :param new_value: Value to set.

        """
        clipped_value = min(self.range[1], max(self.range[0], new_value))
        if clipped_value != self.current_value:
            self.current_value = clipped_value
            self.entry.set_text(str(self.current_value))
            self.slider.set_current_value(self.current_value)

    def set_position(self, position: Coordinate):
        """
        Sets the absolute screen position of this channel, updating all subordinate elements at the
        same time.

        :param position: The absolute screen position to set.

        """
        super().set_position(position)
        self.element_container.set_relative_position(self.relative_rect.topleft)

    def set_relative_position(self, position: Coordinate):
        """
        Sets the relative screen position of this channel, updating all subordinate elements at the
        same time.

        :param position: The relative screen position to set.

        """
        super().set_relative_position(position)
        self.element_container.set_relative_position(self.relative_rect.topleft)

    def set_dimensions(self, dimensions: Coordinate, clamp_to_container: bool = False):
        """
        Method to directly set the dimensions of an element.

        :param dimensions: The new dimensions to set.
        :param clamp_to_container: Whether we should clamp the dimensions to the
                                   dimensions of the container or not.

        """
        super().set_dimensions(dimensions)
        self.element_container.set_dimensions(self.relative_rect.size)

    def show(self):
        """
        In addition to the base UIElement.show() - call show() of the element_container
        - which will propagate to the sub-elements - label, entry and slider.
        """
        super().show()

        self.element_container.show()

    def hide(self):
        """
        In addition to the base UIElement.hide() - call hide() of the element_container
        - which will propagate to the sub-elements - label, entry and slider.
        """
        if not self.visible:
            return

        super().hide()
        if self.element_container is not None:
            self.element_container.hide()


class UIColourPickerDialog(UIWindow):
    """
    A colour picker window that gives us a small range of UI tools to pick a final colour.

    :param rect: The size and position of the colour picker window. Includes the size of shadow,
                 border and title bar.
    :param manager: The manager for the whole of the UI. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param initial_colour: The starting colour for the colour picker, defaults to black.
    :param window_title: The title for the window, defaults to 'Colour Picker'
    :param object_id: The object ID for the window, used for theming - defaults to
                      '#colour_picker_dialog'
    :param visible: Whether the element is visible by default.
    """
    def __init__(self, rect: RectLike,
                 manager: Optional[IUIManagerInterface] = None,
                 *,
                 initial_colour: pygame.Color = pygame.Color(0, 0, 0, 255),
                 window_title: str = "pygame-gui.colour_picker_title_bar",
                 object_id: Union[ObjectID, str] = ObjectID('#colour_picker_dialog', None),
                 visible: int = 1,
                 always_on_top: bool = False):

        super().__init__(rect, manager,
                         window_display_title=window_title,
                         element_id=['colour_picker_dialog'],
                         object_id=object_id,
                         resizable=True,
                         visible=visible,
                         always_on_top=always_on_top)

        minimum_dimensions = (390, 390)
        if self.relative_rect.width < minimum_dimensions[0] or self.relative_rect.height < minimum_dimensions[1]:
            warn_string = (f"Initial size: {self.relative_rect.size} "
                           f"is less than minimum dimensions: {minimum_dimensions}")
            warnings.warn(warn_string, UserWarning)
        self.set_minimum_dimensions(minimum_dimensions)

        self.current_colour = initial_colour

        self.cancel_button = UIButton(relative_rect=pygame.Rect(-10, -40, -1, 30),
                                      text='pygame-gui.Cancel',
                                      manager=self.ui_manager,
                                      container=self,
                                      object_id='#cancel_button',
                                      anchors={'left': 'right',
                                               'right': 'right',
                                               'top': 'bottom',
                                               'bottom': 'bottom'})

        self.ok_button = UIButton(relative_rect=pygame.Rect(-10, -40, -1, 30),
                                  text='pygame-gui.OK',
                                  manager=self.ui_manager,
                                  container=self,
                                  object_id='#ok_button',
                                  anchors={'left': 'right',
                                           'right': 'right',
                                           'top': 'bottom',
                                           'bottom': 'bottom',
                                           'right_target': self.cancel_button})

        default_sizes = {'element_spacing': 20,
                         'channel_spacing': 11,
                         'channel_height': 29}

        current_colour_surface = pygame.surface.Surface((64, 64),
                                                        flags=pygame.SRCALPHA, depth=32)
        current_colour_surface.fill(self.current_colour)

        self.current_colour_image = UIImage(pygame.Rect(default_sizes['element_spacing'],
                                                        -100,
                                                        64,
                                                        64),
                                            image_surface=current_colour_surface,
                                            manager=self.ui_manager,
                                            container=self,
                                            anchors={'left': 'left',
                                                     'right': 'left',
                                                     'top': 'bottom',
                                                     'bottom': 'bottom'}
                                            )

        mini_colour_surf = pygame.surface.Surface((2, 2), flags=pygame.SRCALPHA, depth=32)
        mini_colour_surf.fill(pygame.Color(0, 0, 0, 255), pygame.Rect(0, 0, 1, 2))
        mini_colour_surf.fill(pygame.Color(255, 255, 255, 255), pygame.Rect(1, 1, 1, 1))

        hue_colour = pygame.Color(255, 255, 255, 255)
        hue_colour.hsva = (int(self.current_colour.hsva[0]),
                           100, 100, 100)
        mini_colour_surf.fill(hue_colour, pygame.Rect(1, 0, 1, 1))
        self.sat_value_square = UIImage(pygame.Rect(default_sizes['element_spacing'],
                                                    default_sizes['element_spacing'],
                                                    200,
                                                    200),
                                        image_surface=pygame.transform.smoothscale(mini_colour_surf,
                                                                                   (200, 200)),
                                        manager=self.ui_manager,
                                        container=self)

        self.hue_channel = None
        self.sat_channel = None
        self.value_channel = None

        self.red_channel = None
        self.green_channel = None
        self.blue_channel = None

        self._setup_channels(default_sizes)

        self.colour_2d_slider = UI2DSlider(self.sat_value_square.relative_rect,
                                           start_value_x=50, value_range_x=(0, 100),
                                           start_value_y=50, value_range_y=(0, 100),
                                           invert_y=True,
                                           manager=self.ui_manager,
                                           container=self)

        self.update_colour_2d_slider()

    def get_colour(self) -> pygame.Color:
        """
        Get the current colour
        :return:
        """
        return self.current_colour

    def set_colour(self, colour: pygame.Color) -> None:
        """
        Set the current colour and update all the necessary elements
        :param colour: The colour to set
        :return: None
        """
        self.current_colour = colour
        self.changed_hsv_update_rgb()
        self.changed_rgb_update_hsv()
        self._update_colour_image_sv_square_and_2d_slider()

    def _setup_channels(self, default_sizes):
        # Set up the channels, possibly we can make this into a
        # slimmer method called with just the bits that change like names, position and value range.
        channel_width = (self.rect.right -
                         self.sat_value_square.rect.right) - (default_sizes['element_spacing'] * 2)
        channel_left_start = ((default_sizes['element_spacing'] * 2) +
                              self.sat_value_square.rect.width)
        acc_channel_top = default_sizes['element_spacing']
        self.hue_channel = UIColourChannelEditor(pygame.Rect(channel_left_start,
                                                             acc_channel_top,
                                                             channel_width,
                                                             default_sizes['channel_height']),
                                                 manager=self.ui_manager,
                                                 container=self,
                                                 name='pygame-gui.Hue_H',
                                                 channel_index=0,
                                                 initial_value=int(self.current_colour.hsva[0]),
                                                 value_range=(0, 360),
                                                 anchors={'left': 'left',
                                                          'right': 'right',
                                                          'top': 'top',
                                                          'bottom': 'top'})
        acc_channel_top += (default_sizes['channel_height'] +
                            default_sizes['channel_spacing'])
        self.sat_channel = UIColourChannelEditor(pygame.Rect(channel_left_start,
                                                             acc_channel_top,
                                                             channel_width,
                                                             default_sizes['channel_height']),
                                                 manager=self.ui_manager,
                                                 container=self,
                                                 name='pygame-gui.Saturation_S',
                                                 channel_index=0,
                                                 initial_value=int(self.current_colour.hsva[1]),
                                                 value_range=(0, 100),
                                                 anchors={'left': 'left',
                                                          'right': 'right',
                                                          'top': 'top',
                                                          'bottom': 'top'})
        acc_channel_top += (default_sizes['channel_height'] +
                            default_sizes['channel_spacing'])
        self.value_channel = UIColourChannelEditor(pygame.Rect(channel_left_start,
                                                               acc_channel_top,
                                                               channel_width,
                                                               default_sizes['channel_height']),
                                                   manager=self.ui_manager,
                                                   container=self,
                                                   name='pygame-gui.Value_V',
                                                   channel_index=2,
                                                   initial_value=int(self.current_colour.hsva[2]),
                                                   value_range=(0, 100),
                                                   anchors={'left': 'left',
                                                            'right': 'right',
                                                            'top': 'top',
                                                            'bottom': 'top'})
        acc_channel_top += (default_sizes['channel_height'] +
                            default_sizes['channel_spacing'])
        self.red_channel = UIColourChannelEditor(pygame.Rect(channel_left_start,
                                                             acc_channel_top,
                                                             channel_width,
                                                             default_sizes['channel_height']),
                                                 manager=self.ui_manager,
                                                 container=self,
                                                 name='pygame-gui.Red_R',
                                                 channel_index=0,
                                                 initial_value=self.current_colour.r,
                                                 value_range=(0, 255),
                                                 anchors={'left': 'left',
                                                          'right': 'right',
                                                          'top': 'top',
                                                          'bottom': 'top'})
        acc_channel_top += (default_sizes['channel_height'] +
                            default_sizes['channel_spacing'])
        self.green_channel = UIColourChannelEditor(pygame.Rect(channel_left_start,
                                                               acc_channel_top,
                                                               channel_width,
                                                               default_sizes['channel_height']),
                                                   manager=self.ui_manager,
                                                   container=self,
                                                   name='pygame-gui.Green_G',
                                                   channel_index=1,
                                                   initial_value=self.current_colour.g,
                                                   value_range=(0, 255),
                                                   anchors={'left': 'left',
                                                            'right': 'right',
                                                            'top': 'top',
                                                            'bottom': 'top'})
        acc_channel_top += (default_sizes['channel_height'] +
                            default_sizes['channel_spacing'])
        self.blue_channel = UIColourChannelEditor(pygame.Rect(channel_left_start,
                                                              acc_channel_top,
                                                              channel_width,
                                                              default_sizes['channel_height']),
                                                  manager=self.ui_manager,
                                                  container=self,
                                                  name='pygame-gui.Blue_B',
                                                  channel_index=2,
                                                  initial_value=self.current_colour.b,
                                                  value_range=(0, 255),
                                                  anchors={'left': 'left',
                                                           'right': 'right',
                                                           'top': 'top',
                                                           'bottom': 'top'})

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Handles events that this UI element is interested in. In this case we are responding to
        the colour channel elements being changed, the OK or Cancel buttons being pressed or the
        user clicking the mouse inside the Saturation & Value picking square.

        :param event: The pygame Event to process.

        :return: True if event is consumed by this element and should not be passed on to other
                 elements.

        """
        consumed_event = super().process_event(event)
        if event.type == UI_BUTTON_PRESSED and event.ui_element == self.cancel_button:
            self.kill()

        if event.type == UI_BUTTON_PRESSED and event.ui_element == self.ok_button:
            # old event - to be removed in 0.8.0
            event_data = {'user_type': OldType(UI_COLOUR_PICKER_COLOUR_PICKED),
                          'colour': self.current_colour,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))
            # new event
            event_data = {'colour': self.current_colour,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            pygame.event.post(pygame.event.Event(UI_COLOUR_PICKER_COLOUR_PICKED, event_data))
            self.kill()

        if event.type == UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED:
            if event.ui_element in [self.hue_channel, self.sat_channel, self.value_channel]:
                self.current_colour.hsva = (self.hue_channel.current_value,
                                            self.sat_channel.current_value,
                                            self.value_channel.current_value,
                                            100)
                self.changed_hsv_update_rgb()
            elif event.ui_element in [self.red_channel, self.green_channel, self.blue_channel]:
                self.current_colour[event.channel_index] = event.value
                self.changed_rgb_update_hsv()

            self._update_colour_image_sv_square_and_2d_slider()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            scaled_mouse_pos = self.ui_manager.calculate_scaled_mouse_position(event.pos)
            rect = self.sat_value_square.rect
            extended_rect = pygame.Rect(rect.x, rect.y, rect.w + 1, rect.h + 1)
            if extended_rect.collidepoint(scaled_mouse_pos):
                self._set_colours_from_mouse_pos(scaled_mouse_pos)
        if event.type == UI_2D_SLIDER_MOVED and event.ui_element == self.colour_2d_slider:
            v, s = self.colour_2d_slider.get_current_value()
            self._set_colours_from_value_sat(v, s)
        return consumed_event

    def _update_colour_image_sv_square_and_2d_slider(self):
        self.update_current_colour_image()
        self.update_saturation_value_square()
        self.update_colour_2d_slider()

    def _set_colours_from_value_sat(self,  value, saturation):
        self.sat_channel.set_value(saturation)
        self.value_channel.set_value(value)
        self.current_colour.hsva = (self.hue_channel.current_value,
                                    self.sat_channel.current_value,
                                    self.value_channel.current_value,
                                    100)
        self.changed_hsv_update_rgb()
        self.update_current_colour_image()

    def _set_colours_from_mouse_pos(self, scaled_mouse_pos):
        relative_click_pos = [scaled_mouse_pos[0] - self.sat_value_square.rect.left,
                              scaled_mouse_pos[1] - self.sat_value_square.rect.top]
        # put in range 0 - 100 and reverse y
        x_value = int((relative_click_pos[0] / self.sat_value_square.rect.width) * 100)
        y_value = int((relative_click_pos[1] / self.sat_value_square.rect.height) * 100)
        saturation = min(100, max(0, 100 - y_value))
        value = min(100, max(0, x_value))
        
        self._set_colours_from_value_sat(value, saturation)
        # Update 2D slider values
        self.update_colour_2d_slider()

    def update_current_colour_image(self):
        """
        Updates the 'current colour' image when the current colour has been changed.

        """
        current_colour_surface = pygame.surface.Surface((64, 64), flags=pygame.SRCALPHA, depth=32)
        current_colour_surface.fill(self.current_colour)
        self.current_colour_image._set_image(current_colour_surface)

    def update_saturation_value_square(self):
        """
        Updates the appearance of the big square that lets us visually pick the Saturation and
        Value of our current Hue. This is done by drawing a very small 4x4 pixel square with a
        pattern like so:

                   [black] [hue at max saturation & value]
                   [black] [white]

        And then using the smoothscale transform to enlarge it so that the colours blend smoothly
        from one to the other.
        """
        mini_colour_surf = pygame.surface.Surface((2, 2), flags=pygame.SRCALPHA, depth=32)
        mini_colour_surf.fill(pygame.Color(0, 0, 0, 255), pygame.Rect(0, 0, 1, 2))
        mini_colour_surf.fill(pygame.Color(255, 255, 255, 255), pygame.Rect(1, 1, 1, 1))

        hue_colour = pygame.Color(255, 255, 255, 255)
        hue_colour.hsva = (int(self.hue_channel.current_value),
                           100, 100, 100)
        mini_colour_surf.fill(hue_colour, pygame.Rect(1, 0, 1, 1))
        self.sat_value_square._set_image(pygame.transform.smoothscale(mini_colour_surf, (200, 200)))

    def update_colour_2d_slider(self):
        """
        This is used to update the 2D slider from the sliders
        :return: None
        """
        s, v = self.sat_channel.current_value, self.value_channel.current_value
        self.colour_2d_slider.set_current_value(v, s)

    def changed_hsv_update_rgb(self):
        """
        Updates the RGB channels when we've altered the HSV ones.

        """
        self.red_channel.set_value(self.current_colour.r)
        self.green_channel.set_value(self.current_colour.g)
        self.blue_channel.set_value(self.current_colour.b)

    def changed_rgb_update_hsv(self):
        """
        Updates the HSV channels when we've altered the RGB ones.

        """
        self.hue_channel.set_value(int(self.current_colour.hsva[0]))
        self.sat_channel.set_value(int(self.current_colour.hsva[1]))
        self.value_channel.set_value(int(self.current_colour.hsva[2]))
