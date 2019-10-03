import pygame
from pygame_gui.core.ui_element import UIElement
from pygame_gui.elements.ui_button import UIButton


class UIExpandedDropDownState:
    def __init__(self, drop_down_menu_ui, options_list, selected_option, base_position_rect,
                 close_button_width, ui_manager, ui_container, element_ids, object_id):
        self.drop_down_menu_ui = drop_down_menu_ui
        self.should_transition = False
        self.options_list = options_list
        self.selected_option = selected_option
        self.base_position_rect = base_position_rect
        self.ui_manager = ui_manager
        self.ui_container = ui_container
        self.element_ids = element_ids
        self.object_id = object_id

        self.close_button_width = close_button_width

        self.selected_option_button = None
        self.close_button = None
        self.menu_buttons = []

        self.should_transition = False
        self.target_state = 'closed'

    def start(self):
        self.should_transition = False
        option_y_pos = self.base_position_rect.y
        self.selected_option_button = UIButton(pygame.Rect(self.base_position_rect.topleft,
                                                           (self.base_position_rect.width - self.close_button_width,
                                                            self.base_position_rect.height)),
                                               self.selected_option,
                                               self.ui_manager,
                                               self.ui_container,
                                               starting_height=2,
                                               object_id=self.object_id,
                                               element_ids=self.element_ids)

        close_button_x = self.base_position_rect.x + self.base_position_rect.width - self.close_button_width

        expand_direction = self.ui_manager.get_theme().get_misc_data(self.object_id,
                                                                     self.element_ids, 'expand_direction')
        expand_button_symbol = '▼'
        select_button_dist_to_move = self.selected_option_button.rect.height
        option_button_dist_to_move = self.base_position_rect.height

        if expand_direction is not None:
            if expand_direction == 'up':
                expand_button_symbol = '▲'
                select_button_dist_to_move = -self.selected_option_button.rect.height
                option_button_dist_to_move = -self.base_position_rect.height
            elif expand_direction == 'down':
                expand_button_symbol = '▼'
                select_button_dist_to_move = self.selected_option_button.rect.height
                option_button_dist_to_move = self.base_position_rect.height

        self.close_button = UIButton(pygame.Rect((close_button_x, self.base_position_rect.y),
                                                 (self.close_button_width, self.base_position_rect.height)),
                                     expand_button_symbol,
                                     self.ui_manager,
                                     self.ui_container,
                                     starting_height=2,
                                     object_id=self.object_id,
                                     element_ids=self.element_ids)

        option_y_pos += select_button_dist_to_move
        for option in self.options_list:
            new_button = UIButton(pygame.Rect((self.base_position_rect.x, option_y_pos),
                                              (self.base_position_rect.width - self.close_button_width,
                                  self.base_position_rect.height)),
                                  option,
                                  self.ui_manager,
                                  self.ui_container,
                                  starting_height=3,  # height allows options to overlap other UI elements
                                  object_id=self.object_id,
                                  element_ids=self.element_ids)
            option_y_pos += option_button_dist_to_move
            self.menu_buttons.append(new_button)

    def finish(self):
        for button in self.menu_buttons:
            button.kill()

        self.menu_buttons.clear()

        self.selected_option_button.kill()
        self.close_button.kill()

    def update(self):
        if self.close_button.check_pressed_and_reset():
            self.should_transition = True

        for button in self.menu_buttons:
            if button.check_pressed_and_reset():
                self.drop_down_menu_ui.selected_option = button.text
                self.should_transition = True


class UIClosedDropDownState:
    def __init__(self, drop_down_menu_ui, selected_option, base_position_rect,
                 open_button_width, ui_manager, ui_container, element_ids, object_id):
        self.drop_down_menu_ui = drop_down_menu_ui
        self.selected_option_button = None
        self.open_button = None
        self.selected_option = selected_option
        self.base_position_rect = base_position_rect
        self.ui_manager = ui_manager
        self.ui_container = ui_container
        self.element_ids = element_ids
        self.object_id = object_id

        self.open_button_width = open_button_width

        self.should_transition = False
        self.target_state = 'expanded'

    def start(self):
        self.should_transition = False
        self.selected_option_button = UIButton(pygame.Rect((self.base_position_rect.x,
                                                            self.base_position_rect.y),
                                                           (self.base_position_rect.width - self.open_button_width,
                                               self.base_position_rect.height)),
                                               self.selected_option,
                                               self.ui_manager,
                                               self.ui_container,
                                               starting_height=2,
                                               object_id=self.object_id,
                                               element_ids=self.element_ids)
        open_button_x = self.base_position_rect.x + self.base_position_rect.width - self.open_button_width

        expand_direction = self.ui_manager.get_theme().get_misc_data(self.object_id,
                                                                     self.element_ids, 'expand_direction')
        expand_button_symbol = '▼'
        if expand_direction is not None:
            if expand_direction == 'up':
                expand_button_symbol = '▲'
            elif expand_direction == 'down':
                expand_button_symbol = '▼'

        self.open_button = UIButton(pygame.Rect((open_button_x,
                                                 self.base_position_rect.y),
                                                (self.open_button_width, self.base_position_rect.height)),
                                    expand_button_symbol,
                                    self.ui_manager,
                                    self.ui_container,
                                    starting_height=2,
                                    object_id=self.object_id,
                                    element_ids=self.element_ids)

    def finish(self):
        self.selected_option_button.kill()
        self.open_button.kill()

    def update(self):
        if self.open_button.check_pressed_and_reset():
            self.should_transition = True


class UIDropDownMenu(UIElement):
    def __init__(self, options_list, starting_option, relative_rect, ui_manager,
                 ui_container=None, element_ids=None, object_id=None):

        if element_ids is None:
            new_element_ids = ['drop_down_menu']
        else:
            new_element_ids = element_ids.copy()
            new_element_ids.append('drop_down_menu')
        super().__init__(relative_rect, ui_manager, ui_container,
                         element_ids=new_element_ids,
                         object_id=object_id,
                         layer_thickness=1, starting_height=1)
        self.options_list = options_list
        self.selected_option = starting_option
        self.open_button_width = 20

        self.menu_states = {'closed': UIClosedDropDownState(self,
                                                            self.selected_option,
                                                            self.relative_rect,
                                                            self.open_button_width,
                                                            self.ui_manager,
                                                            self.ui_container,
                                                            self.element_ids,
                                                            self.object_id),
                            'expanded': UIExpandedDropDownState(self,
                                                                self.options_list,
                                                                self.selected_option,
                                                                self.relative_rect,
                                                                self.open_button_width,
                                                                self.ui_manager,
                                                                self.ui_container,
                                                                self.element_ids,
                                                                self.object_id
                                                                )}
        self.current_state = self.menu_states['closed']
        self.current_state.start()

        self.image = pygame.Surface((0, 0))

    def kill(self):
        self.current_state.finish()
        super().kill()

    def update(self, time_delta):
        if self.alive():
            if self.current_state.should_transition:
                self.current_state.finish()
                self.current_state = self.menu_states[self.current_state.target_state]
                self.current_state.selected_option = self.selected_option
                self.current_state.start()

            self.current_state.update()
