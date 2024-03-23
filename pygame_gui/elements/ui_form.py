import pygame

from pygame_gui._constants import UI_BUTTON_PRESSED, OldType, UI_FORM_SUBMITTED
from pygame_gui.core import UIElement, ObjectID
from pygame_gui.core.interfaces import IUIElementInterface, IUIManagerInterface, IContainerLikeInterface
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape
from pygame_gui.elements import UIAutoResizingContainer, UIAutoScrollingContainer
from pygame_gui.elements import UITextEntryLine, UITextEntryBox, UISelectionList, UIDropDownMenu, UILabel, UIButton

import re
from ast import literal_eval
from typing import *


class InputField(NamedTuple):
    """
    This NamedTuple is used within parsed questionnaires to store elements which take input, which were created from
    default types supported by UIForm, like short_text, long_text etc.
    """
    question_type: str
    label: UILabel
    element: Union[UITextEntryLine, UITextEntryBox, UIDropDownMenu]


class UISection(UIAutoResizingContainer):
    """
    A Section is a part of the UIForm which can contain questions or more sections. This behaviour is used to create
    nested structures when required. A section can be expanded/contracted using a button created at initialisation.

    :param relative_rect: The starting size and relative position of the section. The height will be calculated
    automatically by the section. Therefore, any height passed in will have no effect on the section.
    :param form: The UIForm element this section belongs to
    :param name: The name of the section.
    :param questionnaire: The section in the main questionnaire to handle.
    :param manager: The UI manager for this element. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param starting_height: The starting layer height of this container above its container.
                            Defaults to 1.
    :param container: The container this container is within. Defaults to None (which is the root
                      container for the UI)
    :param parent_element: A parent element for this container. Defaults to None, or the
                           container if you've set that.
    :param object_id: An object ID for this element.
    :param anchors: Layout anchors in a dictionary.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    """

    def __init__(self,
                 relative_rect: pygame.Rect,
                 form: "UIForm",
                 name: str,
                 questionnaire: Mapping[str, Union[str, Mapping]],
                 manager: Optional[IUIManagerInterface] = None,
                 *,
                 starting_height: int = 1,
                 container: Optional[IContainerLikeInterface] = None,
                 parent_element: Optional[UIElement] = None,
                 object_id: Optional[Union[ObjectID, str]] = None,
                 anchors: Optional[Dict[str, Union[str, UIElement]]] = None,
                 visible: int = 1):
        super().__init__(relative_rect,
                         resize_left=False,
                         resize_right=False,
                         resize_top=False,
                         manager=manager,
                         starting_height=starting_height,
                         container=container,
                         parent_element=parent_element,
                         object_id=object_id,
                         anchors=anchors,
                         visible=visible)

        self._create_valid_ids(container=container,
                               parent_element=parent_element,
                               object_id=object_id,
                               element_id="section")

        self.form = form
        self.name = name

        self.background_colour = None
        self.border_colour = None
        self.background_image = None
        self.border_width = 1
        self.shadow_width = 2
        self.padding = (5, 5)

        self.label_height = 30
        self.section_label_height = 30
        self.field_height = 40
        self.large_field_height = 80
        self.gap = 10
        self.label_gap = 0
        self.section_gap = 15
        self.section_indent = 5

        self.shape = "rectangle"
        self.shape_corner_radius = 0

        anchors = {"left": "left", "right": "right", "top": "top"}

        # You can click this button to expand/hide the container
        self.main_expand_button = UIButton(pygame.Rect(0, 0, 0, 0),
                                           text=self.name + " ▼",
                                           manager=manager,
                                           container=self,
                                           parent_element=parent_element,
                                           object_id=ObjectID("#expand_section_button", None),
                                           anchors=anchors.copy())

        self.should_transition = False  # Should the section container switch from shown/hidden to the other state?

        anchors = {**anchors,
                   "top_target": self.main_expand_button}
        # Container for the rest of the section
        self.section_container = UIAutoResizingContainer(pygame.Rect(0, 0, self.relative_rect.width, 0),
                                                         # resize_left=False,
                                                         resize_right=False,
                                                         # resize_top=False,
                                                         # resize_bottom=True,
                                                         manager=manager,
                                                         container=self,
                                                         parent_element=parent_element,
                                                         object_id=ObjectID("#inner_section_container", None),
                                                         anchors=anchors.copy()
                                                         )
        self.questionnaire = questionnaire
        self.parsed_questionnaire = {}
        self.parse_section()

        self.rebuild_from_changed_theme_data()

    def parse_section(self) -> None:
        """
        This function is used to create the ui elements to gather input based on the questionnaire passed.
        See UIForm.validate_questionnaire for the structure of the questionnaire supported.

        :return: None
        """

        # Main Expand Button

        size = (self.relative_rect.width - 2 * self.padding[0], self.section_label_height)
        self.main_expand_button.set_dimensions(size)
        self.main_expand_button.set_relative_position((self.padding[0], 0))

        anchors = {"left": "left", "right": "right", "top": "top"}

        self.parsed_questionnaire = self.form.get_parsed_questionnaire(self, self.questionnaire,
                                                                       self.ui_manager, self.section_container,
                                                                       self, anchors)

    def update(self, time_delta: float) -> None:
        """
        Called every update loop of our UI Manager. Handles the actual transitioning of the section from shown to hidden
        and vice versa.

        :param time_delta: The time in seconds between this update method call and the previous one.
        :return: None
        """
        # Transition first, then resize so that the container size gets updates as soon as possible

        container = self.section_container
        if self.should_transition:
            if container.visible:
                # Hide the container and make the size 0 to avoid a giant void where the section used to be
                container.hide()
                container.set_dimensions((container.rect.width, 0))
                container.resize_bottom = False  # Prevent it from resizing itself
            else:
                # Show the container. It will resize automatically when its update gets called.
                container.show()
                container.resize_bottom = True
                container.should_update_dimensions = True

            self.should_transition = False

        super().update(time_delta)

    def rebuild_from_changed_theme_data(self) -> None:
        """
        Called by the UIManager to check the theming data and rebuild whatever needs rebuilding
        for this element when the theme data has changed.

        :return: None
        """
        super().rebuild_from_changed_theme_data()
        has_any_changed = False

        background_colour = self.ui_theme.get_colour_or_gradient("dark_bg",
                                                                 self.combined_element_ids)
        if background_colour != self.background_colour:
            self.background_colour = background_colour
            has_any_changed = True

        border_colour = self.ui_theme.get_colour_or_gradient("normal_border",
                                                             self.combined_element_ids)
        if border_colour != self.border_colour:
            self.border_colour = border_colour
            has_any_changed = True

        # misc
        if self._check_misc_theme_data_changed(attribute_name="shape",
                                               default_value="rectangle",
                                               casting_func=str,
                                               allowed_values=["rectangle",
                                                               "rounded_rectangle"]):
            has_any_changed = True

        if self._check_shape_theming_changed(defaults={"border_width": 1,
                                                       "shadow_width": 2,
                                                       "shape_corner_radius": 2}):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name="padding",
                                               default_value=(5, 5),
                                               casting_func=self.tuple_extract):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name="label_height",
                                               default_value=30,
                                               casting_func=int):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name="section_label_height",
                                               default_value=30,
                                               casting_func=int):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name="field_height",
                                               default_value=40,
                                               casting_func=int):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name="large_field_height",
                                               default_value=80,
                                               casting_func=int):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name="gap",
                                               default_value=10,
                                               casting_func=int):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name="label_gap",
                                               default_value=0,
                                               casting_func=int):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name="section_gap",
                                               default_value=15,
                                               casting_func=int):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name="section_indent",
                                               default_value=5,
                                               casting_func=int):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name="submit_button_horiz_alignment",
                                               default_value="right",
                                               casting_func=str,
                                               allowed_values=["left",
                                                               "center",
                                                               "right"]):
            has_any_changed = True

        if has_any_changed:
            self.rebuild()

    def rebuild(self) -> None:
        """
        A complete rebuild of the drawable shape used by this element.

        :return: None
        """

        super().rebuild()

        self.form.rebuild_parsed_questionnaire(self, self.parsed_questionnaire)

        size = (self.relative_rect.width - 2 * self.padding[0], self.section_label_height)
        self.main_expand_button.set_dimensions(size)
        self.main_expand_button.set_relative_position((self.padding[0], 0))

        theming_parameters = {"normal_bg": self.background_colour,
                              "normal_border": self.border_colour,
                              "normal_image": self.background_image,
                              "border_width": self.border_width,
                              "shadow_width": self.shadow_width,
                              "shape_corner_radius": self.shape_corner_radius}

        if self.shape == "rectangle":
            self.drawable_shape = RectDrawableShape(self.rect, theming_parameters,
                                                    ["normal"], self.ui_manager)
        elif self.shape == "rounded_rectangle":
            self.drawable_shape = RoundedRectangleShape(self.rect, theming_parameters,
                                                        ["normal"], self.ui_manager)

        self.on_fresh_drawable_shape_ready()

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Handles the expansion and contraction of the section

        :param event: The event to process
        :return: Whether the event was consumed
        """

        if event.type == UI_BUTTON_PRESSED and event.mouse_button == pygame.BUTTON_LEFT:
            if event.ui_element == self.main_expand_button:
                self.should_transition = True
        return False  # Should the section expansion/contraction events be consumed?


class UIForm(UIAutoScrollingContainer):
    """
    UIForm is used to create basic forms which can contain text fields, text boxes, dropdowns and more. The form can be
    divided in sections. A section can be expanded/contracted using a button. It also creates a submit button which will
    raise a UI_FORM_SUBMITTED event when clicked. The questions to the form should be parsed in the form of a
    dictionary.

    The questionnaire should be in the following format:

    questionnaire = {
        "section1": {"question1":"short_text", "question2":"boolean(default=False)", ...}, \n
        ..., \n
        "question3": UIDropDownMenu(...), \n
        ...
    }

    Where each key and value represent either:

    * A section's name and all questions within, or
    * A question's name and its corresponding type (see supported values below)

    Each section will create a sub-form for the questions within.

     Supported types (with the elements created automatically to gather input):

    * character (UITextEntryLine with 1 letter input)
    * short_text (normal UITextEntryLine input)
    * long_text (UITextEntryBox)
    * integer (UITextEntryLine with only numeric inputs allowed)
    * decimal (UITextEntryLine with numeric inputs and decimal point allowed)
    * boolean (UIDropDownMenu with True and False as the options. Default option is True)
    * boolean(default=False) (UIDropDownMenu with True and False as the options and the default option as *default*)
    The value of default must be either True or False. The types must be passed as a string only.
    Type values are **not** case-sensitive.

     Passing arguments for supported types:

    Each type can have arguments which follow syntax similar to normal functions as shown above with the boolean
    type. Currently, the only supported parameter is default. All string values should be passed in quotes, like:
    short_text(default="Hello World")

     You may provide an element instead of a pre-existing type. This element will be used for input.

    Supported elements:

    * UITextEntryLine
    * UITextEntryBox
    * UISelectionList
    * UIDropDownMenu

    Other elements (they must be instances of IUIElementInterface or its subclasses) may be passed in,
    if they implement either:

    * A get_current_input() function which takes no arguments and returns the currently input values; or
    * A current_input attribute or property which holds the currently input values

    If they do not implement any of the above, then this class will not handle its input, and you'll have to check
    for the input of the element once the form has been submitted

    :param relative_rect: The starting size and relative position of the form.
    :param questionnaire: The questionnaire is a mapping which contains the questions in the form in a specific format.
    :param manager: The UI manager for this element. If not provided or set to None,
                    it will try to use the first UIManager that was created by your application.
    :param starting_height: The starting layer height of this container above its container.
                            Defaults to 1.
    :param container: The container this container is within. Defaults to None (which is the root
                      container for the UI)
    :param parent_element: A parent element for this container. Defaults to None, or the
                           container if you've set that.
    :param object_id: An object ID for this element.
    :param anchors: Layout anchors in a dictionary.
    :param visible: Whether the element is visible by default. Warning - container visibility
                    may override this.
    """
    # TODO: Implement a show password button
    # TODO: Implement colour inputs
    SUPPORTED_TYPES = {"character": {"default": "'.'", "required": "True|False"},
                       "short_text": {"default": "'.*'", "required": "True|False"},
                       "long_text": {"default": "'.*'", "required": "True|False"},
                       "password": {"default": "'.*'", "required": "True|False"},
                       "integer": {"default": r"\d*", "required": "True|False"},
                       "decimal": {"default": r"[/d.]*", "required": "True|False"},
                       "boolean": {"default": "True|False", "required": "True|False"}
                       }

    def __init__(self,
                 relative_rect: pygame.Rect,
                 questionnaire: Optional[Mapping[str, Union[str, Mapping, IUIElementInterface]]] = None,
                 manager: Optional[IUIManagerInterface] = None,
                 *,
                 starting_height: int = 1,
                 container: Optional[IContainerLikeInterface] = None,
                 parent_element: Optional[UIElement] = None,
                 object_id: Optional[Union[ObjectID, str]] = None,
                 anchors: Optional[Dict[str, Union[str, UIElement]]] = None,
                 visible: int = 1):

        super().__init__(relative_rect,
                         allow_scroll_x=False,
                         manager=manager,
                         starting_height=starting_height,
                         container=container,
                         parent_element=parent_element,
                         object_id=object_id,
                         anchors=anchors,
                         visible=visible)

        self._create_valid_ids(container=container,
                               parent_element=parent_element,
                               object_id=object_id,
                               element_id="form")

        self.background_colour = None
        self.border_colour = None
        self.background_image = None
        self.border_width = 1
        self.shadow_width = 2
        self.padding = (5, 5)  # TODO: Implement vertical padding from the bottom

        self.label_height = 30
        self.field_height = 40
        self.large_field_height = 80
        self.gap = 10
        self.label_gap = 0
        self.section_gap = 15
        self.section_indent = 5

        self.shape = "rectangle"
        self.shape_corner_radius = 0

        self.submit_button_horiz_alignment = "right"

        self.questionnaire = questionnaire or {}  # If None is passed, use an empty dictionary instead
        self.parsed_questionnaire = {}

        self.submit_button = UIButton(pygame.Rect(0, 0, -1, self.field_height),
                                      text="Submit",
                                      manager=manager,
                                      container=self,
                                      parent_element=parent_element,
                                      object_id=ObjectID("#submit_button", None))

        self.parse_form()

        self.rebuild_from_changed_theme_data()
        self.vert_scroll_bar.rebuild()

    def _get_current_values(self, dic: Mapping[str, Union[IUIElementInterface, Mapping]]) -> Dict:
        """
        This function is used by get_current_values to recursively replace the nested dictionary's copy's keys with the
        values from the appropriate UIElements.

        :param dic: The nested dictionary
        :return: The copy of the nested mapping with values reflecting the values input by the user
        """
        value_dic = {}
        for key, value in dic.items():
            type_name = ""  # Used for re-casting str to boolean in Dropdowns created from the boolean type
            if isinstance(value, InputField):
                type_name = value.question_type
                value = value.element  # This is because it includes both the label and the actual element we want.

            if isinstance(value, UISection):
                value_dic[key] = self._get_current_values(value.parsed_questionnaire)

            elif isinstance(value, IUIElementInterface):

                if isinstance(value, UITextEntryLine):
                    value_dic[key] = value.get_text()

                elif isinstance(value, UITextEntryBox):
                    value_dic[key] = value.get_text()

                elif isinstance(value, UISelectionList):
                    if not value.allow_multi_select:
                        value_dic[key] = value.get_single_selection()
                    else:
                        value_dic[key] = value.get_multi_selection()

                elif isinstance(value, UIDropDownMenu):
                    selected_option = value.selected_option
                    if type_name == "boolean":
                        selected_option = literal_eval(selected_option)
                    value_dic[key] = selected_option

                elif hasattr(value, "get_current_input") and isinstance(value.get_current_input, Callable):
                    value_dic[key] = value.get_current_input()

                elif hasattr(value, "current_input"):
                    value_dic[key] = value.current_input

                else:
                    value_dic[key] = value

        return value_dic

    def get_current_values(self) -> Dict:
        """
        This function is used to get all the values from the input elements. If a UIElement is not supported, then the
        UIElement is returned instead

        :return: Dictionary with values reflecting the values input by the user
        """
        return self._get_current_values(self.parsed_questionnaire)

    @staticmethod
    def get_parsed_questionnaire(element: Union["UIForm", UISection], questionnaire: Mapping[str, Union[str, Mapping]],
                                 manager: IUIManagerInterface,
                                 container: IContainerLikeInterface, parent_element: UIElement,
                                 anchors: Dict[str, Union[str, UIElement]]) -> \
            Dict[str, Union[UISection, InputField, IUIElementInterface]]:
        """
        This function is used by UIForm.parse_questionnaire to recursively create the ui elements to gather input based
        on the questionnaire passed. This prevents duplication of code as UISection elements created also call this
        function

        :param element: The element the questionnaire belongs to. Used for theming
        :param questionnaire: The dict representing the questionnaire to parse
        :param manager: The UIManager which will handle the elements
        :param container: The container which should contain the elements
        :param parent_element: The parent element
        :param anchors: The starting anchors of the elements
        :return: The parsed questionnaire
        """
        parsed_questionnaire = {}

        form = element if isinstance(element, UIForm) else element.form
        label_height = element.label_height
        field_height = element.field_height
        large_field_height = element.large_field_height
        gap = element.gap
        label_gap = element.label_gap
        section_gap = element.section_gap
        section_indent = element.section_indent

        rel_rect = pygame.Rect(*element.padding,
                               element.relative_rect.width - 2 * element.padding[0],
                               field_height)

        for key, value in questionnaire.items():

            param_dict = {"relative_rect": rel_rect.copy(),
                          "manager": manager,
                          "container": container,
                          "parent_element": parent_element,
                          "anchors": anchors.copy()}

            if isinstance(value, Mapping):
                # Create Section

                param_dict["relative_rect"].width -= section_indent
                param_dict["relative_rect"].x += section_indent
                parsed_questionnaire[key] = UISection(form=form, name=key, questionnaire=value,
                                                      object_id=ObjectID(f"#{key.lower()}", None),
                                                      **param_dict)
                rel_rect.y = section_gap

            elif isinstance(value, str):
                # Parse supported types to appropriate UIElements. Could use a separate function for this in the future

                # Supported types (Pasted here for quick reference):
                # character (UITextEntryLine with 1 letter input)
                # short_text (normal UITextEntryLine input)
                # long_text (UITextEntryBox)
                # integer (UITextEntryLine with only numeric inputs allowed)
                # decimal (UITextEntryLine with numeric inputs and decimal point allowed)
                # boolean (UIDropDownMenu with True and False as the options. Default option is True)

                type_name, args = UIForm.type_checker(value)

                # Two elements are created, a label and the actual UIElement needed for input

                param_dict["relative_rect"].width = -1
                param_dict["relative_rect"].height = label_height

                # This is to prevent labels from resizing and becoming too small to hold their text
                right = param_dict["anchors"].pop("right", None)
                right_target = param_dict["anchors"].pop("right_target", None)

                label = UILabel(text=key, object_id=ObjectID(f"#{key.lower()}", "@form_label"), **param_dict)

                param_dict["anchors"]["top_target"] = label
                if right:
                    param_dict["anchors"]["right"] = right
                if right_target:
                    param_dict["anchors"]["right_target"] = right_target
                param_dict["relative_rect"] = rel_rect.copy()
                param_dict["relative_rect"].y = label_gap
                param_dict["relative_rect"].height = field_height
                param_dict["object_id"] = ObjectID(f"#{key.lower()}", "@form_field")

                element = None

                if type_name == "character":
                    element = UITextEntryLine(initial_text=args.get("default", ""), **param_dict)
                    element.set_text_length_limit(1)

                elif type_name == "short_text":
                    element = UITextEntryLine(initial_text=args.get("default", ""), **param_dict)

                elif type_name == "long_text":
                    param_dict["relative_rect"].height = large_field_height
                    element = UITextEntryBox(initial_text=args.get("default", ""), **param_dict)

                elif type_name == "password":
                    element = UITextEntryLine(initial_text=args.get("default", ""), **param_dict)
                    element.set_text_hidden(True)

                elif type_name == "integer":
                    element = UITextEntryLine(initial_text=args.get("default", ""), **param_dict)
                    element.set_allowed_characters("numbers")

                elif type_name == "decimal":
                    element = UITextEntryLine(initial_text=args.get("default", ""), **param_dict)
                    element.set_allowed_characters([".", *list("0123456789")])

                elif type_name == "boolean":
                    element = UIDropDownMenu(options_list=["True", "False"],
                                             starting_option=str(args.get("default", "True")),
                                             **param_dict)
                rel_rect.y = gap
                parsed_questionnaire[key] = InputField(type_name, label, element)
                anchors["top_target"] = element
                continue

            elif isinstance(value, IUIElementInterface):

                value.ui_container.remove_element(value)
                container = param_dict["container"].get_container()
                container.add_element(value)
                value.ui_container = container

                value.set_anchors(anchors)
                rect = rel_rect.copy()
                value.set_dimensions((rect.width, rect.height))
                value.set_relative_position(rect.topleft)

                rel_rect.y = gap
                parsed_questionnaire[key] = value

            anchors["top_target"] = parsed_questionnaire[key]

        return parsed_questionnaire

    def parse_form(self) -> None:
        """
        This function is used to create the ui elements to gather input based on the questionnaire passed. First the
        questionnaire is validated. See UIForm.validate_questionnaire for the structure of the questionnaire supported

        :return: None
        """

        self.validate_questionnaire(self.questionnaire, raise_error=True)

        anchors = {"left": "left", "right": "right", "top": "top", "right_target": self.vert_scroll_bar}

        self.parsed_questionnaire = self.get_parsed_questionnaire(self, self.questionnaire, self.ui_manager,
                                                                  self.scrollable_container, self, anchors)

        # Submit Button

        self.submit_button.anchors["top_target"] = anchors["top_target"]
        self.submit_button.relative_rect.y = self.gap
        self.rebuild_submit_button()

    def rebuild_from_changed_theme_data(self) -> None:
        """
        Called by the UIManager to check the theming data and rebuild whatever needs rebuilding
        for this element when the theme data has changed.

        :return: None
        """
        super().rebuild_from_changed_theme_data()
        has_any_changed = False

        background_colour = self.ui_theme.get_colour_or_gradient("dark_bg",
                                                                 self.combined_element_ids)
        if background_colour != self.background_colour:
            self.background_colour = background_colour
            has_any_changed = True

        border_colour = self.ui_theme.get_colour_or_gradient("normal_border",
                                                             self.combined_element_ids)
        if border_colour != self.border_colour:
            self.border_colour = border_colour
            has_any_changed = True

        # misc
        if self._check_misc_theme_data_changed(attribute_name="shape",
                                               default_value="rectangle",
                                               casting_func=str,
                                               allowed_values=["rectangle",
                                                               "rounded_rectangle"]):
            has_any_changed = True

        if self._check_shape_theming_changed(defaults={"border_width": 1,
                                                       "shadow_width": 2,
                                                       "shape_corner_radius": 2}):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name="padding",
                                               default_value=(5, 5),
                                               casting_func=self.tuple_extract):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name="label_height",
                                               default_value=30,
                                               casting_func=int):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name="field_height",
                                               default_value=40,
                                               casting_func=int):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name="large_field_height",
                                               default_value=80,
                                               casting_func=int):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name="gap",
                                               default_value=10,
                                               casting_func=int):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name="label_gap",
                                               default_value=0,
                                               casting_func=int):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name="section_gap",
                                               default_value=15,
                                               casting_func=int):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name="section_indent",
                                               default_value=5,
                                               casting_func=int):
            has_any_changed = True

        if self._check_misc_theme_data_changed(attribute_name="submit_button_horiz_alignment",
                                               default_value="right",
                                               casting_func=str,
                                               allowed_values=["left",
                                                               "center",
                                                               "right"]):
            has_any_changed = True

        if has_any_changed:
            self.rebuild()

    @staticmethod
    def rebuild_parsed_questionnaire(element: Union["UIForm", UISection],
                                     questionnaire: Mapping[str, Union[str, Mapping]]) -> None:

        """
        Called by UIForm.rebuild() to rebuild the elements of the form when theming elements like gaps between elements,
        indentation of the sections, etc. change.

        :param element: The element whose questionnaire to rebuild.
        :param questionnaire: The dict representing the parsed_questionnaire to rebuild
        :return: None
        """

        label_height = element.label_height
        field_height = element.field_height
        large_field_height = element.large_field_height
        gap = element.gap
        label_gap = element.label_gap
        section_gap = element.section_gap
        section_indent = element.section_indent

        relative_rect = pygame.Rect(*element.padding,
                                    element.relative_rect.width - 2 * element.padding[0],
                                    field_height)

        for key, value in questionnaire.items():

            rel_rect = relative_rect.copy()

            if isinstance(value, UISection):
                # Update Section

                rel_rect.width -= section_indent
                rel_rect.x += section_indent

                value.set_dimensions((rel_rect.width, rel_rect.height))
                value.set_relative_position(rel_rect.topleft)

                value.rebuild()
                relative_rect.y = section_gap

            elif isinstance(value, InputField):
                # Updated appropriate UIElements for supported types.
                # Could use a separate function for this in the future

                # Supported types (Pasted here for quick reference):
                # character (UITextEntryLine with 1 letter input)
                # short_text (normal UITextEntryLine input)
                # long_text (UITextEntryBox)
                # integer (UITextEntryLine with only numeric inputs allowed)
                # decimal (UITextEntryLine with numeric inputs and decimal point allowed)
                # boolean (UIDropDownMenu with True and False as the options. Default option is True)

                # Two elements are updated, a label and the actual UIElement needed for input

                label = value.label
                rel_rect.width = label.relative_rect.width
                rel_rect.height = label_height

                label.set_dimensions((rel_rect.width, rel_rect.height))
                label.set_relative_position(rel_rect.topleft)

                rel_rect = relative_rect.copy()
                rel_rect.y = label_gap
                rel_rect.height = field_height

                type_name = value.question_type
                element = value.element

                if type_name == "character":
                    element.set_text_length_limit(1)

                elif type_name == "long_text":
                    rel_rect.height = large_field_height

                elif type_name == "password":
                    element.set_text_hidden(True)

                elif type_name == "integer":
                    element.set_allowed_characters("numbers")

                elif type_name == "decimal":
                    element.set_allowed_characters([".", *list("0123456789")])

                element.set_dimensions((rel_rect.width, rel_rect.height))
                element.set_relative_position(rel_rect.topleft)

                relative_rect.y = gap

            elif isinstance(value, IUIElementInterface):

                value.set_dimensions((rel_rect.width, rel_rect.height))
                value.set_relative_position(rel_rect.topleft)

                relative_rect.y = gap

    def rebuild_submit_button(self) -> None:
        """
        Called by UIForm.rebuild() to rebuild the submit button based on its horizontal alignment

        :return: None
        """

        anchors = {"top": "top", "top_target": self.submit_button.anchors["top_target"]}
        x_padding = self.padding[0]
        pos = pygame.Vector2(0, self.submit_button.relative_rect.y)

        if self.submit_button_horiz_alignment == "left":
            anchors["left"] = "left"
            pos.x = x_padding
        elif self.submit_button_horiz_alignment == "center":
            anchors["centerx"] = "centerx"
        elif self.submit_button_horiz_alignment == "right":
            anchors["right"] = "right"
            anchors["right_target"] = self.vert_scroll_bar
            pos.x = -self.submit_button.rect.width - x_padding

        self.submit_button.set_anchors(anchors)
        self.submit_button.set_dimensions((self.submit_button.relative_rect.width, self.field_height))
        self.submit_button.set_relative_position(pos)

    def rebuild(self) -> None:
        """
        A complete rebuild of the drawable shape used by this element.

        :return: None
        """

        super().rebuild()

        root_rect = pygame.Rect(self.relative_rect.x + self.shadow_width + self.border_width,
                                self.relative_rect.y + self.shadow_width + self.border_width,
                                self.relative_rect.width - (2 * self.shadow_width) - (2 * self.border_width),
                                self.relative_rect.height - (2 * self.shadow_width) - (2 * self.border_width))

        if self._root_container.relative_rect != root_rect:
            self._root_container.set_relative_position(root_rect.topleft)
            self._root_container.set_dimensions(root_rect.size)

        self.rebuild_parsed_questionnaire(self, self.parsed_questionnaire)
        self.rebuild_submit_button()

        theming_parameters = {"normal_bg": self.background_colour,
                              "normal_border": self.border_colour,
                              "normal_image": self.background_image,
                              "border_width": self.border_width,
                              "shadow_width": self.shadow_width,
                              "shape_corner_radius": self.shape_corner_radius}

        if self.shape == "rectangle":
            self.drawable_shape = RectDrawableShape(self.rect, theming_parameters,
                                                    ["normal"], self.ui_manager)
        elif self.shape == "rounded_rectangle":
            self.drawable_shape = RoundedRectangleShape(self.rect, theming_parameters,
                                                        ["normal"], self.ui_manager)

        self.on_fresh_drawable_shape_ready()

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Handles the submission of the form

        :param event: The event to process
        :return: Whether the event was consumed
        """

        consumed = False
        if event.type == UI_BUTTON_PRESSED and event.mouse_button == pygame.BUTTON_LEFT:
            if event.ui_element == self.submit_button:
                form_values = self.get_current_values()


                # new event
                event_data = {"form_values": form_values,
                              "ui_element": self,
                              "ui_object_id": self.most_specific_combined_id}
                pygame.event.post(pygame.event.Event(UI_FORM_SUBMITTED, event_data))

                consumed = True

        return consumed

    @staticmethod
    def type_checker(string) -> Tuple[str, Dict[str, Any]]:
        """
        This is used to check whether a string can be used in a questionnaire to represent a type. Raises an appropriate
        exception (either a NameError, SyntaxError or ValueError) if the string is not valid. Supported types are:

        * character (UITextEntryLine with 1 letter input)
        * short_text (normal UITextEntryLine input)
        * long_text (UITextEntryBox)
        * password (UITextEntryLine input with characters hidden)
        * integer (UITextEntryLine with only numeric inputs allowed)
        * decimal (UITextEntryLine with numeric inputs and decimal point allowed)
        * boolean (UIDropDownMenu with True and False as the options. Default option is True)

        :param string: The string to check
        :return: A tuple of the type name with a list of argument-value tuples if the string is valid
        """

        # Type with their args and supported values for args
        supported_types = UIForm.SUPPORTED_TYPES

        type_check = re.compile(f"(?P<type_name>{'|'.join(supported_types)})(?:\\((?P<type_args>.*)\\))?",
                                re.IGNORECASE)
        type_name_match = type_check.fullmatch(string)
        if not type_name_match:
            raise ValueError(f"Question type '{string}' is not supported")

        if string.endswith("()"):
            raise SyntaxError(f"No parameters passed for question")

        type_name = type_name_match.group("type_name").lower()
        params = supported_types[type_name]
        arg_group = type_name_match.group("type_args")

        if not arg_group:
            return type_name, {}

        # Split the arguments passed based on commas. This is actually a more complicated process than you'd expect,
        # because some commas might be contained in quotes. But we can't just check that the number of ' and " quotes
        # are both even on each side because some ' might be contained within "" (for example in use of apostrophes) and
        # some " might be contained within ''.

        args = []
        in_quotes = False
        quotes_type = None
        arg_start_i = 0
        keyword_present = False
        keyword = None
        arg_value_start_i = 0

        if arg_group[-1] != ",":
            # This is needed to ensure last argument passed is added to the args list
            arg_group += ","

        for i, char in enumerate(arg_group):

            if not in_quotes:

                if char == "=":
                    if i == 0:
                        raise SyntaxError("Found '=' at the beginning of arguments")
                    if keyword_present:
                        # Found 2 "=" symbols in the same argument: incorrect syntax
                        raise SyntaxError(f"Found 2 '=' symbols after keyword argument '{keyword}'")
                    else:
                        keyword_present = True
                        keyword_end_i = i - 1
                        arg_value_start_i = i + 1
                        keyword = arg_group[arg_start_i: keyword_end_i + 1].strip()

                elif char == ",":
                    if arg_start_i == i:
                        # Either comma found at the beginning of arguments or two commas found consecutively
                        if i == 0:
                            raise SyntaxError("Found comma at the beginning of arguments")
                        else:
                            raise SyntaxError("Found 2 consecutive commas")
                    elif keyword_present and arg_value_start_i == i:
                        # No value passed after = sign
                        raise SyntaxError(f"No value passed for keyword argument '{keyword}'")

                    value = arg_group[arg_value_start_i: i].strip()
                    try:
                        value = literal_eval(value)
                    except (ValueError, SyntaxError):
                        # Literal_eval couldn't pass it as a str, int, bool etc.
                        raise NameError(f"'{value}' is not defined. Perhaps quotes were missed")

                    args.append((keyword, value))
                    arg_start_i = i + 1
                    keyword_present = False
                    keyword = None
                    arg_value_start_i = i + 1

                elif char == "'":
                    in_quotes = True
                    quotes_type = "'"

                elif char == '"':
                    in_quotes = True
                    quotes_type = '"'

            elif char == quotes_type:
                in_quotes = False
                quotes_type = None

            elif i == len(arg_group) - 1:
                # Last quotes symbol was unmatched
                raise SyntaxError(f"Found unmatched {quotes_type}")

        # Length of arguments supplied should be smaller than total params
        if len(args) > len(params):
            raise ValueError(f"Question of type '{type_name}' take at most {len(params)} arguments"
                             f" but {len(args)} arguments were passed")

        # Check that positional arguments don't follow keyword arguments
        if any(args[i][0] and not args[i + 1][0] for i in range(len(args) - 1)):
            raise SyntaxError("Found positional argument after keyword argument")

        names_checked = []
        # Evaluate whether each argument is valid
        for i, (name, value) in enumerate(args):
            if not name:
                name = tuple(params)[i]
                args[i] = name, args[i][1]
            if name not in params:
                raise ValueError(f"Unknown parameter '{name}' for question type '{type_name}'")
            if name in names_checked:
                raise SyntaxError(f"Got multiple values for parameter '{name}'")
            if isinstance(value, str):
                value = f"'{value}'"
            if not re.fullmatch(params[name], str(value)):
                raise ValueError(f"Invalid value '{value}' for argument '{name}'")

        return type_name, dict(args)

    @staticmethod
    def validate_questionnaire(questionnaire: Mapping[str, Union[str, Mapping]],
                               raise_error: bool = False) -> Optional[bool]:
        """
        Use this to validate if a questionnaire can be passed to the __init__ function. The format of the questionnaire
        is given in the main documentation of the class.

        :param questionnaire: A dictionary containing the details of the questionnaire in the appropriate format
        :param raise_error: Should an error be raised with appropriate message? Default is False
        :return: True or False
        """

        if not isinstance(questionnaire, Mapping):
            if raise_error:
                raise TypeError(f"Expected type 'Mapping' (Dict) for questionnaire, found type '{type(questionnaire)}'")
            else:
                return False

        for key, value in questionnaire.items():
            if not isinstance(key, str):
                if raise_error:
                    raise TypeError(f"Expected type 'str' for key in questionnaire, found type '{type(key)}'")
                else:
                    return False

            # Sub-questionnaire
            if isinstance(value, Mapping):
                if not UIForm.validate_questionnaire(value, raise_error):
                    return False

            # Value is one of the supported types, check for validity
            elif isinstance(value, str):
                if raise_error:
                    UIForm.type_checker(value)
                else:
                    try:
                        UIForm.type_checker(value)
                    except (NameError, SyntaxError, ValueError):
                        return False

            elif isinstance(value, IUIElementInterface):
                continue

            # Value not present
            elif not value:
                if raise_error:
                    raise ValueError(f"Question type cannot be {value}")
                else:
                    return False

            # Type of Value is not supported
            else:
                if raise_error:
                    raise ValueError(f"Questions of type {type(value)} are not supported")
                else:
                    return False

        return True
