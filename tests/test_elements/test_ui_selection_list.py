import os
import pytest
import pygame
import pygame_gui

from tests.shared_fixtures import _init_pygame, default_ui_manager
from tests.shared_fixtures import default_display_surface, _display_surface_return_none

from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.core.ui_container import UIContainer
from pygame_gui.elements.ui_selection_list import UISelectionList
from pygame_gui.ui_manager import UIManager


class TestUISelectionList:

    def test_creation(self, _init_pygame, default_ui_manager,
                      _display_surface_return_none):
        UISelectionList(relative_rect=pygame.Rect(50, 50, 150, 400),
                        item_list=['green', 'eggs', 'and', 'ham'],
                        manager=default_ui_manager)

    def test_get_single_selection(self, _init_pygame, default_ui_manager,
                                  _display_surface_return_none):
        selection_list = UISelectionList(relative_rect=pygame.Rect(50, 50, 150, 400),
                                         item_list=['green', 'eggs', 'and', 'ham'],
                                         manager=default_ui_manager)

        assert selection_list.get_single_selection() is None

        event_data = {'user_type': pygame_gui.UI_BUTTON_PRESSED,
                      'ui_element': selection_list.item_list_container.elements[0]}
        press_list_item_event = pygame.event.Event(pygame.USEREVENT, event_data)
        default_ui_manager.process_events(press_list_item_event)

        assert selection_list.get_single_selection() == 'green'

        selection_list.item_list[1]['selected'] = True
        with pytest.raises(RuntimeError,
                           match='More than one item selected in single-selection, selection list'):
            selection_list.get_single_selection()

        multi_selection_list = UISelectionList(relative_rect=pygame.Rect(50, 50, 150, 400),
                                               item_list=['green', 'eggs', 'and', 'ham'],
                                               manager=default_ui_manager,
                                               allow_multi_select=True)
        with pytest.raises(RuntimeError,
                           match='Requesting single selection, from multi-selection list'):
            multi_selection_list.get_single_selection()

    def test_get_multi_selection(self, _init_pygame, default_ui_manager,
                                 _display_surface_return_none):
        selection_list = UISelectionList(relative_rect=pygame.Rect(50, 50, 150, 400),
                                         item_list=['green', 'eggs', 'and', 'ham'],
                                         manager=default_ui_manager,
                                         allow_multi_select=True)

        assert selection_list.get_multi_selection() == []

        event_data = {'user_type': pygame_gui.UI_BUTTON_PRESSED,
                      'ui_element': selection_list.item_list_container.elements[0]}
        press_list_item_event = pygame.event.Event(pygame.USEREVENT, event_data)
        default_ui_manager.process_events(press_list_item_event)

        assert selection_list.get_multi_selection() == ['green']

        event_data = {'user_type': pygame_gui.UI_BUTTON_PRESSED,
                      'ui_element': selection_list.item_list_container.elements[1]}
        press_list_item_event = pygame.event.Event(pygame.USEREVENT, event_data)
        default_ui_manager.process_events(press_list_item_event)
        assert selection_list.get_multi_selection() == ['green', 'eggs']

        single_selection_list = UISelectionList(relative_rect=pygame.Rect(50, 50, 150, 400),
                                                item_list=['green', 'eggs', 'and', 'ham'],
                                                manager=default_ui_manager)
        with pytest.raises(RuntimeError,
                           match='Requesting multi selection, from single-selection list'):
            single_selection_list.get_multi_selection()

    def test_update(self, _init_pygame, default_ui_manager, _display_surface_return_none: None):
        selection_list = UISelectionList(relative_rect=pygame.Rect(50, 50, 150, 80),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=default_ui_manager,
                                         allow_multi_select=True)

        assert selection_list.scroll_bar is not None

        visible_items = [item['text'] for item in selection_list.item_list
                         if item['button_element'] is not None]
        assert visible_items == ['item 1', 'item 2', 'item 3', 'item 4']
        # scroll the list a bit
        selection_list.scroll_bar.has_moved_recently = True
        selection_list.scroll_bar.start_percentage = 0.3
        selection_list.update(time_delta=0.05)

        visible_items = [item['text'] for item in selection_list.item_list
                         if item['button_element'] is not None]
        assert visible_items == ['item 5', 'item 6', 'item 7', 'item 8', 'item 9']

    def test_set_item_list(self, _init_pygame, default_ui_manager,
                           _display_surface_return_none: None):
        selection_list = UISelectionList(relative_rect=pygame.Rect(50, 50, 150, 80),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=default_ui_manager,
                                         allow_multi_select=True)

        assert selection_list.scroll_bar is not None
        visible_items = [item['text'] for item in selection_list.item_list
                         if item['button_element'] is not None]
        assert visible_items == ['item 1', 'item 2', 'item 3', 'item 4']

        selection_list.set_item_list(['new item 1', 'new item 2',
                                      'new item 3', 'new item 4', 'new item 5',
                                      'new item 6', 'new item 7', 'new item 8',
                                      'new item 9', 'new item 10',
                                      'new item 11', 'new item 12', 'new item 13',
                                      'new item 14', 'new item 15'])

        assert selection_list.scroll_bar is not None
        visible_items = [item['text'] for item in selection_list.item_list
                         if item['button_element'] is not None]
        assert visible_items == ['new item 1', 'new item 2', 'new item 3', 'new item 4']

        selection_list.set_item_list(['another item 1', 'another item 2'])

        assert selection_list.scroll_bar is None
        visible_items = [item['text'] for item in selection_list.item_list
                         if item['button_element'] is not None]
        assert visible_items == ['another item 1', 'another item 2']

    def test_process_event(self, _init_pygame, default_ui_manager,
                           _display_surface_return_none: None):
        selection_list = UISelectionList(relative_rect=pygame.Rect(50, 50, 150, 80),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=default_ui_manager,
                                         allow_multi_select=True,
                                         allow_double_clicks=True)

        event_data = {'user_type': pygame_gui.UI_BUTTON_PRESSED,
                      'ui_element': selection_list.item_list_container.elements[0]}
        select_event = pygame.event.Event(pygame.USEREVENT, event_data)

        selection_list.process_event(select_event)

        confirm_event_fired = False
        event_text = None
        for event in pygame.event.get():
            if (event.type == pygame.USEREVENT and
                    event.user_type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION and
                    event.ui_element == selection_list):
                confirm_event_fired = True
                event_text = event.text

        assert confirm_event_fired
        assert event_text == 'item 1'

        event_data = {'user_type': pygame_gui.UI_BUTTON_PRESSED,
                      'ui_element': selection_list.item_list_container.elements[0]}
        unselect_event = pygame.event.Event(pygame.USEREVENT, event_data)

        selection_list.process_event(unselect_event)

        confirm_event_fired = False
        event_text = None
        for event in pygame.event.get():
            if (event.type == pygame.USEREVENT and
                    event.user_type == pygame_gui.UI_SELECTION_LIST_DROPPED_SELECTION and
                    event.ui_element == selection_list):
                confirm_event_fired = True
                event_text = event.text

        assert confirm_event_fired
        assert event_text == 'item 1'

        event_data = {'user_type': pygame_gui.UI_BUTTON_DOUBLE_CLICKED,
                      'ui_element': selection_list.item_list_container.elements[0]}
        double_clicked_event = pygame.event.Event(pygame.USEREVENT, event_data)

        selection_list.process_event(double_clicked_event)

        confirm_event_fired = False
        event_text = None
        for event in pygame.event.get():
            if (event.type == pygame.USEREVENT and
                    event.user_type == pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION and
                    event.ui_element == selection_list):
                confirm_event_fired = True
                event_text = event.text

        assert confirm_event_fired
        assert event_text == 'item 1'

        single_selection_list = UISelectionList(relative_rect=pygame.Rect(50, 50, 150, 80),
                                                item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                           'item 5', 'item 6', 'item 7', 'item 8',
                                                           'item 9', 'item 10',
                                                           'item 11', 'item 12',
                                                           'item 13', 'item 14',
                                                           'item 15', 'item 16'],
                                                manager=default_ui_manager,
                                                allow_multi_select=False,
                                                allow_double_clicks=True)

        event_data = {'user_type': pygame_gui.UI_BUTTON_PRESSED,
                      'ui_element': single_selection_list.item_list_container.elements[0]}
        select_event = pygame.event.Event(pygame.USEREVENT, event_data)

        single_selection_list.process_event(select_event)

        event_data = {'user_type': pygame_gui.UI_BUTTON_PRESSED,
                      'ui_element': single_selection_list.item_list_container.elements[1]}
        select_another_event = pygame.event.Event(pygame.USEREVENT, event_data)

        single_selection_list.process_event(select_another_event)

        dropped_event_text = None
        select_event_text = None
        for event in pygame.event.get():
            if (event.type == pygame.USEREVENT and
                    event.user_type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION and
                    event.ui_element == single_selection_list):
                select_event_text = event.text

            if (event.type == pygame.USEREVENT and
                    event.user_type == pygame_gui.UI_SELECTION_LIST_DROPPED_SELECTION and
                    event.ui_element == single_selection_list):
                dropped_event_text = event.text

        assert select_event_text == 'item 2' and dropped_event_text == 'item 1'

    def test_set_relative_position(self, _init_pygame, default_ui_manager,
                                   _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(100, 100, 300, 300),
                                     manager=default_ui_manager)
        selection_list = UISelectionList(relative_rect=pygame.Rect(0, 0, 50, 50),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=default_ui_manager,
                                         container=test_container,
                                         allow_multi_select=True,
                                         anchors={'left': 'left',
                                                  'right': 'left',
                                                  'top': 'top',
                                                  'bottom': 'top'})

        selection_list.set_relative_position((20, 20))
        assert selection_list.rect.topleft == (120, 120)
        assert selection_list.rect.size == (50, 50)
        assert selection_list.rect.bottomright == (170, 170)

        selection_list = UISelectionList(relative_rect=pygame.Rect(0, 0, 50, 50),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=default_ui_manager,
                                         container=test_container,
                                         allow_multi_select=True,
                                         anchors={'left': 'right',
                                                  'right': 'right',
                                                  'top': 'top',
                                                  'bottom': 'top'})

        selection_list.set_relative_position((-20, 20))
        assert selection_list.rect.topleft == (380, 120)
        assert selection_list.rect.size == (50, 50)
        assert selection_list.rect.bottomright == (430, 170)

        selection_list = UISelectionList(relative_rect=pygame.Rect(0, 0, 50, 50),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=default_ui_manager,
                                         container=test_container,
                                         allow_multi_select=True,
                                         anchors={'left': 'right',
                                                  'right': 'right',
                                                  'top': 'bottom',
                                                  'bottom': 'bottom'})

        selection_list.set_relative_position((-70, -70))
        assert selection_list.rect.topleft == (330, 330)
        assert selection_list.rect.size == (50, 50)
        assert selection_list.rect.bottomright == (380, 380)

        selection_list = UISelectionList(relative_rect=pygame.Rect(0, 0, 50, 50),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=default_ui_manager,
                                         container=test_container,
                                         allow_multi_select=True,
                                         anchors={'left': 'left',
                                                  'right': 'left',
                                                  'top': 'bottom',
                                                  'bottom': 'bottom'})

        selection_list.set_relative_position((30, -70))
        assert selection_list.rect.topleft == (130, 330)
        assert selection_list.rect.size == (50, 50)
        assert selection_list.rect.bottomright == (180, 380)

        selection_list = UISelectionList(relative_rect=pygame.Rect(0, 0, 50, 50),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=default_ui_manager,
                                         container=test_container,
                                         allow_multi_select=True,
                                         anchors={'left': 'left',
                                                  'right': 'right',
                                                  'top': 'top',
                                                  'bottom': 'bottom'})

        assert selection_list.relative_right_margin == 250
        assert selection_list.relative_bottom_margin == 250

        selection_list.set_relative_position((20, 20))
        assert selection_list.rect.topleft == (120, 120)
        assert selection_list.rect.size == (50, 50)
        assert selection_list.rect.bottomright == (170, 170)
        assert selection_list.relative_right_margin == 230
        assert selection_list.relative_bottom_margin == 230

    def test_set_position(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(10, 10, 300, 300),
                                     manager=default_ui_manager)

        selection_list = UISelectionList(relative_rect=pygame.Rect(0, 0, 50, 50),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=default_ui_manager,
                                         container=test_container,
                                         allow_multi_select=True,
                                         anchors={'left': 'left',
                                                  'right': 'left',
                                                  'top': 'top',
                                                  'bottom': 'top'})

        selection_list.set_position((20, 20))
        assert selection_list.relative_rect.topleft == (10, 10)
        assert selection_list.relative_rect.size == (50, 50)
        assert selection_list.relative_rect.bottomright == (60, 60)

        selection_list = UISelectionList(relative_rect=pygame.Rect(0, 0, 50, 50),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=default_ui_manager,
                                         container=test_container,
                                         allow_multi_select=True,
                                         anchors={'left': 'right',
                                                  'right': 'right',
                                                  'top': 'top',
                                                  'bottom': 'top'})

        selection_list.set_position((280, 120))
        assert selection_list.relative_rect.topleft == (-30, 110)
        assert selection_list.relative_rect.size == (50, 50)
        assert selection_list.relative_rect.bottomright == (20, 160)

        selection_list = UISelectionList(relative_rect=pygame.Rect(0, 0, 50, 50),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=default_ui_manager,
                                         container=test_container,
                                         allow_multi_select=True,
                                         anchors={'left': 'right',
                                                  'right': 'right',
                                                  'top': 'bottom',
                                                  'bottom': 'bottom'})

        selection_list.set_position((230, 230))
        assert selection_list.relative_rect.topleft == (-80, -80)
        assert selection_list.relative_rect.size == (50, 50)
        assert selection_list.relative_rect.bottomright == (-30, -30)

        selection_list = UISelectionList(relative_rect=pygame.Rect(0, 0, 50, 50),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=default_ui_manager,
                                         container=test_container,
                                         allow_multi_select=True,
                                         anchors={'left': 'left',
                                                  'right': 'left',
                                                  'top': 'bottom',
                                                  'bottom': 'bottom'})

        selection_list.set_position((130, 230))
        assert selection_list.relative_rect.topleft == (120, -80)
        assert selection_list.relative_rect.size == (50, 50)
        assert selection_list.relative_rect.bottomright == (170, -30)

        selection_list = UISelectionList(relative_rect=pygame.Rect(0, 0, 50, 50),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=default_ui_manager,
                                         container=test_container,
                                         allow_multi_select=True,
                                         anchors={'left': 'left',
                                                  'right': 'right',
                                                  'top': 'top',
                                                  'bottom': 'bottom'})

        assert selection_list.relative_right_margin == 250
        assert selection_list.relative_bottom_margin == 250

        selection_list.set_position((20, 20))
        assert selection_list.relative_rect.topleft == (10, 10)
        assert selection_list.relative_rect.size == (50, 50)
        assert selection_list.relative_rect.bottomright == (60, 60)
        assert selection_list.relative_right_margin == 240
        assert selection_list.relative_bottom_margin == 240

    def test_set_dimensions(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        test_container = UIContainer(relative_rect=pygame.Rect(10, 10, 300, 300),
                                     manager=default_ui_manager)

        selection_list = UISelectionList(relative_rect=pygame.Rect(30, 30, 50, 50),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=default_ui_manager,
                                         container=test_container,
                                         allow_multi_select=True,
                                         anchors={'left': 'left',
                                                  'right': 'left',
                                                  'top': 'top',
                                                  'bottom': 'top'})
        assert selection_list.relative_right_margin is None
        assert selection_list.relative_bottom_margin is None

        selection_list.set_dimensions((20, 20))
        assert selection_list.relative_rect.topleft == (30, 30)
        assert selection_list.relative_rect.size == (20, 20)
        assert selection_list.relative_rect.bottomright == (50, 50)
        assert selection_list.rect.topleft == (40, 40)
        assert selection_list.rect.size == (20, 20)
        assert selection_list.rect.bottomright == (60, 60)
        assert selection_list.relative_right_margin is None
        assert selection_list.relative_bottom_margin is None

        selection_list = UISelectionList(relative_rect=pygame.Rect(-60, 10, 50, 50),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=default_ui_manager,
                                         container=test_container,
                                         allow_multi_select=True,
                                         anchors={'left': 'right',
                                                  'right': 'right',
                                                  'top': 'top',
                                                  'bottom': 'top'})

        assert selection_list.relative_right_margin == 10
        assert selection_list.relative_bottom_margin is None
        selection_list.set_dimensions((60, 60))
        assert selection_list.relative_rect.topleft == (-60, 10)
        assert selection_list.relative_rect.size == (60, 60)
        assert selection_list.relative_rect.bottomright == (0, 70)
        assert selection_list.rect.topleft == (250, 20)
        assert selection_list.rect.size == (60, 60)
        assert selection_list.rect.bottomright == (310, 80)
        assert selection_list.relative_right_margin == 0
        assert selection_list.relative_bottom_margin is None

        selection_list = UISelectionList(relative_rect=pygame.Rect(-70, -70, 50, 50),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=default_ui_manager,
                                         container=test_container,
                                         allow_multi_select=True,
                                         anchors={'left': 'right',
                                                  'right': 'right',
                                                  'top': 'bottom',
                                                  'bottom': 'bottom'})

        assert selection_list.relative_right_margin == 20
        assert selection_list.relative_bottom_margin == 20
        selection_list.set_dimensions((30, 30))
        assert selection_list.relative_rect.topleft == (-70, -70)
        assert selection_list.relative_rect.size == (30, 30)
        assert selection_list.relative_rect.bottomright == (-40, -40)
        assert selection_list.rect.topleft == (240, 240)
        assert selection_list.rect.size == (30, 30)
        assert selection_list.rect.bottomright == (270, 270)
        assert selection_list.relative_right_margin == 40
        assert selection_list.relative_bottom_margin == 40

        selection_list = UISelectionList(relative_rect=pygame.Rect(50, -50, 50, 50),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=default_ui_manager,
                                         container=test_container,
                                         allow_multi_select=True,
                                         anchors={'left': 'left',
                                                  'right': 'left',
                                                  'top': 'bottom',
                                                  'bottom': 'bottom'})

        assert selection_list.relative_right_margin is None
        assert selection_list.relative_bottom_margin == 0

        selection_list.set_dimensions((100, 100))
        assert selection_list.relative_rect.topleft == (50, -50)
        assert selection_list.relative_rect.size == (100, 100)
        assert selection_list.relative_rect.bottomright == (150, 50)
        assert selection_list.rect.topleft == (60, 260)
        assert selection_list.rect.size == (100, 100)
        assert selection_list.rect.bottomright == (160, 360)
        assert selection_list.relative_right_margin is None
        assert selection_list.relative_bottom_margin == -50

        selection_list = UISelectionList(relative_rect=pygame.Rect(10, 10, 50, 50),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=default_ui_manager,
                                         container=test_container,
                                         allow_multi_select=True,
                                         anchors={'left': 'left',
                                                  'right': 'right',
                                                  'top': 'top',
                                                  'bottom': 'bottom'})

        assert selection_list.relative_right_margin == 240
        assert selection_list.relative_bottom_margin == 240

        selection_list.set_dimensions((90, 90))
        assert selection_list.relative_rect.topleft == (10, 10)
        assert selection_list.relative_rect.size == (90, 90)
        assert selection_list.relative_rect.bottomright == (100, 100)
        assert selection_list.rect.topleft == (20, 20)
        assert selection_list.rect.size == (90, 90)
        assert selection_list.rect.bottomright == (110, 110)
        assert selection_list.relative_right_margin == 200
        assert selection_list.relative_bottom_margin == 200

    def test_kill(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                  _display_surface_return_none):
        selection_list = UISelectionList(relative_rect=pygame.Rect(0, 0, 50, 80),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=default_ui_manager,
                                         allow_multi_select=True)

        assert len(default_ui_manager.get_root_container().elements) == 2
        assert len(default_ui_manager.get_sprite_group().sprites()) == 13

        selection_list_sprites = [default_ui_manager.get_root_container(),
                                  selection_list,
                                  selection_list.list_and_scroll_bar_container,
                                  selection_list.item_list_container,
                                  selection_list.scroll_bar,
                                  selection_list.scroll_bar.button_container,
                                  *selection_list.item_list_container.elements,
                                  selection_list.scroll_bar.top_button,
                                  selection_list.scroll_bar.bottom_button,
                                  selection_list.scroll_bar.sliding_button]
        assert default_ui_manager.get_sprite_group().sprites() == selection_list_sprites
        selection_list.kill()
        assert len(default_ui_manager.get_root_container().elements) == 0
        assert len(default_ui_manager.get_sprite_group().sprites()) == 1
        empty_ui_sprites = [default_ui_manager.get_root_container()]
        assert default_ui_manager.get_sprite_group().sprites() == empty_ui_sprites

    def test_rebuild_from_changed_theme_data_non_default(self, _init_pygame,
                                                         _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes",
                                                     "ui_selection_list_non_default.json"))
        selection_list = UISelectionList(relative_rect=pygame.Rect(0, 0, 50, 80),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=manager,
                                         allow_multi_select=True)

        assert selection_list.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    @pytest.mark.filterwarnings("ignore:Invalid gradient")
    @pytest.mark.filterwarnings("ignore:Unable to load")
    def test_rebuild_from_changed_theme_data_bad_values(self, _init_pygame,
                                                        _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data", "themes",
                                                     "ui_selection_list_bad_values.json"))
        selection_list = UISelectionList(relative_rect=pygame.Rect(0, 0, 50, 80),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=manager,
                                         allow_multi_select=True)

        assert selection_list.image is not None

    def test_disable(self, _init_pygame: None, default_ui_manager: UIManager,
                     _display_surface_return_none: None):
        selection_list = UISelectionList(relative_rect=pygame.Rect(50, 50, 150, 400),
                                         item_list=['green', 'eggs', 'and', 'ham'],
                                         manager=default_ui_manager)

        assert selection_list.get_single_selection() is None

        selection_list.disable()
        assert selection_list.is_enabled is False
        assert selection_list.item_list_container.is_enabled is False

        # process a mouse button down event
        list_button = selection_list.item_list_container.elements[0]
        list_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1,
                                                        'pos': list_button.rect.center}))

        # process a mouse button up event
        list_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1,
                                                      'pos': list_button.rect.center}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert selection_list.get_single_selection() is None

    def test_enable(self, _init_pygame: None, default_ui_manager: UIManager,
                    _display_surface_return_none: None):
        selection_list = UISelectionList(relative_rect=pygame.Rect(50, 50, 150, 400),
                                         item_list=['green', 'eggs', 'and', 'ham'],
                                         manager=default_ui_manager)

        assert selection_list.get_single_selection() is None

        selection_list.disable()
        selection_list.enable()
        assert selection_list.is_enabled is True
        assert selection_list.item_list_container.is_enabled is True

        # process a mouse button down event
        list_button = selection_list.item_list_container.elements[0]
        list_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1,
                                                        'pos': list_button.rect.center}))

        # process a mouse button up event
        list_button.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1,
                                                      'pos': list_button.rect.center}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert selection_list.get_single_selection() == 'green'

    def test_show(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        selection_list = UISelectionList(relative_rect=pygame.Rect(0, 0, 50, 80),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=default_ui_manager,
                                         allow_multi_select=True, visible=0)

        assert selection_list.visible == 0
        assert selection_list.dirty == 1

        assert selection_list.list_and_scroll_bar_container.visible == 0
        assert selection_list.item_list_container.visible == 0

        assert selection_list.scroll_bar.visible == 0
        assert selection_list.scroll_bar.button_container.visible == 0
        assert selection_list.scroll_bar.bottom_button.visible == 0
        assert selection_list.scroll_bar.top_button.visible == 0
        assert selection_list.scroll_bar.sliding_button.visible == 0

        selection_list.show()

        assert selection_list.visible == 1
        assert selection_list.dirty == 2

        assert selection_list.list_and_scroll_bar_container.visible == 1
        assert selection_list.item_list_container.visible == 1

        assert selection_list.scroll_bar.visible == 1
        assert selection_list.scroll_bar.button_container.visible == 1
        assert selection_list.scroll_bar.bottom_button.visible == 1
        assert selection_list.scroll_bar.top_button.visible == 1
        assert selection_list.scroll_bar.sliding_button.visible == 1

    def test_hide(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        selection_list = UISelectionList(relative_rect=pygame.Rect(0, 0, 50, 80),
                                         item_list=['item 1', 'item 2', 'item 3', 'item 4',
                                                    'item 5', 'item 6', 'item 7', 'item 8',
                                                    'item 9', 'item 10', 'item 11', 'item 12',
                                                    'item 13', 'item 14', 'item 15', 'item 16'],
                                         manager=default_ui_manager,
                                         allow_multi_select=True)

        assert selection_list.visible == 1
        assert selection_list.dirty == 2

        assert selection_list.list_and_scroll_bar_container.visible == 1
        assert selection_list.item_list_container.visible == 1

        assert selection_list.scroll_bar.visible == 1
        assert selection_list.scroll_bar.button_container.visible == 1
        assert selection_list.scroll_bar.bottom_button.visible == 1
        assert selection_list.scroll_bar.top_button.visible == 1
        assert selection_list.scroll_bar.sliding_button.visible == 1

        selection_list.hide()

        assert selection_list.visible == 0
        assert selection_list.dirty == 1

        assert selection_list.list_and_scroll_bar_container.visible == 0
        assert selection_list.item_list_container.visible == 0

        assert selection_list.scroll_bar.visible == 0
        assert selection_list.scroll_bar.button_container.visible == 0
        assert selection_list.scroll_bar.bottom_button.visible == 0
        assert selection_list.scroll_bar.top_button.visible == 0
        assert selection_list.scroll_bar.sliding_button.visible == 0
