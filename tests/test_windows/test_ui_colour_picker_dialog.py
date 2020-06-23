import os
import pygame
import pytest
import pygame_gui

from tests.shared_fixtures import _init_pygame, default_ui_manager
from tests.shared_fixtures import default_display_surface, _display_surface_return_none
from tests.shared_comparators import compare_surfaces

from pygame_gui.ui_manager import UIManager
from pygame_gui.core.ui_container import UIContainer
from pygame_gui.windows import UIColourPickerDialog
from pygame_gui.windows.ui_colour_picker_dialog import UIColourChannelEditor
from pygame_gui.core.utility import restore_premul_col

try:
    # mouse button constants not defined in pygame 1.9.3
    pygame.BUTTON_LEFT
    pygame.BUTTON_MIDDLE
    pygame.BUTTON_RIGHT
except AttributeError:
    pygame.BUTTON_LEFT = 1
    pygame.BUTTON_MIDDLE = 2
    pygame.BUTTON_RIGHT = 3


class TestUIColourChannelEditor:
    def test_creation(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        UIColourChannelEditor(relative_rect=pygame.Rect(0, 0, 150, 29),
                              manager=default_ui_manager,
                              name='H:',
                              channel_index=0,
                              initial_value=0,
                              value_range=(0, 360))

    def test_text_entry_finished(self, _init_pygame, default_ui_manager,
                                 _display_surface_return_none):
        channel_editor = UIColourChannelEditor(relative_rect=pygame.Rect(0, 0, 150, 29),
                                               manager=default_ui_manager,
                                               name='H:',
                                               channel_index=0,
                                               initial_value=0,
                                               value_range=(0, 360))

        channel_editor.entry.set_text('50')

        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': channel_editor.entry.rect.center}
                                                             ))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': channel_editor.entry.rect.center}
                                                             ))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYDOWN,
                                                             {'key': pygame.K_RETURN}
                                                             ))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert channel_editor.slider.current_value == 50

    def test_slider_moved_finished(self, _init_pygame, default_ui_manager,
                                   _display_surface_return_none):
        channel_editor = UIColourChannelEditor(relative_rect=pygame.Rect(0, 0, 150, 29),
                                               manager=default_ui_manager,
                                               name='H:',
                                               channel_index=0,
                                               initial_value=0,
                                               value_range=(0, 360))

        channel_editor.slider.current_value = 100

        default_ui_manager.process_events(pygame.event.Event(pygame.USEREVENT,
                                                             {'user_type': pygame_gui.UI_HORIZONTAL_SLIDER_MOVED,
                                                              'ui_element': channel_editor.slider}
                                                             ))
        assert channel_editor.entry.get_text() == '100'

    def test_set_value(self, _init_pygame, default_ui_manager,
                       _display_surface_return_none):
        channel_editor = UIColourChannelEditor(relative_rect=pygame.Rect(0, 0, 150, 29),
                                               manager=default_ui_manager,
                                               name='H:',
                                               channel_index=0,
                                               initial_value=0,
                                               value_range=(0, 360))

        assert channel_editor.entry.get_text() == '0'
        assert channel_editor.slider.get_current_value() == 0

        channel_editor.set_value(200)

        assert channel_editor.entry.get_text() == '200'
        assert channel_editor.slider.get_current_value() == 200
        assert channel_editor.current_value == 200

    def test_set_position(self, _init_pygame, default_ui_manager,
                          _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60),
                                     manager=default_ui_manager)
        channel_editor = UIColourChannelEditor(relative_rect=pygame.Rect(0, 0, 150, 29),
                                               manager=default_ui_manager,
                                               name='H:',
                                               channel_index=0,
                                               initial_value=0,
                                               value_range=(0, 360),
                                               container=test_container)

        channel_editor.set_position((150, 30))

        assert channel_editor.relative_rect.topleft == (50, -70)

    def test_set_relative_position(self, _init_pygame, default_ui_manager,
                                   _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60),
                                     manager=default_ui_manager)
        channel_editor = UIColourChannelEditor(relative_rect=pygame.Rect(0, 0, 150, 29),
                                               manager=default_ui_manager,
                                               name='H:',
                                               channel_index=0,
                                               initial_value=0,
                                               value_range=(0, 360),
                                               container=test_container)

        channel_editor.set_relative_position((50, 50))

        assert channel_editor.rect.topleft == (150, 150)

    def test_set_dimensions(self, _init_pygame, default_ui_manager,
                            _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60),
                                     manager=default_ui_manager)
        channel_editor = UIColourChannelEditor(relative_rect=pygame.Rect(0, 0, 150, 29),
                                               manager=default_ui_manager,
                                               name='H:',
                                               channel_index=0,
                                               initial_value=0,
                                               value_range=(0, 360),
                                               container=test_container)

        channel_editor.set_dimensions((200, 29))

        assert channel_editor.rect.size == (200, 29)

    def test_show(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60),
                                     manager=default_ui_manager)
        channel_editor = UIColourChannelEditor(relative_rect=pygame.Rect(0, 0, 150, 29),
                                               manager=default_ui_manager,
                                               name='H:',
                                               channel_index=0,
                                               initial_value=0,
                                               value_range=(0, 360),
                                               container=test_container,
                                               visible=0)

        channel_editor.set_dimensions((200, 29))

        assert channel_editor.visible == 0
        assert channel_editor.dirty == 1

        assert channel_editor.element_container.visible == 0
        assert channel_editor.label.visible == 0
        assert channel_editor.entry.visible == 0
        assert channel_editor.slider.visible == 0

        channel_editor.show()

        assert channel_editor.visible == 1
        assert channel_editor.dirty == 2

        assert channel_editor.element_container.visible == 1
        assert channel_editor.label.visible == 1
        assert channel_editor.entry.visible == 1
        assert channel_editor.slider.visible == 1

    def test_hide(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60),
                                     manager=default_ui_manager)
        channel_editor = UIColourChannelEditor(relative_rect=pygame.Rect(0, 0, 150, 29),
                                               manager=default_ui_manager,
                                               name='H:',
                                               channel_index=0,
                                               initial_value=0,
                                               value_range=(0, 360),
                                               container=test_container,
                                               visible=1)

        channel_editor.set_dimensions((200, 29))

        assert channel_editor.visible == 1
        assert channel_editor.dirty == 2

        assert channel_editor.element_container.visible == 1
        assert channel_editor.label.visible == 1
        assert channel_editor.entry.visible == 1
        assert channel_editor.slider.visible == 1

        channel_editor.hide()

        assert channel_editor.visible == 0
        assert channel_editor.dirty == 1

        assert channel_editor.element_container.visible == 0
        assert channel_editor.label.visible == 0
        assert channel_editor.entry.visible == 0
        assert channel_editor.slider.visible == 0

    def test_show_hide_rendering(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        resolution = (400, 400)
        empty_surface = pygame.Surface(resolution)
        empty_surface.fill(pygame.Color(0, 0, 0))

        surface = empty_surface.copy()
        manager = pygame_gui.UIManager(resolution)
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 60),
                                     manager=manager)
        manager.draw_ui(empty_surface)
        channel_editor = UIColourChannelEditor(relative_rect=pygame.Rect(0, 0, 150, 29),
                                               manager=manager,
                                               name='H:',
                                               channel_index=0,
                                               initial_value=0,
                                               value_range=(0, 360),
                                               container=test_container,
                                               visible=0)

        channel_editor.set_dimensions((200, 29))

        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        channel_editor.show()
        manager.draw_ui(surface)
        assert not compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        channel_editor.hide()
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)


