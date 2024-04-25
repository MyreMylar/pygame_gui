import os

import pytest
import pygame

import pygame_gui
from pygame_gui.elements.ui_form import InputField, UISection, UIForm
from pygame_gui.elements import UITextEntryLine, UITextEntryBox, UISelectionList, UIDropDownMenu, UIButton
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.ui_manager import UIManager
from tests.shared_comparators import compare_surfaces


def get_questionnaire():
    test_rect = pygame.Rect(100, 100, 100, 100)
    questionnaire = {
        "Character Test:": "character",
        "Short Text Test:": "short_text",
        "Long Text Test:": "long_text",
        "Integer Test:": "integer",
        "Decimal Test:": "decimal",
        "Password Test:": "password",
        "Boolean Test:": "boolean",

        "Section Test:": {
            "UITextEntryLine Test": UITextEntryLine(test_rect),
            "UITextEntryBox Test": UITextEntryBox(test_rect),
            "UISelectionList Test": UISelectionList(test_rect, ["item 1", "item 2"]),
            "UISelectionList Multiselect Test": UISelectionList(test_rect, ["item 1", "item 2"], allow_multi_select=True),
            "UIDropDownMenu Test": UIDropDownMenu(["item 1", "item 2"], "item 1", test_rect)
        }
    }
    return questionnaire


# class TestUISection:
#     # TODO: Add tests for UISections
#
#     def test_creation(self, _init_pygame, default_ui_manager, _display_surface_return_none):
#         form = UIForm(pygame.Rect(100, 100, 200, 200), questionnaire=get_questionnaire(), manager=default_ui_manager)
#         UISection(pygame.Rect(100, 100, 200, 200), form, "section", questionnaire=get_questionnaire(), manager=default_ui_manager)


