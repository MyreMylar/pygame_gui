import warnings
from typing import Union, Tuple, Dict

import pygame

from pygame_gui._constants import UI_BUTTON_PRESSED, UI_HORIZONTAL_SLIDER_MOVED
from pygame_gui._constants import UI_COLOUR_PICKER_COLOUR_PICKED, UI_TEXT_ENTRY_FINISHED
from pygame_gui._constants import UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED

from pygame_gui.core.interfaces import IUIManagerInterface, IContainerLikeInterface
from pygame_gui.core import UIElement, UIContainer, ObjectID

from pygame_gui.elements import UIWindow, UIButton, UIImage
from pygame_gui.elements import UIHorizontalSlider, UILabel, UITextEntryLine

try:
    # mouse button constants not defined in pygame 1.9.3
    assert pygame.BUTTON_LEFT == 1
    assert pygame.BUTTON_MIDDLE == 2
    assert pygame.BUTTON_RIGHT == 3
except (AttributeError, AssertionError):
    pygame.BUTTON_LEFT = 1
    pygame.BUTTON_MIDDLE = 2
    pygame.BUTTON_RIGHT = 3


class UIColourChannelEditor(UIElement):
    """
    This colour picker specific element lets us edit a single colour channel (Red, Green, Blue,
    Hue etc). It's bundled along with the colour picker class because I don't see much use for it
    outside of a colour picker, but it still seemed sensible to make a class for a pattern in the
    colour picker that is repeated six times.

    :param relative_rect: The relative rectangle for sizing and positioning the element, relative
                          to the anchors.
    :param manager: The UI manager for the UI system.
    :param name: Name for this colour channel, (e.g 'R:' or 'B:'). Used for the label.
    :param channel_index: Index for the colour channel (e.g. red is 0, blue is 1, hue is also 0,
                          saturation is 1)
    :param value_range: Range of values for this channel (0 to 255 for R,G,B - 0 to 360 for hue, 0
                        to 100 for the rest)
    :param initial_value: Starting value for this colour channel.
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
                 relative_rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 name: str,
                 channel_index: int,
                 value_range: Tuple[int, int],
                 initial_value: int,
                 container: Union[IContainerLikeInterface, None] = None,
                 parent_element: UIElement = None,
                 object_id: Union[ObjectID, str, None] = None,
                 anchors: Dict[str, str] = None,
                 visible: int = 1):

        super().__init__(relative_rect,
                         manager,
                         container,
                         starting_height=1,
                         layer_thickness=1,
                         anchors=anchors,
                         visible=visible)

        self._create_valid_ids(container=container,
                               parent_element=parent_element,
                               object_id=object_id,
                               element_id='colour_channel_editor')

        self.range = value_range
        self.current_value = initial_value
        self.channel_index = channel_index

        self.set_image(self.ui_manager.get_universal_empty_surface())

        self.element_container = UIContainer(relative_rect,
                                             self.ui_manager,
                                             container=self.ui_container,
                                             parent_element=self,
                                             anchors=anchors,
                                             visible=self.visible)

        default_sizes = {'space_between': 5,
                         'label_width': 17,
                         'entry_width': 43,
                         'line_height': 29,
                         'slider_height': 21,
                         'slider_vert_space': 4}

        self.label = UILabel(pygame.Rect(0, 0,
                                         default_sizes['label_width'],
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

        self.slider = UIHorizontalSlider(pygame.Rect((default_sizes['label_width'] +
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
        if (event.type == pygame.USEREVENT and
                event.user_type == UI_TEXT_ENTRY_FINISHED and
                event.ui_element == self.entry):

            int_value = self.current_value
            try:
                int_value = int(self.entry.get_text())
            except ValueError:
                int_value = 0
            finally:
                self._set_value_from_entry(int_value)

        if (event.type == pygame.USEREVENT and
                event.user_type == UI_HORIZONTAL_SLIDER_MOVED and
                event.ui_element == self.slider):

            int_value = self.current_value
            try:
                int_value = int(self.slider.get_current_value())
            except ValueError:
                int_value = 0
            finally:
                self._set_value_from_slider(int_value)

        return consumed_event

    def _set_value_from_slider(self, new_value: int):
        """
        For updating the value in the text entry element when we've moved the slider. Also sends
        out an event for the color picker.

        :param new_value: The new value to set.

        """
        clipped_value = min(self.range[1], max(self.range[0], new_value))
        if clipped_value != self.current_value:
            self.current_value = clipped_value
            self.entry.set_text(str(self.current_value))
            event_data = {'user_type': UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED,
                          'value': self.current_value,
                          'channel_index': self.channel_index,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            colour_channel_changed_event = pygame.event.Event(pygame.USEREVENT, event_data)
            pygame.event.post(colour_channel_changed_event)

    def _set_value_from_entry(self, new_value: int):
        """
        For updating the value the slider element is set to when we've edited the text entry. The
        slider may have much less precision than the text entry depending on it's available width
        so we need to be careful to make the change one way. Also sends out an event for the color
        picker and clips the value to within the allowed value range.

        :param new_value: The new value to set.

        """
        clipped_value = min(self.range[1], max(self.range[0], new_value))
        if clipped_value != new_value:
            self.entry.set_text(str(clipped_value))
        if clipped_value != self.current_value:
            self.current_value = clipped_value
            self.slider.set_current_value(self.current_value)
            event_data = {'user_type': UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED,
                          'value': self.current_value,
                          'channel_index': self.channel_index,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            colour_channel_changed_event = pygame.event.Event(pygame.USEREVENT, event_data)
            pygame.event.post(colour_channel_changed_event)

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

    def set_position(self, position: Union[pygame.math.Vector2,
                                           Tuple[int, int],
                                           Tuple[float, float]]):
        """
        Sets the absolute screen position of this channel, updating all subordinate elements at the
        same time.

        :param position: The absolute screen position to set.

        """
        super().set_position(position)
        self.element_container.set_relative_position(self.relative_rect.topleft)

    def set_relative_position(self, position: Union[pygame.math.Vector2,
                                                    Tuple[int, int],
                                                    Tuple[float, float]]):
        """
        Sets the relative screen position of this channel, updating all subordinate elements at the
        same time.

        :param position: The relative screen position to set.

        """
        super().set_relative_position(position)
        self.element_container.set_relative_position(self.relative_rect.topleft)

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2,
                                               Tuple[int, int],
                                               Tuple[float, float]]):
        """
        Method to directly set the dimensions of an element.

        :param dimensions: The new dimensions to set.

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
        super().hide()

        self.element_container.hide()