class TestUIColourPickerDialog:

    def test_creation(self, _init_pygame, default_ui_manager,
                      _display_surface_return_none):
        UIColourPickerDialog(rect=pygame.Rect(100, 100, 400, 400),
                             manager=default_ui_manager)

    def test_create_too_small(self, _init_pygame, default_ui_manager,
                              _display_surface_return_none):
        with pytest.warns(UserWarning, match="Initial size"):
            UIColourPickerDialog(rect=pygame.Rect(100, 100, 50, 50),
                                 manager=default_ui_manager)

    def test_press_cancel_button(self, _init_pygame, default_ui_manager,
                                 _display_surface_return_none):
        colour_picker = UIColourPickerDialog(rect=pygame.Rect(100, 100, 400, 400),
                                             manager=default_ui_manager)

        is_alive_pre_events = colour_picker.alive()
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': colour_picker.cancel_button.rect.center}))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': colour_picker.cancel_button.rect.center}))
        for event in pygame.event.get():
            default_ui_manager.process_events(event)
        is_dead_post_events = not colour_picker.alive()

        assert is_alive_pre_events is True and is_dead_post_events is True

    def test_press_ok_button(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        colour_picker = UIColourPickerDialog(rect=pygame.Rect(100, 100, 400, 400),
                                             manager=default_ui_manager,
                                             initial_colour=pygame.Color(200, 220, 50, 255))

        is_alive_pre_events = colour_picker.alive()
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': colour_picker.ok_button.rect.center}))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': colour_picker.ok_button.rect.center}))
        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        confirm_event_fired = False
        event_colour = None
        for event in pygame.event.get():
            default_ui_manager.process_events(event)

            if (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED and
                    event.ui_element == colour_picker):
                confirm_event_fired = True
                event_colour = event.colour
        is_dead_post_events = not colour_picker.alive()

        assert is_alive_pre_events
        assert is_dead_post_events
        assert confirm_event_fired
        assert event_colour == pygame.Color(200, 220, 50, 255)

    def test_click_in_saturation_value_square_button(self, _init_pygame,
                                                     default_ui_manager, _display_surface_return_none):
        colour_picker = UIColourPickerDialog(rect=pygame.Rect(100, 100, 400, 400),
                                             manager=default_ui_manager,
                                             initial_colour=pygame.Color(200, 220, 50, 255))

        assert colour_picker.current_colour == pygame.Color(200, 220, 50, 255)

        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': colour_picker.sat_value_square.rect.center}
                                                             ))

        assert colour_picker.current_colour == pygame.Color(120, 127, 63, 255)

    def test_mess_with_colour_channel_event(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        colour_picker = UIColourPickerDialog(rect=pygame.Rect(100, 100, 400, 400),
                                             manager=default_ui_manager,
                                             initial_colour=pygame.Color(200, 220, 50, 255))

        colour_picker.red_channel.entry.set_text('50')
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': colour_picker.red_channel.entry.rect.center}
                                                             ))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': colour_picker.red_channel.entry.rect.center}
                                                             ))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYDOWN,
                                                             {'key': pygame.K_RETURN}
                                                             ))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        confirm_event_fired = False
        for event in pygame.event.get():

            if (event.type == pygame.USEREVENT and
                    event.user_type == pygame_gui.UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED and
                    event.ui_element == colour_picker.red_channel):
                confirm_event_fired = True

        assert confirm_event_fired

    def test_update_saturation_value_square(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        colour_picker = UIColourPickerDialog(rect=pygame.Rect(100, 100, 400, 400),
                                             manager=default_ui_manager)

        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': colour_picker.sat_value_square.rect.center}
                                                             ))
        assert colour_picker.current_colour == pygame.Color(127, 63, 63, 255)

        colour_picker.hue_channel.current_value = 150
        colour_picker.update_saturation_value_square()

        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                             {'button': pygame.BUTTON_LEFT,
                                                              'pos': colour_picker.sat_value_square.rect.center}
                                                             ))
        assert colour_picker.current_colour == pygame.Color(63, 127, 95, 255)

    def test_update_current_colour_image(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        colour_picker = UIColourPickerDialog(rect=pygame.Rect(100, 100, 400, 400),
                                             manager=default_ui_manager,
                                             initial_colour=pygame.Color(200, 220, 50, 255))

        pixel_colour = colour_picker.current_colour_image.image.get_at((int(colour_picker.current_colour_image.rect.width/2),
                                                                        int(colour_picker.current_colour_image.rect.height/2)))

        pixel_colour = restore_premul_col(pixel_colour)  # this is going to be slightly inaccurate

        assert 201 >= pixel_colour.r >= 199
        assert 221 >= pixel_colour.g >= 219
        assert 51 >= pixel_colour.b >= 49
        assert pixel_colour.a == 255

        colour_picker.current_colour = pygame.Color(50, 180, 150, 255)
        colour_picker.update_current_colour_image()

        pixel_colour = colour_picker.current_colour_image.image.get_at(
            (int(colour_picker.current_colour_image.rect.width / 2),
             int(colour_picker.current_colour_image.rect.height / 2)))

        pixel_colour = restore_premul_col(pixel_colour)

        assert 51 >= pixel_colour.r >= 49
        assert 181 >= pixel_colour.g >= 179
        assert 151 >= pixel_colour.b >= 149
        assert pixel_colour.a == 255

    def test_changed_rgb_update_hsv(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        colour_picker = UIColourPickerDialog(rect=pygame.Rect(100, 100, 400, 400),
                                             manager=default_ui_manager,
                                             initial_colour=pygame.Color(200, 220, 50, 255))

        assert colour_picker.red_channel.current_value == 200
        assert colour_picker.green_channel.current_value == 220
        assert colour_picker.blue_channel.current_value == 50

        colour_picker.red_channel.set_value(100)
        colour_picker.green_channel.set_value(80)
        colour_picker.blue_channel.set_value(190)

        colour_picker.current_colour = pygame.Color(colour_picker.red_channel.current_value,
                                                    colour_picker.green_channel.current_value,
                                                    colour_picker.blue_channel.current_value)

        assert colour_picker.hue_channel.current_value == 67
        assert colour_picker.sat_channel.current_value == 77
        assert colour_picker.value_channel.current_value == 86

        colour_picker.changed_rgb_update_hsv()

        assert colour_picker.hue_channel.current_value == 250
        assert colour_picker.sat_channel.current_value == 57
        assert colour_picker.value_channel.current_value == 74

    def test_changed_hsv_update_rgb(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        colour_picker = UIColourPickerDialog(rect=pygame.Rect(100, 100, 400, 400),
                                             manager=default_ui_manager,
                                             initial_colour=pygame.Color(200, 220, 50, 255))

        assert colour_picker.hue_channel.current_value == 67
        assert colour_picker.sat_channel.current_value == 77
        assert colour_picker.value_channel.current_value == 86

        colour_picker.hue_channel.set_value(250)
        colour_picker.sat_channel.set_value(57)
        colour_picker.value_channel.set_value(74)

        colour_picker.current_colour.hsva = (colour_picker.hue_channel.current_value,
                                             colour_picker.sat_channel.current_value,
                                             colour_picker.value_channel.current_value,
                                             100)

        assert colour_picker.red_channel.current_value == 200
        assert colour_picker.green_channel.current_value == 220
        assert colour_picker.blue_channel.current_value == 50

        colour_picker.changed_hsv_update_rgb()

        assert colour_picker.red_channel.current_value == 99
        assert colour_picker.green_channel.current_value == 81
        assert colour_picker.blue_channel.current_value == 188

    def test_show(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        colour_picker = UIColourPickerDialog(rect=pygame.Rect(100, 100, 400, 400),
                                             manager=default_ui_manager,
                                             initial_colour=pygame.Color(200, 220, 50, 255),
                                             visible=0)

        assert colour_picker.visible == 0
        assert colour_picker.dirty == 1

        assert colour_picker.ok_button.visible == 0
        assert colour_picker.cancel_button.visible == 0
        assert colour_picker.current_colour_image.visible == 0
        assert colour_picker.sat_value_square.visible == 0

        assert colour_picker.hue_channel.visible == 0
        assert colour_picker.sat_channel.visible == 0
        assert colour_picker.value_channel.visible == 0

        assert colour_picker.red_channel.visible == 0
        assert colour_picker.green_channel.visible == 0
        assert colour_picker.blue_channel.visible == 0

        colour_picker.show()

        assert colour_picker.visible == 1
        assert colour_picker.dirty == 2

        assert colour_picker.ok_button.visible == 1
        assert colour_picker.cancel_button.visible == 1
        assert colour_picker.current_colour_image.visible == 1
        assert colour_picker.sat_value_square.visible == 1

        assert colour_picker.hue_channel.visible == 1
        assert colour_picker.sat_channel.visible == 1
        assert colour_picker.value_channel.visible == 1

        assert colour_picker.red_channel.visible == 1
        assert colour_picker.green_channel.visible == 1
        assert colour_picker.blue_channel.visible == 1

    def test_hide(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        colour_picker = UIColourPickerDialog(rect=pygame.Rect(100, 100, 400, 400),
                                             manager=default_ui_manager,
                                             initial_colour=pygame.Color(200, 220, 50, 255),
                                             visible=1)

        assert colour_picker.visible == 1
        assert colour_picker.dirty == 2

        assert colour_picker.ok_button.visible == 1
        assert colour_picker.cancel_button.visible == 1
        assert colour_picker.current_colour_image.visible == 1
        assert colour_picker.sat_value_square.visible == 1

        assert colour_picker.hue_channel.visible == 1
        assert colour_picker.sat_channel.visible == 1
        assert colour_picker.value_channel.visible == 1

        assert colour_picker.red_channel.visible == 1
        assert colour_picker.green_channel.visible == 1
        assert colour_picker.blue_channel.visible == 1

        colour_picker.hide()

        assert colour_picker.visible == 0
        assert colour_picker.dirty == 1

        assert colour_picker.ok_button.visible == 0
        assert colour_picker.cancel_button.visible == 0
        assert colour_picker.current_colour_image.visible == 0
        assert colour_picker.sat_value_square.visible == 0

        assert colour_picker.hue_channel.visible == 0
        assert colour_picker.sat_channel.visible == 0
        assert colour_picker.value_channel.visible == 0

        assert colour_picker.red_channel.visible == 0
        assert colour_picker.green_channel.visible == 0
        assert colour_picker.blue_channel.visible == 0

    def test_show_hide_rendering(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        resolution = (600, 600)
        empty_surface = pygame.Surface(resolution)
        empty_surface.fill(pygame.Color(0, 0, 0))

        surface = empty_surface.copy()
        manager = pygame_gui.UIManager(resolution)
        colour_picker = UIColourPickerDialog(rect=pygame.Rect(100, 100, 400, 400),
                                             manager=manager,
                                             initial_colour=pygame.Color(200, 220, 50, 255),
                                             visible=0)

        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        colour_picker.show()
        manager.draw_ui(surface)
        assert not compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        colour_picker.hide()
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)