class TestUIForm:

    # TODO: Add tests testing various inputs
    # TODO: Add tests for validate_questionnaire
    # TODO: Add tests for theming

    def test_creation(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        UIForm(pygame.Rect(100, 100, 200, 200), questionnaire=get_questionnaire(), manager=default_ui_manager)

    def test_get_container(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                           _display_surface_return_none):
        container = UIForm(pygame.Rect(100, 100, 200, 200), questionnaire=get_questionnaire(),
                           manager=default_ui_manager)
        assert container.get_container() == container.scrollable_container

    def test_add_element(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                         _display_surface_return_none):
        container = UIForm(pygame.Rect(100, 100, 200, 200), questionnaire=get_questionnaire(),
                           manager=default_ui_manager)
        assert len(container.get_container().elements) == 16

        button = UIButton(relative_rect=pygame.Rect(0, 0, 50, 50), text="",
                          manager=default_ui_manager)
        default_ui_manager.get_root_container().remove_element(button)
        container.get_container().add_element(button)
        assert len(container.get_container().elements) == 17

        button = UIButton(relative_rect=pygame.Rect(0, 0, 50, 250), text="",
                          manager=default_ui_manager)
        default_ui_manager.get_root_container().remove_element(button)
        container.get_container().add_element(button)
        container.scrollable_container.update(0.4)
        container.update(0.4)
        assert len(container.get_container().elements) == 18

    def test_remove_element(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                            _display_surface_return_none):
        container = UIForm(pygame.Rect(100, 100, 200, 200), questionnaire=get_questionnaire(),
                           manager=default_ui_manager)
        assert len(container.get_container().elements) == 16

        button = UIButton(relative_rect=pygame.Rect(0, 0, 50, 50), text="",
                          manager=default_ui_manager,
                          container=container)

        container.get_container().remove_element(button)
        assert len(container.get_container().elements) == 16

    def test_set_position(self, _init_pygame, default_ui_manager,
                          _display_surface_return_none):
        container = UIForm(pygame.Rect(100, 100, 200, 200), questionnaire=get_questionnaire(),
                           manager=default_ui_manager)

        container.set_position((50, 50))

        assert container.rect.topleft == (50, 50)
        assert container._root_container.rect.size == (194, 194)

    def test_set_relative_position(self, _init_pygame, default_ui_manager,
                                   _display_surface_return_none):
        container = UIForm(pygame.Rect(100, 100, 200, 200), questionnaire=get_questionnaire(),
                           manager=default_ui_manager)
        container_2 = UIForm(pygame.Rect(50, 50, 50, 50),
                             manager=default_ui_manager,
                             container=container)

        container_2.set_relative_position((25, 25))

        assert container_2.rect.topleft == (128, 128)

    def test_set_dimensions(self, _init_pygame, default_ui_manager,
                            _display_surface_return_none):
        container = UIForm(pygame.Rect(100, 100, 200, 200), questionnaire=get_questionnaire(),
                           manager=default_ui_manager)
        # TODO: Find out why it crashes when set to 50 or lesser in x axis or 5 or lesser in y axis
        # TODO: Find out why it crashes when placing a UIForm inside a UIForm
        container.set_dimensions((100, 100))
        assert container.rect.size == (100, 100)

    def test_disable(self, _init_pygame: None, default_ui_manager: UIManager,
                     _display_surface_return_none: None):
        container = UIForm(pygame.Rect(100, 100, 200, 200), questionnaire=get_questionnaire(),
                           manager=default_ui_manager)
        button_1 = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                            text="Test Button",
                            tool_tip_text="This is a test of the button's tool tip functionality.",
                            manager=default_ui_manager,
                            container=container)

        button_2 = UIButton(relative_rect=pygame.Rect(10, 50, 150, 30),
                            text="Test Button 2",
                            manager=default_ui_manager,
                            container=container)

        element = container.parsed_questionnaire["Character Test:"].element

        container.disable()

        assert container.is_enabled is False
        assert button_1.is_enabled is False
        assert button_2.is_enabled is False
        assert element.is_enabled is False

        # process a mouse button down event
        button_1.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': button_1.rect.center}))

        # process a mouse button up event
        button_1.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': button_1.rect.center}))

        button_1.update(0.01)

        assert button_1.check_pressed() is False

        # process input

        default_ui_manager.mouse_position = element.rect.center
        default_ui_manager.process_events(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": pygame.BUTTON_LEFT, "pos": element.rect.center})
        )
        default_ui_manager.process_events(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": pygame.BUTTON_LEFT, "pos": element.rect.center})
        )
        element.process_event(pygame.event.Event(pygame.TEXTINPUT, {"text": "abc"}))
        assert container.get_current_values()["Character Test:"] == ''

    def test_enable(self, _init_pygame: None, default_ui_manager: UIManager,
                    _display_surface_return_none: None):
        container = UIForm(pygame.Rect(100, 100, 200, 200), questionnaire=get_questionnaire(),
                           manager=default_ui_manager)
        button_1 = UIButton(relative_rect=pygame.Rect(10, 10, 150, 30),
                            text="Test Button",
                            tool_tip_text="This is a test of the button's tool tip functionality.",
                            manager=default_ui_manager,
                            container=container)

        button_2 = UIButton(relative_rect=pygame.Rect(10, 50, 150, 30),
                            text="Test Button 2",
                            manager=default_ui_manager,
                            container=container)

        element = container.parsed_questionnaire["Character Test:"].element

        container.disable()
        container.enable()

        assert container.is_enabled is True
        assert button_1.is_enabled is True
        assert button_2.is_enabled is True
        assert element.is_enabled is True

        # process a mouse button down event
        button_1.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': button_1.rect.center}))

        # process a mouse button up event
        button_1.process_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': button_1.rect.center}))

        button_1.update(0.01)

        assert button_1.check_pressed() is True

        # process input

        default_ui_manager.mouse_position = element.rect.center
        default_ui_manager.process_events(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": pygame.BUTTON_LEFT, "pos": element.rect.center})
        )
        default_ui_manager.process_events(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": pygame.BUTTON_LEFT, "pos": element.rect.center})
        )
        element.process_event(pygame.event.Event(pygame.TEXTINPUT, {"text": "abc"}))
        assert container.get_current_values()["Character Test:"] == 'a'

    def test_show(self, _init_pygame, default_ui_manager,
                  _display_surface_return_none):
        container = UIForm(relative_rect=pygame.Rect(100, 100, 400, 400),
                           manager=default_ui_manager, visible=0)

        assert container.visible == 0

        assert container._root_container.visible == 0
        assert container._view_container.visible == 0
        assert container.vert_scroll_bar.visible == 0
        assert container.scrollable_container.visible == 0

        container.show()

        assert container.visible == 1

        assert container._root_container.visible == 1
        assert container._view_container.visible == 1
        assert container.vert_scroll_bar.visible == 1
        assert container.scrollable_container.visible == 1

    def test_hide(self, _init_pygame, default_ui_manager,
                  _display_surface_return_none):
        container = UIForm(relative_rect=pygame.Rect(100, 100, 400, 400),
                           manager=default_ui_manager)

        assert container.visible == 1

        assert container._root_container.visible == 1
        assert container._view_container.visible == 1
        assert container.vert_scroll_bar.visible == 1
        assert container.scrollable_container.visible == 1

        container.hide()

        assert container.visible == 0

        assert container._root_container.visible == 0
        assert container._view_container.visible == 0
        assert container.vert_scroll_bar.visible == 0
        assert container.scrollable_container.visible == 0

    def test_show_hide_rendering(self, _init_pygame, default_ui_manager, _display_surface_return_none):
        resolution = (400, 400)
        empty_surface = pygame.Surface(resolution)
        empty_surface.fill(pygame.Color(0, 0, 0))

        surface = empty_surface.copy()
        manager = UIManager(resolution)

        container = UIForm(relative_rect=pygame.Rect(100, 100, 200, 100),
                           manager=manager,
                           visible=0)
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        container.show()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert not compare_surfaces(empty_surface, surface)

        surface.fill(pygame.Color(0, 0, 0))
        container.hide()
        manager.update(0.01)
        manager.draw_ui(surface)
        assert compare_surfaces(empty_surface, surface)

    def test_get_current_values(self, _init_pygame, default_ui_manager: IUIManagerInterface,
                                _display_surface_return_none):
        questionnaire = get_questionnaire()
        container = UIForm(pygame.Rect(100, 100, 200, 200), questionnaire=questionnaire,
                           manager=default_ui_manager)

        assert container.get_current_values() == {'Character Test:': '', 'Short Text Test:': '', 'Long Text Test:': '',
                                                  'Integer Test:': 0, 'Decimal Test:': 0.0, 'Password Test:': '',
                                                  'Boolean Test:': True,
                                                  'Section Test:': {
                                                      'UITextEntryLine Test': '',
                                                      'UITextEntryBox Test': '',
                                                      'UISelectionList Test': None,
                                                      'UISelectionList Multiselect Test': [],
                                                      'UIDropDownMenu Test': 'item 1'
                                                  }
                                                  }

        container.kill()

        # Character Test

        container = UIForm(pygame.Rect(100, 100, 200, 200), questionnaire=questionnaire,
                           manager=default_ui_manager)
        element = container.parsed_questionnaire["Character Test:"].element

        default_ui_manager.mouse_position = element.rect.center
        default_ui_manager.process_events(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": pygame.BUTTON_LEFT, "pos": element.rect.center})
        )
        default_ui_manager.process_events(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": pygame.BUTTON_LEFT, "pos": element.rect.center})
        )
        element.process_event(pygame.event.Event(pygame.TEXTINPUT, {"text": "abc"}))
        assert container.get_current_values()["Character Test:"] == 'a'

        container.kill()
        questionnaire.pop("Character Test:")

        # Short Text Test

        container = UIForm(pygame.Rect(100, 100, 200, 200), questionnaire=questionnaire,
                           manager=default_ui_manager)
        element = container.parsed_questionnaire["Short Text Test:"].element

        default_ui_manager.mouse_position = element.rect.center
        default_ui_manager.process_events(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": pygame.BUTTON_LEFT, "pos": element.rect.center})
        )
        default_ui_manager.process_events(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": pygame.BUTTON_LEFT, "pos": element.rect.center})
        )
        element.process_event(pygame.event.Event(pygame.TEXTINPUT, {"text": "abc"}))
        assert container.get_current_values()["Short Text Test:"] == 'abc'

        container.kill()
        questionnaire.pop("Short Text Test:")

        # Long Text Test

        container = UIForm(pygame.Rect(100, 100, 200, 200), questionnaire=questionnaire,
                           manager=default_ui_manager)
        element = container.parsed_questionnaire["Long Text Test:"].element

        default_ui_manager.mouse_position = element.rect.center
        default_ui_manager.process_events(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": pygame.BUTTON_LEFT, "pos": element.rect.center})
        )
        default_ui_manager.process_events(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": pygame.BUTTON_LEFT, "pos": element.rect.center})
        )

        element.process_event(pygame.event.Event(pygame.TEXTINPUT, {"text": "abc"}))
        assert container.get_current_values()["Long Text Test:"] == 'abc'

        container.kill()
        questionnaire.pop("Long Text Test:")

        # Integer Test

        container = UIForm(pygame.Rect(100, 100, 200, 200), questionnaire=questionnaire,
                           manager=default_ui_manager)
        element = container.parsed_questionnaire["Integer Test:"].element

        default_ui_manager.mouse_position = element.rect.center
        default_ui_manager.process_events(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": pygame.BUTTON_LEFT, "pos": element.rect.center})
        )
        default_ui_manager.process_events(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": pygame.BUTTON_LEFT, "pos": element.rect.center})
        )
        element.process_event(pygame.event.Event(pygame.TEXTINPUT, {"text": "a1.b2"}))
        assert container.get_current_values()["Integer Test:"] == 12

        container.kill()
        questionnaire.pop("Integer Test:")

        # Decimal Test

        container = UIForm(pygame.Rect(100, 100, 200, 200), questionnaire=questionnaire,
                           manager=default_ui_manager)

        element = container.parsed_questionnaire["Decimal Test:"].element

        default_ui_manager.mouse_position = element.rect.center
        default_ui_manager.process_events(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": pygame.BUTTON_LEFT, "pos": element.rect.center})
        )
        default_ui_manager.process_events(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": pygame.BUTTON_LEFT, "pos": element.rect.center})
        )
        element.process_event(pygame.event.Event(pygame.TEXTINPUT, {"text": "a1.b2"}))
        assert container.get_current_values()["Decimal Test:"] == 1.2
        element.process_event(pygame.event.Event(pygame.TEXTINPUT, {"text": "a1.b2.c3"}))
        assert container.get_current_values()["Decimal Test:"] == 0.0  # Invalid input results in 0.0

        container.kill()
        questionnaire.pop("Decimal Test:")

        # Password Test

        container = UIForm(pygame.Rect(100, 100, 200, 200), questionnaire=questionnaire,
                           manager=default_ui_manager)

        element = container.parsed_questionnaire["Password Test:"].element

        default_ui_manager.mouse_position = element.rect.center
        default_ui_manager.process_events(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": pygame.BUTTON_LEFT, "pos": element.rect.center})
        )
        default_ui_manager.process_events(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": pygame.BUTTON_LEFT, "pos": element.rect.center})
        )
        element.process_event(pygame.event.Event(pygame.TEXTINPUT, {"text": "abc"}))
        assert container.get_current_values()["Password Test:"] == 'abc'

        container.kill()
        questionnaire.pop("Password Test:")

        # Boolean Test

        container = UIForm(pygame.Rect(100, 100, 200, 200), questionnaire=questionnaire,
                           manager=default_ui_manager)

        element = container.parsed_questionnaire["Boolean Test:"].element

        # Simulate Opening a drop-down
        button = element.current_state.open_button
        default_ui_manager.mouse_position = element.rect.center
        default_ui_manager.process_events(
            pygame.event.Event(pygame_gui.UI_BUTTON_PRESSED, {"mouse_button": pygame.BUTTON_LEFT, 'ui_element': button,
                                                              'ui_object_id': button.most_specific_combined_id})
        )

        element.update(0.1)

        # Simulate selecting an option
        element = element.current_state.options_selection_list.item_list[-1]["button_element"]
        default_ui_manager.process_events(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": pygame.BUTTON_LEFT, "pos": element.rect.center})
        )
        default_ui_manager.process_events(
            pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": pygame.BUTTON_LEFT, "pos": element.rect.center})
        )
        assert container.get_current_values()["Boolean Test:"] is True

        container.kill()
        questionnaire.pop("Boolean Test:")

    def test_rebuild_from_theme_data_non_default(self, _init_pygame,
                                                 _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests", "data",
                                                     "themes",
                                                     "ui_2d_slider_non_default.json"))

    @pytest.mark.filterwarnings("ignore:Invalid value")
    @pytest.mark.filterwarnings("ignore:Colour hex code")
    @pytest.mark.filterwarnings("ignore:Invalid Theme Colour")
    def test_rebuild_from_theme_data_bad_values(self, _init_pygame,
                                                _display_surface_return_none):
        manager = UIManager((800, 600), os.path.join("tests",
                                                     "data",
                                                     "themes",
                                                     "ui_2d_slider_bad_values.json"))

    def test_kill(self, _init_pygame, default_ui_manager,
                  _display_surface_return_none):
        container = UIForm(pygame.Rect(100, 100, 200, 200), questionnaire=get_questionnaire(),
                           manager=default_ui_manager)
        container_2 = UIForm(pygame.Rect(50, 50, 50, 50),
                             manager=default_ui_manager,
                             container=container)

        button = UIButton(relative_rect=pygame.Rect(20, 20, 30, 20), text="X",
                          manager=default_ui_manager, container=container_2)

        container.kill()

        assert not button.alive()
        assert not container_2.alive()
        assert not container.alive()

    def test_check_hover_when_not_able_to_hover(self, _init_pygame, default_ui_manager,
                                                _display_surface_return_none):
        container = UIForm(pygame.Rect(100, 100, 200, 200), questionnaire=get_questionnaire(),
                           manager=default_ui_manager)
        default_ui_manager.mouse_position = (150, 150)
        assert container.check_hover(0.5, False) is True  # already hovering
        container.kill()
        assert container.check_hover(0.5, False) is False  # dead so can't hover anymore

    def test_type_checker(self, _init_pygame, default_ui_manager,
                          _display_surface_return_none):
        # General

        value = UIForm.type_checker("character")
        assert isinstance(value, tuple)
        assert isinstance(value[0], str)
        assert isinstance(value[1], dict)

        # White Space
        w = " \n\t\v\r\f"  # stands for white_spaces
        assert UIForm.type_checker(f"{w}short_text{w}({w}' a' \t\f'b' \t\f\"c\"{w},{w}required{w}={w}True{w}){w}") == ("short_text", {"default": " abc", "required": True})

        # Syntax + Character

        assert UIForm.type_checker("character") == ("character", {})
        assert UIForm.type_checker("character('a')") == ("character", {"default": "a"})
        assert UIForm.type_checker("character(default='a')") == ("character", {"default": "a"})
        assert UIForm.type_checker("character('a',True)") == ("character", {"default": "a", "required": True})
        assert UIForm.type_checker("character('a',False)") == ("character", {"default": "a", "required": False})
        assert UIForm.type_checker("character('a',required=True)") == ("character", {"default": "a", "required": True})
        assert UIForm.type_checker("character(default='a',required=False)") == ("character", {"default": "a", "required": False})

        # Short Text
        assert UIForm.type_checker("short_text('abc', required=True)") == ("short_text", {"default": "abc", "required": True})

        # Long Text
        assert UIForm.type_checker("long_text('abc', required=True)") == ("long_text", {"default": "abc", "required": True})

        # Integer Text
        assert UIForm.type_checker("integer(1,required=True)") == ("integer", {"default": 1, "required": True})

        # Decimal Text
        assert UIForm.type_checker("decimal(1,required=True)") == ("decimal", {"default": 1, "required": True})
        assert UIForm.type_checker("decimal(1.0,required=False)") == ("decimal", {"default": 1.0, "required": False})

        # Password Text
        assert UIForm.type_checker("password('abc', True)") == ("password", {"default": "abc", "required": True})

        # Boolean Text
        assert UIForm.type_checker("boolean(True, True)") == ("boolean", {"default": True, "required": True})
        assert UIForm.type_checker("boolean(False, False)") == ("boolean", {"default": False, "required": False})

    def test_type_checker_bad_values(self, _init_pygame, default_ui_manager,
                                     _display_surface_return_none):
        # General

        with pytest.raises(ValueError, match="Question type 'unknown' is not supported"):
            UIForm.type_checker("unknown")

        with pytest.raises(SyntaxError, match="Parenthesis used without passing parameters for question"):
            UIForm.type_checker("character()")

        with pytest.raises(SyntaxError, match="Found whitespace between keyword or value"):
            UIForm.type_checker("character(de fault='a')")

        with pytest.raises(SyntaxError, match="Found whitespace between keyword or value"):
            UIForm.type_checker("character(a b)")

        with pytest.raises(SyntaxError, match="Found '=' at the beginning of arguments"):
            UIForm.type_checker("character(=)")

        with pytest.raises(SyntaxError, match="Found keyword wrapped in quotes"):
            UIForm.type_checker("character('default'='a')")

        with pytest.raises(SyntaxError, match="No keyword passed for argument before '=' symbol"):
            UIForm.type_checker("character(default='a',=)")

        with pytest.raises(SyntaxError, match="Found 2 consecutive '=' symbols"):
            UIForm.type_checker("character(default==)")

        with pytest.raises(SyntaxError, match="Found comma at the beginning of arguments"):
            UIForm.type_checker("character(,)")

        with pytest.raises(SyntaxError, match="Found 2 consecutive commas"):
            UIForm.type_checker("character(default='a',,)")

        with pytest.raises(SyntaxError, match="No value passed for keyword argument 'default'"):
            UIForm.type_checker("character(default=,)")

        with pytest.raises(NameError, match="'a' is not defined. Perhaps quotes were missed"):
            UIForm.type_checker("character(default=a)")

        with pytest.raises(NameError, match="'a' is not defined. Perhaps quotes were missed"):
            UIForm.type_checker("character(a)")

        with pytest.raises(SyntaxError, match="Found unmatched '"):
            UIForm.type_checker("character(')")

        with pytest.raises(SyntaxError, match="Found unmatched \""):
            UIForm.type_checker("character(\")")

        with pytest.raises(ValueError, match="Question of type 'character' take at most 2 arguments"
                                             " but 3 arguments were passed"):
            UIForm.type_checker("character('a','b','c')")

        with pytest.raises(SyntaxError, match="Found positional argument after keyword argument"):
            UIForm.type_checker("character(default='a', 'b')")

        with pytest.raises(ValueError, match="Unknown parameter 'unknown' for question type 'character'"):
            UIForm.type_checker("character(unknown = 'a')")

        with pytest.raises(SyntaxError, match="Got multiple values for parameter 'default'"):
            UIForm.type_checker("character('a', default='a')")

        # Character

        with pytest.raises(ValueError, match="Invalid value ''ab'' for argument 'default'"):
            UIForm.type_checker("character(default='ab')")

        with pytest.raises(ValueError, match="Invalid value ''ab'' for argument 'default'"):
            UIForm.type_checker("character('ab')")

        # Integer

        with pytest.raises(ValueError, match="Invalid value ''a'' for argument 'default'"):
            UIForm.type_checker("integer('a')")

        with pytest.raises(ValueError, match="Invalid value '2.0' for argument 'default'"):
            UIForm.type_checker("integer(2.0)")

        with pytest.raises(ValueError, match="Invalid value ''2'' for argument 'default'"):
            UIForm.type_checker("integer('2')")

        # Decimal

        with pytest.raises(ValueError, match="Invalid value ''a'' for argument 'default'"):
            UIForm.type_checker("decimal('a')")

        with pytest.raises(ValueError, match="Invalid value ''2.0'' for argument 'default'"):
            UIForm.type_checker("decimal('2.0')")

        # Boolean

        with pytest.raises(ValueError, match="Invalid value ''a'' for argument 'default'"):
            UIForm.type_checker("boolean('a')")

        with pytest.raises(ValueError, match="Invalid value ''True'' for argument 'default'"):
            UIForm.type_checker("boolean(default='True')")

        with pytest.raises(ValueError, match="Invalid value ''False'' for argument 'required'"):
            UIForm.type_checker("boolean(required='False')")

    def test_validate_questionnaire(self, _init_pygame, default_ui_manager,
                                    _display_surface_return_none):
        container = UIForm(pygame.Rect(100, 100, 200, 200), questionnaire=get_questionnaire(),
                           manager=default_ui_manager)

        container.kill()

        assert not container.alive()

    def test_validate_questionnaire_bad_values(self, _init_pygame, default_ui_manager,
                                               _display_surface_return_none):
        container = UIForm(pygame.Rect(100, 100, 200, 200), questionnaire=get_questionnaire(),
                           manager=default_ui_manager)

        container.kill()

        assert not container.alive()


if __name__ == '__main__':
    pytest.console_main()