class UIColourPickerDialog(UIWindow):
    """
    A colour picker window that gives us a small range of UI tools to pick a final colour.

    :param rect: The size and position of the colour picker window. Includes the size of shadow,
                 border and title bar.
    :param manager: The manager for the whole of the UI.
    :param initial_colour: The starting colour for the colour picker, defaults to black.
    :param window_title: The title for the window, defaults to 'Colour Picker'
    :param object_id: The object ID for the window, used for theming - defaults to
                      '#colour_picker_dialog'
    :param visible: Whether the element is visible by default.
    """
    def __init__(self, rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 *,
                 initial_colour: pygame.Color = pygame.Color(0, 0, 0, 255),
                 window_title: str = "pygame-gui.colour_picker_title_bar",
                 object_id: Union[ObjectID, str] = ObjectID('#colour_picker_dialog', None),
                 visible: int = 1):

        super().__init__(rect, manager,
                         window_display_title=window_title,
                         object_id=object_id,
                         resizable=True,
                         visible=visible)

        minimum_dimensions = (390, 390)
        if rect.width < minimum_dimensions[0] or rect.height < minimum_dimensions[1]:
            warn_string = ("Initial size: " + str(rect.size) +
                           " is less than minimum dimensions: " + str(minimum_dimensions))
            warnings.warn(warn_string, UserWarning)
        self.set_minimum_dimensions(minimum_dimensions)

        self.current_colour = initial_colour

        self.ok_button = UIButton(relative_rect=pygame.Rect(-220, -40, 100, 30),
                                  text='pygame-gui.OK',
                                  manager=self.ui_manager,
                                  container=self,
                                  object_id='#ok_button',
                                  anchors={'left': 'right',
                                           'right': 'right',
                                           'top': 'bottom',
                                           'bottom': 'bottom'})

        self.cancel_button = UIButton(relative_rect=pygame.Rect(-110, -40, 100, 30),
                                      text='pygame-gui.Cancel',
                                      manager=self.ui_manager,
                                      container=self,
                                      object_id='#cancel_button',
                                      anchors={'left': 'right',
                                               'right': 'right',
                                               'top': 'bottom',
                                               'bottom': 'bottom'})

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

    def _setup_channels(self, default_sizes):
        # group up setting up the channels, possibly we can make this into a
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
                                                   name='pygame-gui.Value_V:',
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
        user clicking the mouse inside of the Saturation & Value picking square.

        :param event: The pygame Event to process.

        :return: True if event is consumed by this element and should not be passed on to other
                 elements.

        """
        consumed_event = super().process_event(event)
        if (event.type == pygame.USEREVENT and
                event.user_type == UI_BUTTON_PRESSED and
                event.ui_element == self.cancel_button):
            self.kill()

        if (event.type == pygame.USEREVENT and
                event.user_type == UI_BUTTON_PRESSED and
                event.ui_element == self.ok_button):
            event_data = {'user_type': UI_COLOUR_PICKER_COLOUR_PICKED,
                          'colour': self.current_colour,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            new_colour_chosen_event = pygame.event.Event(pygame.USEREVENT, event_data)
            pygame.event.post(new_colour_chosen_event)
            self.kill()

        if (event.type == pygame.USEREVENT and
                event.user_type == UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED):
            if event.ui_element in [self.hue_channel, self.sat_channel, self.value_channel]:
                self.current_colour.hsva = (self.hue_channel.current_value,
                                            self.sat_channel.current_value,
                                            self.value_channel.current_value,
                                            100)
                self.changed_hsv_update_rgb()
                self.update_current_colour_image()
                self.update_saturation_value_square()
            elif event.ui_element in [self.red_channel, self.green_channel, self.blue_channel]:
                self.current_colour[event.channel_index] = event.value
                self.changed_rgb_update_hsv()
                self.update_current_colour_image()
                self.update_saturation_value_square()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            scaled_mouse_pos = self.ui_manager.calculate_scaled_mouse_position(event.pos)
            if self.sat_value_square.rect.collidepoint(scaled_mouse_pos):
                relative_click_pos = [scaled_mouse_pos[0] - self.sat_value_square.rect.left,
                                      scaled_mouse_pos[1] - self.sat_value_square.rect.top]
                # put in range 0 - 100 and reverse y
                x_value = int((relative_click_pos[0] / self.sat_value_square.rect.width) * 100)
                y_value = int((relative_click_pos[1] / self.sat_value_square.rect.height) * 100)
                value = min(100, max(0, x_value))
                saturation = min(100, max(0, 100 - y_value))

                self.sat_channel.set_value(saturation)
                self.value_channel.set_value(value)
                self.current_colour.hsva = (self.hue_channel.current_value,
                                            self.sat_channel.current_value,
                                            self.value_channel.current_value,
                                            100)
                self.changed_hsv_update_rgb()
                self.update_current_colour_image()

        return consumed_event

    def update_current_colour_image(self):
        """
        Updates the 'current colour' image when the current colour has been changed.

        """
        current_colour_surface = pygame.surface.Surface((64, 64), flags=pygame.SRCALPHA, depth=32)
        current_colour_surface.fill(self.current_colour)
        self.current_colour_image.set_image(current_colour_surface)

    def update_saturation_value_square(self):
        """
        Updates the appearance of the big square that lets us visually pick the Saturation and
        Value of our current Hue. This is done by drawing a very small 4x4 pixel square with a
        pattern like so:

                   [black] [hue at max saturation & value)]
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
        self.sat_value_square.set_image(pygame.transform.smoothscale(mini_colour_surf, (200, 200)))

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
