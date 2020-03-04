import pygame
import pygame_gui

from pygame_gui.elements import UIButton, UIImage, UIHorizontalSlider, UILabel, UITextEntryLine

from pygame_gui.elements import UIWindow
from pygame_gui import ui_manager

from typing import Union, Tuple, Dict
from pygame_gui.core import UIElement, IContainerInterface, UIContainer


class UIColourChannelEditor(UIElement):
    def __init__(self,
                 relative_rect: pygame.Rect,
                 manager: 'ui_manager.UIManager',
                 name: str,
                 channel_index: int,
                 value_range: Tuple[int, int],
                 initial_value: int,
                 container: Union[IContainerInterface, None] = None,
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
        if self.range[0] <= new_value <= self.range[1] and new_value != self.current_value:
            self.current_value = new_value
            self.entry.set_text(str(self.current_value))
            event_data = {'user_type': pygame_gui.UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED,
                          'value': self.current_value,
                          'channel_index': self.channel_index,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            colour_channel_changed_event = pygame.event.Event(pygame.USEREVENT, event_data)
            pygame.event.post(colour_channel_changed_event)

    def _set_value_from_entry(self, new_value: int):
        if self.range[0] <= new_value <= self.range[1] and new_value != self.current_value:
            self.current_value = new_value
            self.slider.set_current_value(self.current_value)
            event_data = {'user_type': pygame_gui.UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED,
                          'value': self.current_value,
                          'channel_index': self.channel_index,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            colour_channel_changed_event = pygame.event.Event(pygame.USEREVENT, event_data)
            pygame.event.post(colour_channel_changed_event)

    def set_value(self, new_value: int):
        if self.range[0] <= new_value <= self.range[1] and new_value != self.current_value:
            self.current_value = new_value
            self.entry.set_text(str(self.current_value))
            self.slider.set_current_value(self.current_value)


class UIColourPickerDialog(UIWindow):
    def __init__(self, rect: pygame.Rect,
                 manager: 'ui_manager.UIManager',
                 *,
                 initial_colour: pygame.Color = pygame.Color(0, 0, 0),
                 window_title: str = "Colour Picker",
                 object_id: str = '#colour_picker_dialog'):
        super().__init__(rect, manager, window_display_title=window_title, object_id=object_id)

        self.current_colour = initial_colour
        # if self.current_colour.hsva[2] == 0:
        #     self.current_colour.hsva = (int(self.current_colour.hsva[0]),
        #                                 int(self.current_colour.hsva[1]),
        #                                 1,
        #                                 int(self.current_colour.hsva[3]))
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
        mini_colour_surf.fill(pygame.Color(0, 0, 0), pygame.Rect(0, 0, 1, 2))
        mini_colour_surf.fill(pygame.Color(255, 255, 255), pygame.Rect(1, 1, 1, 1))

        hue_colour = pygame.Color(255, 255, 255)
        hue_colour.hsva = (int(self.hue_channel.current_value),
                           100, 100, 100)
        mini_colour_surf.fill(hue_colour, pygame.Rect(1, 0, 1, 1))
        colour_square_surface = pygame.transform.smoothscale(mini_colour_surf, (200, 200))
        self.colour_square = UIImage(pygame.Rect(20, 20, 200, 200),
                                     image_surface=colour_square_surface,
                                     manager=self.ui_manager,
                                     container=self)

    def update_saturation_value_square(self):
        mini_colour_surf = pygame.Surface((2, 2))
        mini_colour_surf.fill(pygame.Color(0, 0, 0), pygame.Rect(0, 0, 1, 2))
        mini_colour_surf.fill(pygame.Color(255, 255, 255), pygame.Rect(1, 1, 1, 1))

        hue_colour = pygame.Color(255, 255, 255)
        hue_colour.hsva = (int(self.hue_channel.current_value),
                           100, 100, 100)
        mini_colour_surf.fill(hue_colour, pygame.Rect(1, 0, 1, 1))
        self.colour_square.set_image(pygame.transform.smoothscale(mini_colour_surf, (200, 200)))

    def process_event(self, event: pygame.event.Event) -> bool:
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
            if self.colour_square.rect.collidepoint(scaled_mouse_pos):
                relative_click_pos = [scaled_mouse_pos[0] - self.colour_square.rect.left,
                                      scaled_mouse_pos[1] - self.colour_square.rect.top]
                # put in range 0 - 100 and reverse y
                value = min(100, max(0, int((relative_click_pos[0] / self.colour_square.rect.width) * 100)))
                saturation = min(100, max(0, 100 - int((relative_click_pos[1] / self.colour_square.rect.height) * 100)))

                self.saturation_channel.set_value(saturation)
                self.value_channel.set_value(value)
                self.current_colour.hsva = (self.hue_channel.current_value,
                                            self.saturation_channel.current_value,
                                            self.value_channel.current_value)
                self.changed_hsv_update_rgb()
                self.update_current_colour_image()

        return consumed_event

    def update_current_colour_image(self):
        current_colour_surface = pygame.Surface((64, 64))
        current_colour_surface.fill(self.current_colour)
        self.current_colour_image.set_image(current_colour_surface)

    def changed_hsv_update_rgb(self):
        self.red_channel.set_value(self.current_colour.r)
        self.green_channel.set_value(self.current_colour.g)
        self.blue_channel.set_value(self.current_colour.b)

    def changed_rgb_update_hsv(self):
        self.hue_channel.set_value(int(self.current_colour.hsva[0]))
        self.saturation_channel.set_value(int(self.current_colour.hsva[1]))
        self.value_channel.set_value(int(self.current_colour.hsva[2]))
