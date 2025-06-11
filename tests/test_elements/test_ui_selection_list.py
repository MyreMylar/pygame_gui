import os
import pytest
import pygame
import pygame_gui

from tests.shared_comparators import compare_surfaces

from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.core.ui_container import UIContainer
from pygame_gui.elements.ui_selection_list import UISelectionList
from pygame_gui.ui_manager import UIManager


class TestUISelectionList:
    def test_creation(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        UISelectionList(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            item_list=["green", "eggs", "and", "ham"],
            manager=default_ui_manager,
        )

    def test_rebuild(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        selection_list = UISelectionList(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            item_list=["green", "eggs", "and", "ham"],
            manager=default_ui_manager,
        )

        selection_list.rebuild()

    def test_addition(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        selection_list = UISelectionList(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            item_list=["green", "eggs", "and", "ham"],
            manager=default_ui_manager,
        )

        selection_list.add_items(["spam", ("bad spam", "bad_spam")])

        assert selection_list.item_list[-1]["text"] == "bad spam"

    def test_removal(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        selection_list = UISelectionList(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            item_list=["green", "eggs", "and", "ham", ("bad spam", "bad_spam")],
            manager=default_ui_manager,
        )

        selection_list.remove_items(["ham", ("bad spam", "bad_spam")])

        assert selection_list.item_list[-1]["text"] == "and"

    def test_get_single_selection(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        selection_list = UISelectionList(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            item_list=["green", "eggs", "and", "ham"],
            manager=default_ui_manager,
        )

        assert selection_list.get_single_selection() is None

        event_data = {"ui_element": selection_list.item_list_container.elements[0]}
        press_list_item_event = pygame.event.Event(
            pygame_gui.UI_BUTTON_PRESSED, event_data
        )
        default_ui_manager.process_events(press_list_item_event)

        assert selection_list.get_single_selection() == "green"

        selection_list.item_list[1]["selected"] = True
        with pytest.raises(
            RuntimeError,
            match="More than one item selected in single-selection, selection list",
        ):
            selection_list.get_single_selection()

        multi_selection_list = UISelectionList(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            item_list=["green", "eggs", "and", "ham"],
            manager=default_ui_manager,
            allow_multi_select=True,
        )
        with pytest.raises(
            RuntimeError, match="Requesting single selection, from multi-selection list"
        ):
            multi_selection_list.get_single_selection()

    def test_get_multi_selection(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        selection_list = UISelectionList(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            item_list=["green", "eggs", "and", "ham"],
            manager=default_ui_manager,
            allow_multi_select=True,
        )

        assert selection_list.get_multi_selection() == []

        event_data = {"ui_element": selection_list.item_list_container.elements[0]}
        press_list_item_event = pygame.event.Event(
            pygame_gui.UI_BUTTON_PRESSED, event_data
        )
        default_ui_manager.process_events(press_list_item_event)

        assert selection_list.get_multi_selection() == ["green"]

        event_data = {"ui_element": selection_list.item_list_container.elements[1]}
        press_list_item_event = pygame.event.Event(
            pygame_gui.UI_BUTTON_PRESSED, event_data
        )
        default_ui_manager.process_events(press_list_item_event)
        assert selection_list.get_multi_selection() == ["green", "eggs"]

        single_selection_list = UISelectionList(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            item_list=["green", "eggs", "and", "ham"],
            manager=default_ui_manager,
        )
        with pytest.raises(
            RuntimeError, match="Requesting multi selection, from single-selection list"
        ):
            single_selection_list.get_multi_selection()

    def test_update(
        self, _init_pygame, default_ui_manager, _display_surface_return_none: None
    ):
        selection_list = UISelectionList(
            relative_rect=pygame.Rect(50, 50, 150, 80),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            default_selection=["item 7"],
            allow_multi_select=True,
        )

        assert selection_list.scroll_bar is not None

        visible_items = [
            item["text"]
            for item in selection_list.item_list
            if item["button_element"] is not None
        ]
        assert visible_items == ["item 1", "item 2", "item 3", "item 4"]
        # scroll the list a bit
        selection_list.scroll_bar.has_moved_recently = True
        selection_list.scroll_bar.start_percentage = 0.3
        selection_list.update(time_delta=0.05)

        visible_items = [
            item["text"]
            for item in selection_list.item_list
            if item["button_element"] is not None
        ]
        assert visible_items == ["item 5", "item 6", "item 7", "item 8", "item 9"]

    def test_set_item_list(
        self, _init_pygame, default_ui_manager, _display_surface_return_none: None
    ):
        selection_list = UISelectionList(
            relative_rect=pygame.Rect(50, 50, 150, 80),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            allow_multi_select=True,
        )

        assert selection_list.scroll_bar is not None
        visible_items = [
            item["text"]
            for item in selection_list.item_list
            if item["button_element"] is not None
        ]
        assert visible_items == ["item 1", "item 2", "item 3", "item 4"]

        selection_list.set_item_list(
            [
                "new item 1",
                "new item 2",
                "new item 3",
                "new item 4",
                "new item 5",
                "new item 6",
                "new item 7",
                "new item 8",
                "new item 9",
                "new item 10",
                "new item 11",
                "new item 12",
                "new item 13",
                "new item 14",
                "new item 15",
            ]
        )

        assert selection_list.scroll_bar is not None
        visible_items = [
            item["text"]
            for item in selection_list.item_list
            if item["button_element"] is not None
        ]
        assert visible_items == ["new item 1", "new item 2", "new item 3", "new item 4"]

        selection_list.set_item_list(["another item 1", "another item 2"])

        assert selection_list.scroll_bar is None
        visible_items = [
            item["text"]
            for item in selection_list.item_list
            if item["button_element"] is not None
        ]
        assert visible_items == ["another item 1", "another item 2"]

        with pytest.raises(ValueError):
            selection_list.set_item_list([1, 2, 3])

    def test_process_event(
        self, _init_pygame, default_ui_manager, _display_surface_return_none: None
    ):
        selection_list = UISelectionList(
            relative_rect=pygame.Rect(50, 50, 150, 80),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            allow_multi_select=True,
            allow_double_clicks=True,
        )

        event_data = {"ui_element": selection_list.item_list_container.elements[0]}
        select_event = pygame.event.Event(pygame_gui.UI_BUTTON_PRESSED, event_data)

        selection_list.process_event(select_event)

        confirm_event_fired = False
        event_text = None
        for event in pygame.event.get():
            if (
                event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION
                and event.ui_element == selection_list
            ):
                confirm_event_fired = True
                event_text = event.text

        assert confirm_event_fired
        assert event_text == "item 1"

        event_data = {"ui_element": selection_list.item_list_container.elements[0]}
        unselect_event = pygame.event.Event(pygame_gui.UI_BUTTON_PRESSED, event_data)

        selection_list.process_event(unselect_event)

        confirm_event_fired = False
        event_text = None
        for event in pygame.event.get():
            if (
                event.type == pygame_gui.UI_SELECTION_LIST_DROPPED_SELECTION
                and event.ui_element == selection_list
            ):
                confirm_event_fired = True
                event_text = event.text

        assert confirm_event_fired
        assert event_text == "item 1"

        event_data = {"ui_element": selection_list.item_list_container.elements[0]}
        double_clicked_event = pygame.event.Event(
            pygame_gui.UI_BUTTON_DOUBLE_CLICKED, event_data
        )

        selection_list.process_event(double_clicked_event)

        confirm_event_fired = False
        event_text = None
        for event in pygame.event.get():
            if (
                event.type == pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION
                and event.ui_element == selection_list
            ):
                confirm_event_fired = True
                event_text = event.text

        assert confirm_event_fired
        assert event_text == "item 1"

        single_selection_list = UISelectionList(
            relative_rect=pygame.Rect(50, 50, 150, 80),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            allow_multi_select=False,
            allow_double_clicks=True,
        )

        event_data = {
            "ui_element": single_selection_list.item_list_container.elements[0]
        }
        select_event = pygame.event.Event(pygame_gui.UI_BUTTON_PRESSED, event_data)

        single_selection_list.process_event(select_event)

        event_data = {
            "ui_element": single_selection_list.item_list_container.elements[1]
        }
        select_another_event = pygame.event.Event(
            pygame_gui.UI_BUTTON_PRESSED, event_data
        )

        single_selection_list.process_event(select_another_event)

        dropped_event_text = None
        select_event_text = None
        for event in pygame.event.get():
            if (
                event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION
                and event.ui_element == single_selection_list
            ):
                select_event_text = event.text

            if (
                event.type == pygame_gui.UI_SELECTION_LIST_DROPPED_SELECTION
                and event.ui_element == single_selection_list
            ):
                dropped_event_text = event.text

        assert select_event_text == "item 2" and dropped_event_text == "item 1"

    def test_set_relative_position(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        test_container = UIContainer(
            relative_rect=pygame.Rect(100, 100, 300, 300), manager=default_ui_manager
        )
        selection_list = UISelectionList(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            container=test_container,
            allow_multi_select=True,
            anchors={"left": "left", "right": "left", "top": "top", "bottom": "top"},
        )

        selection_list.set_relative_position((20, 20))
        assert selection_list.rect.topleft == (120, 120)
        assert selection_list.rect.size == (50, 50)
        assert selection_list.rect.bottomright == (170, 170)

        selection_list = UISelectionList(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            container=test_container,
            allow_multi_select=True,
            anchors={"left": "right", "right": "right", "top": "top", "bottom": "top"},
        )

        selection_list.set_relative_position((-20, 20))
        assert selection_list.rect.topleft == (380, 120)
        assert selection_list.rect.size == (50, 50)
        assert selection_list.rect.bottomright == (430, 170)

        selection_list = UISelectionList(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            container=test_container,
            allow_multi_select=True,
            anchors={
                "left": "right",
                "right": "right",
                "top": "bottom",
                "bottom": "bottom",
            },
        )

        selection_list.set_relative_position((-70, -70))
        assert selection_list.rect.topleft == (330, 330)
        assert selection_list.rect.size == (50, 50)
        assert selection_list.rect.bottomright == (380, 380)

        selection_list = UISelectionList(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            container=test_container,
            allow_multi_select=True,
            anchors={
                "left": "left",
                "right": "left",
                "top": "bottom",
                "bottom": "bottom",
            },
        )

        selection_list.set_relative_position((30, -70))
        assert selection_list.rect.topleft == (130, 330)
        assert selection_list.rect.size == (50, 50)
        assert selection_list.rect.bottomright == (180, 380)

        selection_list = UISelectionList(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            container=test_container,
            allow_multi_select=True,
            anchors={
                "left": "left",
                "right": "right",
                "top": "top",
                "bottom": "bottom",
            },
        )

        assert selection_list.relative_right_margin == 250
        assert selection_list.relative_bottom_margin == 250

        selection_list.set_relative_position((20, 20))
        assert selection_list.rect.topleft == (120, 120)
        assert selection_list.rect.size == (50, 50)
        assert selection_list.rect.bottomright == (170, 170)
        assert selection_list.relative_right_margin == 230
        assert selection_list.relative_bottom_margin == 230

    def test_set_position(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        test_container = UIContainer(
            relative_rect=pygame.Rect(10, 10, 300, 300), manager=default_ui_manager
        )

        selection_list = UISelectionList(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            container=test_container,
            allow_multi_select=True,
            anchors={"left": "left", "right": "left", "top": "top", "bottom": "top"},
        )

        selection_list.set_position((20, 20))
        assert selection_list.relative_rect.topleft == (10, 10)
        assert selection_list.relative_rect.size == (50, 50)
        assert selection_list.relative_rect.bottomright == (60, 60)

        selection_list = UISelectionList(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            container=test_container,
            allow_multi_select=True,
            anchors={"left": "right", "right": "right", "top": "top", "bottom": "top"},
        )

        selection_list.set_position((280, 120))
        assert selection_list.relative_rect.topleft == (-30, 110)
        assert selection_list.relative_rect.size == (50, 50)
        assert selection_list.relative_rect.bottomright == (20, 160)

        selection_list = UISelectionList(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            container=test_container,
            allow_multi_select=True,
            anchors={
                "left": "right",
                "right": "right",
                "top": "bottom",
                "bottom": "bottom",
            },
        )

        selection_list.set_position((230, 230))
        assert selection_list.relative_rect.topleft == (-80, -80)
        assert selection_list.relative_rect.size == (50, 50)
        assert selection_list.relative_rect.bottomright == (-30, -30)

        selection_list = UISelectionList(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            container=test_container,
            allow_multi_select=True,
            anchors={
                "left": "left",
                "right": "left",
                "top": "bottom",
                "bottom": "bottom",
            },
        )

        selection_list.set_position((130, 230))
        assert selection_list.relative_rect.topleft == (120, -80)
        assert selection_list.relative_rect.size == (50, 50)
        assert selection_list.relative_rect.bottomright == (170, -30)

        selection_list = UISelectionList(
            relative_rect=pygame.Rect(0, 0, 50, 50),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            container=test_container,
            allow_multi_select=True,
            anchors={
                "left": "left",
                "right": "right",
                "top": "top",
                "bottom": "bottom",
            },
        )

        assert selection_list.relative_right_margin == 250
        assert selection_list.relative_bottom_margin == 250

        selection_list.set_position((20, 20))
        assert selection_list.relative_rect.topleft == (10, 10)
        assert selection_list.relative_rect.size == (50, 50)
        assert selection_list.relative_rect.bottomright == (60, 60)
        assert selection_list.relative_right_margin == 240
        assert selection_list.relative_bottom_margin == 240

    def test_set_dimensions(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        test_container = UIContainer(
            relative_rect=pygame.Rect(10, 10, 300, 300), manager=default_ui_manager
        )

        selection_list = UISelectionList(
            relative_rect=pygame.Rect(30, 30, 50, 50),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            container=test_container,
            allow_multi_select=True,
            anchors={"left": "left", "right": "left", "top": "top", "bottom": "top"},
        )
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

        selection_list = UISelectionList(
            relative_rect=pygame.Rect(-60, 10, 50, 50),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            container=test_container,
            allow_multi_select=True,
            anchors={"left": "right", "right": "right", "top": "top", "bottom": "top"},
        )

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

        selection_list = UISelectionList(
            relative_rect=pygame.Rect(-70, -70, 50, 50),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            container=test_container,
            allow_multi_select=True,
            anchors={
                "left": "right",
                "right": "right",
                "top": "bottom",
                "bottom": "bottom",
            },
        )

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

        selection_list = UISelectionList(
            relative_rect=pygame.Rect(50, -50, 50, 50),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            container=test_container,
            allow_multi_select=True,
            anchors={
                "left": "left",
                "right": "left",
                "top": "bottom",
                "bottom": "bottom",
            },
        )

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

        selection_list = UISelectionList(
            relative_rect=pygame.Rect(10, 10, 50, 50),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            container=test_container,
            allow_multi_select=True,
            anchors={
                "left": "left",
                "right": "right",
                "top": "top",
                "bottom": "bottom",
            },
        )

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

        selection_list = UISelectionList(
            relative_rect=pygame.Rect(30, 30, 100, 500),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            container=test_container,
            allow_multi_select=True,
            anchors={"left": "left", "right": "left", "top": "top", "bottom": "top"},
        )

        # check creating and destroying scrollbar by resizing
        assert selection_list.scroll_bar is None

        selection_list.set_dimensions((100, 50))

        assert selection_list.scroll_bar is not None

        selection_list.set_dimensions((100, 500))

        assert selection_list.scroll_bar is None

    def test_kill(
        self,
        _init_pygame,
        default_ui_manager: IUIManagerInterface,
        _display_surface_return_none,
    ):
        selection_list = UISelectionList(
            relative_rect=pygame.Rect(0, 0, 50, 80),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            allow_multi_select=True,
        )

        assert len(default_ui_manager.get_root_container().elements) == 2
        assert len(default_ui_manager.get_sprite_group().sprites()) == 13

        selection_list_sprites = [
            default_ui_manager.get_root_container(),
            selection_list,
            selection_list.list_and_scroll_bar_container,
            selection_list.item_list_container,
            selection_list.scroll_bar,
            selection_list.scroll_bar.button_container,
            *selection_list.item_list_container.elements,
            selection_list.scroll_bar.top_button,
            selection_list.scroll_bar.bottom_button,
            selection_list.scroll_bar.sliding_button,
        ]
        assert default_ui_manager.get_sprite_group().sprites() == selection_list_sprites
        selection_list.kill()
        assert len(default_ui_manager.get_root_container().elements) == 0
        assert len(default_ui_manager.get_sprite_group().sprites()) == 1
        empty_ui_sprites = [default_ui_manager.get_root_container()]
        assert default_ui_manager.get_sprite_group().sprites() == empty_ui_sprites

    def test_rebuild_from_changed_theme_data_non_default(
        self, _init_pygame, _display_surface_return_none
    ):
        manager = UIManager(
            (800, 600),
            os.path.join(
                "tests", "data", "themes", "ui_selection_list_non_default.json"
            ),
        )
        selection_list = UISelectionList(
            relative_rect=pygame.Rect(0, 0, 50, 80),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=manager,
            allow_multi_select=True,
        )

        assert selection_list.image is not None

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    @pytest.mark.filterwarnings("ignore:Invalid gradient")
    @pytest.mark.filterwarnings("ignore:Unable to load")
    @pytest.mark.filterwarnings("ignore:Invalid Theme Colour")
    @pytest.mark.filterwarnings("ignore:Theme validation found")
    @pytest.mark.filterwarnings("ignore:Misc data validation")
    @pytest.mark.filterwarnings("ignore:Font data validation")
    @pytest.mark.filterwarnings("ignore:Image data validation")
    def test_rebuild_from_changed_theme_data_bad_values(
        self, _init_pygame, _display_surface_return_none
    ):
        manager = UIManager(
            (800, 600),
            os.path.join(
                "tests", "data", "themes", "ui_selection_list_bad_values.json"
            ),
        )
        selection_list = UISelectionList(
            relative_rect=pygame.Rect(0, 0, 50, 80),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=manager,
            allow_multi_select=True,
        )

        assert selection_list.image is not None

    def test_disable(
        self,
        _init_pygame: None,
        default_ui_manager: UIManager,
        _display_surface_return_none: None,
    ):
        selection_list = UISelectionList(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            item_list=["green", "eggs", "and", "ham"],
            manager=default_ui_manager,
        )

        assert selection_list.get_single_selection() is None

        selection_list.disable()
        assert selection_list.is_enabled is False
        assert selection_list.item_list_container.is_enabled is False

        # process a mouse button down event
        list_button = selection_list.item_list_container.elements[0]
        list_button.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": list_button.rect.center}
            )
        )

        # process a mouse button up event
        list_button.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONUP, {"button": 1, "pos": list_button.rect.center}
            )
        )

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert selection_list.get_single_selection() is None

    def test_enable(
        self,
        _init_pygame: None,
        default_ui_manager: UIManager,
        _display_surface_return_none: None,
    ):
        selection_list = UISelectionList(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            item_list=["green", "eggs", "and", "ham"],
            manager=default_ui_manager,
        )

        assert selection_list.get_single_selection() is None

        selection_list.disable()
        selection_list.enable()
        assert selection_list.is_enabled is True
        assert selection_list.item_list_container.is_enabled is True

        # process a mouse button down event
        list_button = selection_list.item_list_container.elements[0]
        list_button.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": list_button.rect.center}
            )
        )

        # process a mouse button up event
        list_button.process_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONUP, {"button": 1, "pos": list_button.rect.center}
            )
        )

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert selection_list.get_single_selection() == "green"

    def test_show(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        selection_list = UISelectionList(
            relative_rect=pygame.Rect(0, 0, 50, 80),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            allow_multi_select=True,
            visible=0,
        )

        assert selection_list.visible == 0

        assert selection_list.list_and_scroll_bar_container.visible == 0
        assert selection_list.item_list_container.visible == 0

        assert selection_list.scroll_bar.visible == 0
        assert selection_list.scroll_bar.button_container.visible == 0
        assert selection_list.scroll_bar.bottom_button.visible == 0
        assert selection_list.scroll_bar.top_button.visible == 0
        assert selection_list.scroll_bar.sliding_button.visible == 0

        selection_list.show()

        assert selection_list.visible == 1

        assert selection_list.list_and_scroll_bar_container.visible == 1
        assert selection_list.item_list_container.visible == 1

        assert selection_list.scroll_bar.visible == 1
        assert selection_list.scroll_bar.button_container.visible == 1
        assert selection_list.scroll_bar.bottom_button.visible == 1
        assert selection_list.scroll_bar.top_button.visible == 1
        assert selection_list.scroll_bar.sliding_button.visible == 1

    def test_hide(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        selection_list = UISelectionList(
            relative_rect=pygame.Rect(0, 0, 50, 80),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=default_ui_manager,
            allow_multi_select=True,
        )

        assert selection_list.visible == 1

        assert selection_list.list_and_scroll_bar_container.visible == 1
        assert selection_list.item_list_container.visible == 1

        assert selection_list.scroll_bar.visible == 1
        assert selection_list.scroll_bar.button_container.visible == 1
        assert selection_list.scroll_bar.bottom_button.visible == 1
        assert selection_list.scroll_bar.top_button.visible == 1
        assert selection_list.scroll_bar.sliding_button.visible == 1

        selection_list.hide()

        assert selection_list.visible == 0

        assert selection_list.list_and_scroll_bar_container.visible == 0
        assert selection_list.item_list_container.visible == 0

        assert selection_list.scroll_bar.visible == 0
        assert selection_list.scroll_bar.button_container.visible == 0
        assert selection_list.scroll_bar.bottom_button.visible == 0
        assert selection_list.scroll_bar.top_button.visible == 0
        assert selection_list.scroll_bar.sliding_button.visible == 0

    def test_show_hide_rendering(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        resolution = (400, 400)
        empty_surface = pygame.Surface(resolution)
        empty_surface.fill(pygame.Color(0, 0, 0))

        surface = empty_surface.copy()
        manager = UIManager(resolution)

        selection_list = UISelectionList(
            relative_rect=pygame.Rect(100, 100, 400, 400),
            item_list=[
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
                "item 7",
                "item 8",
                "item 9",
                "item 10",
                "item 11",
                "item 12",
                "item 13",
                "item 14",
                "item 15",
                "item 16",
            ],
            manager=manager,
            allow_multi_select=True,
            visible=0,
        )
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        selection_list.show()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert not compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        selection_list.hide()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

    def test_default_selection_exceptions(
        self, _init_pygame, _display_surface_return_none
    ):
        """
        Test that all exceptions throw appropriately:
        1. ValueError if a list of strings/string tuples is passed to a single-selection list.
        2. TypeError is a completely invalid type (like an object) is passed.
        3. ValueError if ANY of the requested default values are not actually present in the item
            list.
        """
        resolution = (400, 400)
        manager = UIManager(resolution)
        lst = [f"item {n}" for n in range(20)]

        # Test Case 1
        test_case_1_throws = False
        try:
            UISelectionList(
                relative_rect=pygame.Rect(100, 100, 400, 400),
                item_list=lst,
                default_selection=["item 1", "item 2"],
                manager=manager,
            )
        except ValueError as e:
            assert "Multiple default values" in str(e)
            test_case_1_throws = True

        assert test_case_1_throws is True

        # Test Case 2
        test_case_2_throws = False
        try:
            UISelectionList(
                relative_rect=pygame.Rect(100, 100, 400, 400),
                item_list=lst,
                default_selection=4,
                manager=manager,
            )
        except TypeError as e:
            assert "is not a string or (str, str) tuple." in str(e)
            test_case_2_throws = True

        assert test_case_2_throws is True

        # Test Case 3 for single-selection lists
        test_case_3_single_throws = False
        try:
            UISelectionList(
                relative_rect=pygame.Rect(100, 100, 400, 400),
                item_list=lst,
                default_selection="I am not in the list",
                manager=manager,
            )
        except ValueError as e:
            assert "not found in selection list" in str(e)
            test_case_3_single_throws = True

        assert test_case_3_single_throws is True

        # Test Case 4 for multi-select lists.
        test_case_3_multiple_throws = False
        try:
            UISelectionList(
                relative_rect=pygame.Rect(100, 100, 400, 400),
                item_list=lst,
                default_selection=["item 1", "I am not in the list"],
                allow_multi_select=True,
                manager=manager,
            )
        except ValueError as e:
            assert "not found in selection list" in str(e)
            test_case_3_multiple_throws = True

        assert test_case_3_multiple_throws is True

    def test_default_selection_sets_correctly(
        self, _init_pygame, _display_surface_return_none
    ):
        """
        Test that the default selection parameter ACTUALLY sets the values.
        """
        resolution = (400, 400)
        manager = UIManager(resolution)
        lst = [f"item {i}" for i in range(20)]
        selection = "item 10"

        # Single-selection list default.
        single_list = UISelectionList(
            relative_rect=pygame.Rect(100, 100, 400, 400),
            item_list=lst,
            default_selection=selection,
            manager=manager,
        )

        assert selection == single_list.get_single_selection()

        # Multi-selection list defaults.
        selection = ["item 3", "item 10", "item 15"]
        multi_list = UISelectionList(
            relative_rect=pygame.Rect(100, 100, 400, 400),
            item_list=lst,
            default_selection=selection,
            allow_multi_select=True,
            manager=manager,
        )

        assert selection == multi_list.get_multi_selection()

        selection = [("Item 2", "#item_2"), ("Item 3", "#item_3")]
        # tuple list
        multi_list = UISelectionList(
            relative_rect=pygame.Rect(100, 100, 400, 400),
            item_list=[
                ("Item 1", "#item_1"),
                ("Item 2", "#item_2"),
                ("Item 3", "#item_3"),
            ],
            default_selection=selection,
            allow_multi_select=True,
            manager=manager,
        )

        assert multi_list.get_multi_selection() == ["Item 2", "Item 3"]

    def test_default_selection_changes(
        self,
        _init_pygame,
        default_ui_manager,
        default_display_surface,
        _display_surface_return_none,
    ):
        """
        Test that the default selection parameter does not permanently fix the list selection.
        """
        resolution = (400, 400)
        manager = UIManager(resolution)
        lst = [f"item {i}" for i in range(0, 20)]
        default = 10
        new_selection = 5

        # Test single selection list
        single_list = UISelectionList(
            relative_rect=pygame.Rect(100, 100, 400, 400),
            item_list=lst,
            default_selection=lst[default],
            manager=manager,
        )

        event_data = {
            "ui_element": single_list.item_list_container.elements[new_selection]
        }
        select_event = pygame.event.Event(pygame_gui.UI_BUTTON_PRESSED, event_data)
        single_list.process_event(select_event)

        assert lst[new_selection] == single_list.get_single_selection()

        # Test multi-selection list
        default = [lst[10], lst[17]]
        selections = [4, 10, 15]

        multi_list = UISelectionList(
            relative_rect=pygame.Rect(100, 100, 400, 400),
            item_list=lst,
            default_selection=default,
            allow_multi_select=True,
            manager=manager,
        )

        for selection in selections:
            event_data = {
                "ui_element": multi_list.item_list_container.elements[selection]
            }
            select_event = pygame.event.Event(pygame_gui.UI_BUTTON_PRESSED, event_data)
            multi_list.process_event(select_event)

        final_vals = multi_list.get_multi_selection()
        assert len(final_vals) == 3
        assert lst[10] not in final_vals
        assert lst[4] in final_vals
        assert lst[15] in final_vals
        assert lst[17] in final_vals

    def test_set_default_selection(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        selection_list = UISelectionList(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            item_list=["green", "eggs", "and", "ham"],
            manager=default_ui_manager,
            allow_multi_select=True,
        )

        assert selection_list.get_multi_selection() == []

        event_data = {"ui_element": selection_list.item_list_container.elements[0]}
        press_list_item_event = pygame.event.Event(
            pygame_gui.UI_BUTTON_PRESSED, event_data
        )
        default_ui_manager.process_events(press_list_item_event)

        assert selection_list.get_multi_selection() == ["green"]

        selection_list._default_selection = ["eggs"]
        selection_list._set_default_selection()

        assert selection_list.get_multi_selection() == ["green"]

    def test_get_single_selection_start_percentage(
        self, _init_pygame, default_ui_manager, _display_surface_return_none
    ):
        selection_list = UISelectionList(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            item_list=["green", "eggs", "and", "ham"],
            manager=default_ui_manager,
            default_selection="green",
        )
        assert selection_list.get_single_selection_start_percentage() == 0.0

        selection_list = UISelectionList(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            item_list=["green", "eggs", "and", "ham"],
            manager=default_ui_manager,
            default_selection="and",
        )
        assert selection_list.get_single_selection_start_percentage() == 0.5

        selection_list = UISelectionList(
            relative_rect=pygame.Rect(50, 50, 150, 400),
            item_list=["green", "eggs", "and", "ham"],
            manager=default_ui_manager,
            allow_multi_select=True,
        )
        assert selection_list.get_single_selection_start_percentage() == 0.0


if __name__ == "__main__":
    pytest.console_main()
