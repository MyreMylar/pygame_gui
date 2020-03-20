from typing import Union, Tuple, Dict

import pygame
import pygame_gui

from pygame_gui.core.interfaces import IUIManagerInterface, IContainerLikeInterface
from pygame_gui.core import UIElement, UIContainer

from pygame_gui.elements import UIWindow, UIButton, UIImage, UIHorizontalSlider, UILabel, UITextEntryLine


class UIColourChannelEditor(UIElement):
    """
    This colour picker specific element lets us edit a single colour channel (Red, Green, Blue, Hue etc). It's bundled
    along with the colour picker class because I don't see much use for it outside of a colour picker, but it still
    seemed sensible to make a class for a pattern in the colour picker that is repeated six times.

    :param relative_rect: The relative rectangle for sizing and positioning the element, relative to the anchors.
    :param manager: The UI manager for the UI system.
    :param name: Name for this colour channel, (e.g 'R:' or 'B:'). Used for the label.
    :param channel_index: Index for the colour channel (e.g. red is 0, blue is 1, hue is also 0, saturation is 1)
    :param value_range: Range of values for this channel (0 to 255 for R,G,B - 0 to 360 for hue, 0 to 100 for the rest)
    :param initial_value: Starting value for this colour channel.
    :param container: UI container for this element.
    :param parent_element: An element to parent this element, used for theming hierarchies and events.
    :param object_id: A specific theming/event ID for this element.
    :param anchors: A dictionary of anchors used for setting up what this element's relative_rect is relative to.
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
                 object_id: Union[str, None] = None,
                 anchors: Dict[str, str] = None):

        new_element_ids, new_object_ids = self.create_valid_ids(container=container,
                                                                parent_element=parent_element,
                                                                object_id=object_id,
                                                                element_id='colour_channel_editor')
        super().__init__(relative_rect,
                         manager,
                         container,
                         starting_height=1,
                         layer_thickness=1,
                         element_ids=new_element_ids,
                         object_ids=new_object_ids,
                         anchors=anchors)

        self.range = value_range
        self.current_value = initial_value
        self.channel_index = channel_index

        self.set_image(self.ui_manager.get_universal_empty_surface())

        self.element_container = UIContainer(relative_rect,
                                             self.ui_manager,
                                             container=self.ui_container,
                                             parent_element=self,
                                             anchors=anchors)

        # TODO: alter this so that the labels and text entry boxes are fixed width based on the font and the slider
        #  expands to fill the space in between.

        space_between = 5
        width_without_spacing = self.element_container.relative_rect.width - (2 * space_between)
        slider_width = int(9 * (width_without_spacing / 16))
        label_width = int(2 * (width_without_spacing / 16))
        entry_width = int(5 * (width_without_spacing / 16))
        everything_else_height = 29
        slider_height = 21
        self.slider = UIHorizontalSlider(pygame.Rect(-(slider_width + space_between + entry_width), 4,
                                                     slider_width, slider_height),
                                         start_value=initial_value,
                                         value_range=value_range,
                                         manager=self.ui_manager,
                                         container=self.element_container,
                                         parent_element=self,
                                         anchors={'left': 'right',
                                                  'right': 'right',
                                                  'top': 'top',
                                                  'bottom': 'bottom'})

        self.label = UILabel(pygame.Rect(0, 0, label_width, everything_else_height),
                             text=name,
                             manager=self.ui_manager,
                             container=self.element_container,
                             parent_element=self,
                             anchors={'left': 'left',
                                      'right': 'left',
                                      'top': 'top',
                                      'bottom': 'bottom'})

        self.entry = UITextEntryLine(pygame.Rect(-entry_width, 0, entry_width, everything_else_height),
                                     manager=self.ui_manager,
                                     container=self.element_container,
                                     parent_element=self,
                                     anchors={'left': 'right',
                                              'right': 'right',
                                              'top': 'top',
                                              'bottom': 'bottom'})
        self.entry.set_allowed_characters('numbers')
        self.entry.set_text(str(initial_value))
        self.entry.set_text_length_limit(3)

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Handles events that this UI element is interested in. In this case we are responding to the slider being moved
        and the user finishing entering text in the text entry element.

        :param event: The pygame Event to process.
        :return: True if event is consumed by this element and should not be passed on to other elements.
        """
        consumed_event = super().process_event(event)
        if (event.type == pygame.USEREVENT and
                event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED and
                event.ui_element == self.entry):

            try:
                int_value = int(self.entry.get_text())
            except ValueError:
                int_value = 0
            self._set_value_from_entry(int_value)

        if (event.type == pygame.USEREVENT and
                event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED and
                event.ui_element == self.slider):
            try:
                int_value = int(self.slider.get_current_value())
            except ValueError:
                int_value = 0
            self._set_value_from_slider(int_value)

        return consumed_event

    def _set_value_from_slider(self, new_value: int):
        """
        For updating the value in the text entry element when we've moved the slider. Also sends out an event for the
        color picker.

        :param new_value: The new value to set.
        """
        clipped_value = min(self.range[1], max(self.range[0], new_value))
        if clipped_value != self.current_value:
            self.current_value = clipped_value
            self.entry.set_text(str(self.current_value))
            event_data = {'user_type': pygame_gui.UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED,
                          'value': self.current_value,
                          'channel_index': self.channel_index,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            colour_channel_changed_event = pygame.event.Event(pygame.USEREVENT, event_data)
            pygame.event.post(colour_channel_changed_event)

    def _set_value_from_entry(self, new_value: int):
        """
        For updating the value the slider element is set to when we've edited the text entry. The slider may have much
        less precision than the text entry depending on it's available width so we need to be careful to make the change
        one way. Also sends out an event for the color picker and clips the value to within the allowed value range.

        :param new_value: The new value to set.
        """
        clipped_value = min(self.range[1], max(self.range[0], new_value))
        if clipped_value != new_value:
            self.entry.set_text(str(clipped_value))
        if clipped_value != self.current_value:
            self.current_value = clipped_value
            self.slider.set_current_value(self.current_value)
            event_data = {'user_type': pygame_gui.UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED,
                          'value': self.current_value,
                          'channel_index': self.channel_index,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            colour_channel_changed_event = pygame.event.Event(pygame.USEREVENT, event_data)
            pygame.event.post(colour_channel_changed_event)

    def set_value(self, new_value: int):
        """
        For when we need to set the value of the colour channel from outside, usually from adjusting the colour
        elsewhere in the colour picker. Makes sure the new value is within the allowed range.

        :param new_value:
        """
        clipped_value = min(self.range[1], max(self.range[0], new_value))
        if clipped_value != self.current_value:
            self.current_value = clipped_value
            self.entry.set_text(str(self.current_value))
            self.slider.set_current_value(self.current_value)


class UIColourPickerDialog(UIWindow):
    """
    A colour picker window that gives us a small range of UI tools to pick a final colour.

    TODO: specify the minimum dimensions with the default font somewhere in here?
    TODO: Also scale what needs scaling with the window. Enable resizing to test.

    :param rect: The size and position of the colour picker window. Includes the size of shadow, border and title bar.
    :param manager: The manager for the whole of the UI.
    :param initial_colour: The starting colour for the colour picker, defaults to black.
    :param window_title: The title for the window, defaults to 'Colour Picker'
    :param object_id: The object ID for the window, used for theming - defaults to '#colour_picker_dialog'
    """
    def __init__(self, rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 *,
                 initial_colour: pygame.Color = pygame.Color(0, 0, 0, 255),
                 window_title: str = "Colour Picker",
                 object_id: str = '#colour_picker_dialog'):

        super().__init__(rect, manager,
                         window_display_title=window_title,
                         object_id=object_id,
                         resizable=True)

        self.current_colour = initial_colour

        self.ok_button = UIButton(relative_rect=pygame.Rect(-220, -40, 100, 30),
                                  text='OK',
                                  manager=self.ui_manager,
                                  container=self,
                                  anchors={'left': 'right',
                                           'right': 'right',
                                           'top': 'bottom',
                                           'bottom': 'bottom'})

        self.cancel_button = UIButton(relative_rect=pygame.Rect(-110, -40, 100, 30),
                                      text='Cancel',
                                      manager=self.ui_manager,
                                      container=self,
                                      anchors={'left': 'right',
                                               'right': 'right',
                                               'top': 'bottom',
                                               'bottom': 'bottom'})

        current_colour_surface = pygame.Surface((64, 64))
        current_colour_surface.fill(self.current_colour)

        self.current_colour_image = UIImage(pygame.Rect(20, -100, 64, 64),
                                            image_surface=current_colour_surface,
                                            manager=self.ui_manager,
                                            container=self,
                                            anchors={'left': 'left',
                                                     'right': 'left',
                                                     'top': 'bottom',
                                                     'bottom': 'bottom'}
                                            )

        self.hue_channel = UIColourChannelEditor(pygame.Rect(-160, 20, 150, 29),
                                                 manager=self.ui_manager,
                                                 container=self,
                                                 name='H:',
                                                 channel_index=0,
                                                 initial_value=int(self.current_colour.hsva[0]),
                                                 value_range=(0, 360),
                                                 anchors={'left': 'right',
                                                          'right': 'right',
                                                          'top': 'top',
                                                          'bottom': 'top'})

        self.saturation_channel = UIColourChannelEditor(pygame.Rect(-160, 60, 150, 29),
                                                        manager=self.ui_manager,
                                                        container=self,
                                                        name='S:',
                                                        channel_index=0,
                                                        initial_value=int(self.current_colour.hsva[1]),
                                                        value_range=(0, 100),
                                                        anchors={'left': 'right',
                                                                 'right': 'right',
                                                                 'top': 'top',
                                                                 'bottom': 'top'})

        self.value_channel = UIColourChannelEditor(pygame.Rect(-160, 100, 150, 29),
                                                   manager=self.ui_manager,
                                                   container=self,
                                                   name='V:',
                                                   channel_index=2,
                                                   initial_value=int(self.current_colour.hsva[2]),
                                                   value_range=(0, 100),
                                                   anchors={'left': 'right',
                                                            'right': 'right',
                                                            'top': 'top',
                                                            'bottom': 'top'})

        self.red_channel = UIColourChannelEditor(pygame.Rect(-160, 140, 150, 29),
                                                 manager=self.ui_manager,
                                                 container=self,
                                                 name='R:',
                                                 channel_index=0,
                                                 initial_value=self.current_colour.r,
                                                 value_range=(0, 255),
                                                 anchors={'left': 'right',
                                                          'right': 'right',
                                                          'top': 'top',
                                                          'bottom': 'top'})

        self.green_channel = UIColourChannelEditor(pygame.Rect(-160, 180, 150, 29),
                                                   manager=self.ui_manager,
                                                   container=self,
                                                   name='G:',
                                                   channel_index=1,
                                                   initial_value=self.current_colour.g,
                                                   value_range=(0, 255),
                                                   anchors={'left': 'right',
                                                            'right': 'right',
                                                            'top': 'top',
                                                            'bottom': 'top'})

        self.blue_channel = UIColourChannelEditor(pygame.Rect(-160, 220, 150, 29),
                                                  manager=self.ui_manager,
                                                  container=self,
                                                  name='B:',
                                                  channel_index=2,
                                                  initial_value=self.current_colour.b,
                                                  value_range=(0, 255),
                                                  anchors={'left': 'right',
                                                           'right': 'right',
                                                           'top': 'top',
                                                           'bottom': 'top'})

        mini_colour_surf = pygame.Surface((2, 2))
        mini_colour_surf.fill(pygame.Color(0, 0, 0, 255), pygame.Rect(0, 0, 1, 2))
        mini_colour_surf.fill(pygame.Color(255, 255, 255, 255), pygame.Rect(1, 1, 1, 1))

        hue_colour = pygame.Color(255, 255, 255, 255)
        hue_colour.hsva = (int(self.hue_channel.current_value),
                           100, 100, 100)
        mini_colour_surf.fill(hue_colour, pygame.Rect(1, 0, 1, 1))
        colour_square_surface = pygame.transform.smoothscale(mini_colour_surf, (200, 200))
        self.saturation_value_square = UIImage(pygame.Rect(20, 20, 200, 200),
                                               image_surface=colour_square_surface,
                                               manager=self.ui_manager,
                                               container=self)

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Handles events that this UI element is interested in. In this case we are responding to the colour channel
        elements being changed, the OK or Cancel buttons being pressed or the user clicking the mouse inside of the
        Saturation & Value picking square.

        :param event: The pygame Event to process.
        :return: True if event is consumed by this element and should not be passed on to other elements.
        """
        consumed_event = super().process_event(event)
        if (event.type == pygame.USEREVENT and
                event.user_type == pygame_gui.UI_BUTTON_PRESSED and
                event.ui_element == self.cancel_button):
            self.kill()

        if (event.type == pygame.USEREVENT and
                event.user_type == pygame_gui.UI_BUTTON_PRESSED and
                event.ui_element == self.ok_button):
            event_data = {'user_type': pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED,
                          'colour': self.current_colour,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            new_colour_chosen_event = pygame.event.Event(pygame.USEREVENT, event_data)
            pygame.event.post(new_colour_chosen_event)
            self.kill()

        if (event.type == pygame.USEREVENT and
                event.user_type == pygame_gui.UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED):
            if event.ui_element in [self.hue_channel, self.saturation_channel, self.value_channel]:
                self.current_colour.hsva = (self.hue_channel.current_value,
                                            self.saturation_channel.current_value,
                                            self.value_channel.current_value)
                self.changed_hsv_update_rgb()
                self.update_current_colour_image()
                self.update_saturation_value_square()
            elif event.ui_element in [self.red_channel, self.green_channel, self.blue_channel]:
                self.current_colour[event.channel_index] = event.value
                self.changed_rgb_update_hsv()
                self.update_current_colour_image()
                self.update_saturation_value_square()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            scaled_mouse_pos = (int(event.pos[0] * self.ui_manager.mouse_pos_scale_factor[0]),
                                int(event.pos[1] * self.ui_manager.mouse_pos_scale_factor[1]))
            if self.saturation_value_square.rect.collidepoint(scaled_mouse_pos):
                relative_click_pos = [scaled_mouse_pos[0] - self.saturation_value_square.rect.left,
                                      scaled_mouse_pos[1] - self.saturation_value_square.rect.top]
                # put in range 0 - 100 and reverse y
                value = min(100, max(0, int((relative_click_pos[0] / self.saturation_value_square.rect.width) * 100)))
                saturation = min(100, max(0, 100 - int((relative_click_pos[1] / self.saturation_value_square.rect.height) * 100)))

                self.saturation_channel.set_value(saturation)
                self.value_channel.set_value(value)
                self.current_colour.hsva = (self.hue_channel.current_value,
                                            self.saturation_channel.current_value,
                                            self.value_channel.current_value,
                                            100)
                self.changed_hsv_update_rgb()
                self.update_current_colour_image()

        return consumed_event

    def update_current_colour_image(self):
        """
        Updates the 'current colour' image when the current colour has been changed.

        #TODO: This also needs to be made to scale with the window.
        """
        current_colour_surface = pygame.Surface((64, 64))
        current_colour_surface.fill(self.current_colour)
        self.current_colour_image.set_image(current_colour_surface)

    def update_saturation_value_square(self):
        """
        Updates the appearance of the big square that lets us visually pick the Saturation and Value of our current
        Hue. This is done by drawing a very small 4x4 pixel square with a pattern like so:

                   [black] [hue at max saturation & value)]
                   [black] [white]

        And then using the smoothscale transform to enlarge it so that the colours blend smoothly from one to the other.

        #TODO: This also needs to be made to scale with the window.
        """
        mini_colour_surf = pygame.Surface((2, 2))
        mini_colour_surf.fill(pygame.Color(0, 0, 0, 255), pygame.Rect(0, 0, 1, 2))
        mini_colour_surf.fill(pygame.Color(255, 255, 255, 255), pygame.Rect(1, 1, 1, 1))

        hue_colour = pygame.Color(255, 255, 255, 255)
        hue_colour.hsva = (int(self.hue_channel.current_value),
                           100, 100, 100)
        mini_colour_surf.fill(hue_colour, pygame.Rect(1, 0, 1, 1))
        self.saturation_value_square.set_image(pygame.transform.smoothscale(mini_colour_surf, (200, 200)))

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
        self.saturation_channel.set_value(int(self.current_colour.hsva[1]))
        self.value_channel.set_value(int(self.current_colour.hsva[2]))
