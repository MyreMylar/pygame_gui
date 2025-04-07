import warnings

from typing import List, Union, Tuple, Dict, Any, Callable, Set, Optional
from typing import TYPE_CHECKING

import pygame

from pygame_gui.core.gui_type_hints import Coordinate, RectLike
from pygame_gui.core.interfaces import IUIElementInterface, IUITooltipInterface
from pygame_gui.core.interfaces import (
    IContainerLikeInterface,
    IUIManagerInterface,
    IContainerAndContainerLike,
    IUIAppearanceThemeInterface,
)
from pygame_gui.core.utility import render_white_text_alpha_black_bg
from pygame_gui.core.utility import basic_blit
from pygame_gui.core.layered_gui_group import GUISprite
from pygame_gui.core.utility import get_default_manager
from pygame_gui.core.object_id import ObjectID

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from pygame_gui.core.drawable_shapes.drawable_shape import DrawableShape


class UIElement(GUISprite, IUIElementInterface):
    """
    A base class for UI elements. You shouldn't create UI Element objects, instead all UI Element
    classes should derive from this class. Inherits from pygame.sprite.Sprite.

    :param relative_rect: A rectangle shape of the UI element, the position is relative to the
                          element's container.
    :param manager: The UIManager that manages this UIElement.
    :param container: A container that this element is contained in.
    :param starting_height: Used to record how many layers above its container this element
                            should be. Normally 1.
    :param layer_thickness: Used to record how 'thick' this element is in layers. Normally 1.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.
    :param visible: Whether the element is visible by default. Warning - container visibility may
                    override this.
    :param parent_element: Element that this element 'belongs to' in theming. Elements inherit
                    colours from parents.
    :param object_id: An optional set of IDs to help distinguish this element from other elements.
    :param element_id: A list of string ID representing this element's class.
    """

    def __init__(
        self,
        relative_rect: RectLike,
        manager: Optional[IUIManagerInterface],
        container: Optional[IContainerLikeInterface],
        *,
        starting_height: int,
        layer_thickness: int,
        anchors: Optional[Dict[str, Union[str, IUIElementInterface]]] = None,
        visible: int = 1,
        parent_element: Optional[IUIElementInterface] = None,
        object_id: Union[ObjectID, str, None] = None,
        element_id: Optional[List[str]] = None,
        ignore_shadow_for_initial_size_and_pos: bool = False,
    ):
        self._layer = 0

        self.ui_container: Optional[IContainerAndContainerLike] = None
        self.parent_element = parent_element
        if manager is None:
            manager = get_default_manager()
        if manager is None:
            raise ValueError(
                "Need to create at least one UIManager to create UIElements"
            )

        self.ui_manager: IUIManagerInterface = manager

        super().__init__(self.ui_manager.get_sprite_group())

        self.ui_group = self.ui_manager.get_sprite_group()
        self._ui_theme = self.ui_manager.get_theme()

        self.minimum_dimensions = (-1, -1)

        self.object_ids: List[str | None] = []
        self.class_ids: List[str | None] = []
        self.element_ids: List[str] = []
        self.element_base_ids: List[str | None] = []
        self.combined_element_ids: List[str] = []
        self.most_specific_combined_id = "no_id"

        # Themed parameters
        self.shadow_width: int = 2
        self.border_width: int = 1
        self.border_overlap: Optional[int] = None
        self.shape_corner_radius: List[int] = [0, 0, 0, 0]

        self.tool_tip_text: Optional[str] = None
        self.tool_tip_text_kwargs: Dict[str, str] = {}
        self.tool_tip_object_id: Optional[ObjectID] = None
        self.tool_tip_delay = 1.0
        self.tool_tip_wrap_width: Optional[int] = None
        self.tool_tip: Optional[IUITooltipInterface] = None

        self.layer_thickness = layer_thickness
        self.starting_height = starting_height
        self.drawable_shape: Optional[DrawableShape] = None

        self.is_enabled = True

        self._setup_container(container)

        element_ids = element_id
        inner_element_id: Optional[str] = None
        inner_base_id: Optional[str] = None
        if element_ids is not None:
            if len(element_ids) >= 1:
                inner_element_id = element_ids[0]

            if len(element_ids) >= 2:
                inner_base_id = element_ids[1]

            if inner_element_id is not None:
                self._create_valid_ids(
                    container=container,
                    parent_element=parent_element,
                    object_id=object_id,
                    element_id=inner_element_id,
                    element_base_id=inner_base_id,
                )

        if isinstance(relative_rect, (pygame.Rect, pygame.FRect)):
            self.relative_rect = relative_rect.copy()
        else:
            self.relative_rect = pygame.Rect(relative_rect)

        if ignore_shadow_for_initial_size_and_pos:
            # need to expand our rect by the shadow size and adjust position by it as well.
            self._check_shape_theming_changed(
                defaults={
                    "border_width": 1,
                    "shadow_width": 2,
                    "border_overlap": 1,
                    "shape_corner_radius": [2, 2, 2, 2],
                }
            )

            self.relative_rect.width += self.shadow_width * 2
            self.relative_rect.height += self.shadow_width * 2
            self.relative_rect.top -= (
                self.shadow_width
            )  # will need to be changed when we can adjust the anchor source
            self.relative_rect.left -= (
                self.shadow_width
            )  # will need to be changed when we can adjust the anchor source

        self.relative_rect.size = self._get_clamped_to_minimum_dimensions(
            self.relative_rect.size
        )
        self.rect = self.relative_rect.copy()

        self.dynamic_width = self.relative_rect.width == -1
        self.dynamic_height = self.relative_rect.height == -1

        self.anchors: Optional[Dict[str, Union[str, IUIElementInterface]]] = {}
        self.set_anchors(anchors)

        self.image = None

        self.visible = bool(visible)
        self.blendmode = pygame.BLEND_PREMULTIPLIED

        self.relative_bottom_margin = None
        self.relative_right_margin = None

        self._hovered = False
        self._is_focused = False
        self.hover_time = 0.0

        self.pre_debug_image: Optional[pygame.Surface] = None
        self._pre_clipped_image: Optional[pygame.Surface] = None

        self._image_clip: Optional[pygame.Rect] = None

        self._visual_debug_mode = False

        self.dirty = 1
        self._setup_visibility(visible)

        self._update_absolute_rect_position_from_anchors()

        self._update_container_clip()

        self._focus_set: Optional[set[IUIElementInterface]] = {self}
        self.is_window = False

    @property
    def ui_theme(self) -> IUIAppearanceThemeInterface:
        return self._ui_theme

    @ui_theme.setter
    def ui_theme(self, value: IUIAppearanceThemeInterface):
        self._ui_theme = value

    @property
    def is_focused(self) -> bool:
        return self._is_focused

    @is_focused.setter
    def is_focused(self, value: bool):
        self._is_focused = value

    @property
    def hovered(self) -> bool:
        return self._hovered

    @hovered.setter
    def hovered(self, value: bool):
        self._hovered = value

    def _get_clamped_to_minimum_dimensions(self, dimensions, clamp_to_container=False):
        if self.ui_container is not None and clamp_to_container:
            dimensions = (
                min(
                    self.ui_container.get_container().get_rect().width,
                    max(self.minimum_dimensions[0], int(dimensions[0])),
                ),
                min(
                    self.ui_container.get_container().get_rect().height,
                    max(self.minimum_dimensions[1], int(dimensions[1])),
                ),
            )
        else:
            dimensions = (
                max(self.minimum_dimensions[0], int(dimensions[0])),
                max(self.minimum_dimensions[1], int(dimensions[1])),
            )
        return dimensions

    def _on_contents_changed(self):
        if self.dynamic_width or self.dynamic_height:
            self._calc_dynamic_size()

    def _calc_dynamic_size(self):
        pass

    def _set_dynamic_width(self, is_dynamic: bool = True):
        self.dynamic_width = is_dynamic
        if self.drawable_shape is not None:
            self.drawable_shape.dynamic_width = is_dynamic

    def _set_dynamic_height(self, is_dynamic: bool = True):
        self.dynamic_height = is_dynamic
        if self.drawable_shape is not None:
            self.drawable_shape.dynamic_height = is_dynamic

    @staticmethod
    def _validate_horizontal_anchors(
        anchors: Dict[str, Union[str, IUIElementInterface]],
    ):
        # first make a dictionary of just the horizontal anchors
        horizontal_anchors = {}

        if "left" in anchors:
            horizontal_anchors["left"] = anchors["left"]
        if "right" in anchors:
            horizontal_anchors["right"] = anchors["right"]
        if "centerx" in anchors:
            horizontal_anchors["centerx"] = anchors["centerx"]

        valid_anchor_set = [
            {"left": "left", "right": "left"},
            {"left": "right", "right": "right"},
            {"left": "left", "right": "right"},
            {"left": "left"},
            {"right": "right"},
            {"left": "right"},
            {"right": "left"},
            {"centerx": "centerx"},
        ]

        if horizontal_anchors in valid_anchor_set:
            return True
        elif not horizontal_anchors:
            return False  # no horizontal anchors so just use defaults
        else:
            warnings.warn(
                "Supplied horizontal anchors are invalid, defaulting to left",
                category=UserWarning,
            )
            return False

    @staticmethod
    def _validate_vertical_anchors(anchors: Dict[str, Union[str, IUIElementInterface]]):
        # first make a dictionary of just the vertical anchors
        vertical_anchors = {}

        if "top" in anchors:
            vertical_anchors["top"] = anchors["top"]
        if "bottom" in anchors:
            vertical_anchors["bottom"] = anchors["bottom"]
        if "centery" in anchors:
            vertical_anchors["centery"] = anchors["centery"]

        valid_anchor_set = [
            {"top": "top", "bottom": "top"},
            {"top": "bottom", "bottom": "bottom"},
            {"top": "top", "bottom": "bottom"},
            {"top": "top"},
            {"bottom": "bottom"},
            {"top": "bottom"},
            {"bottom": "top"},
            {"centery": "centery"},
        ]

        if vertical_anchors in valid_anchor_set:
            return True
        elif not vertical_anchors:
            return False  # no vertical anchors so just use defaults
        else:
            warnings.warn(
                "Supplied vertical anchors are invalid, defaulting to top",
                category=UserWarning,
            )
            return False

    def _setup_visibility(self, visible):
        if visible:
            self.visible = True

        if (
            self.ui_container is not None
            and not self.ui_container.get_container().visible
        ):
            self.visible = False

    def set_container(self, container: Union[None, IContainerLikeInterface]):
        """
        Switch the element to new container.
        Remove the element from the old container and add it to the new container.

        :param container: The new container to add.

        """
        if isinstance(self.ui_container, IContainerLikeInterface):
            self.ui_container.get_container().remove_element(self)

        self._setup_container(container)
        self._update_absolute_rect_position_from_anchors()
        self.rebuild_from_changed_theme_data()

    def _setup_container(self, container_like: Optional[IContainerLikeInterface]):
        new_container: Optional[IContainerAndContainerLike] = None
        if container_like is None:
            if self.ui_manager is not None:
                # no container passed in so make it the root container
                if self.ui_manager.get_root_container() is not None:
                    new_container = self.ui_manager.get_root_container()
                elif isinstance(self, IContainerAndContainerLike):
                    new_container = self
        elif not isinstance(container_like, IContainerLikeInterface):
            # oops, passed in something that wasn't like a container so bail
            raise ValueError(
                "container_like parameter must be of type IContainerLikeInterface."
            )
        elif isinstance(container_like, IContainerLikeInterface):
            new_container = container_like.get_container()

        # by this point new_container should be a valid IContainerAndContainerLike
        if new_container is not None:
            self.ui_container = new_container
            if self.ui_container is not self:
                self.ui_container.add_element(self)

    def get_focus_set(self) -> Optional[Set[IUIElementInterface]]:
        return self._focus_set

    def set_focus_set(self, focus_set: Optional[Set[IUIElementInterface]]):
        if self.ui_manager is not None:
            if self.ui_manager.get_focus_set() is self._focus_set:
                self.ui_manager.set_focus_set(focus_set)
            self._focus_set = focus_set

    def join_focus_sets(self, element: IUIElementInterface):
        set_to_join = element.get_focus_set()
        if self._focus_set is not None and set_to_join is not None:
            union_of_sets = set(self._focus_set | set_to_join)
            for item in union_of_sets:
                item.set_focus_set(union_of_sets)

    def remove_element_from_focus_set(self, element):
        if self._focus_set is not None:
            self._focus_set.discard(element)

    def get_relative_rect(self) -> pygame.Rect | pygame.FRect:
        """
        The relative positioning rect.

        :return: A pygame rect.

        """
        return self.relative_rect

    def get_abs_rect(self) -> pygame.Rect | pygame.FRect:
        """
        The absolute positioning rect.

        :return: A pygame rect.

        """
        return self.rect

    def get_element_base_ids(self) -> List[str | None]:
        """
        A list of all the element base IDs in this element's theming/event hierarchy.

        :return: a list of strings, one for each element in the hierarchy.
        """
        return self.element_base_ids

    def get_element_ids(self) -> List[str]:
        """
        A list of all the element IDs in this element's theming/event hierarchy.

        :return: a list of strings, one for each element in the hierarchy.
        """
        return self.element_ids

    def get_class_ids(self) -> List[str | None]:
        """
        A list of all the class IDs in this element's theming/event hierarchy.

        :return: a list of strings, one for each element in the hierarchy.
        """
        return self.class_ids

    def get_object_ids(self) -> List[str | None]:
        """
        A list of all the object IDs in this element's theming/event hierarchy.

        :return: a list of strings, one for each element in the hierarchy.
        """
        return self.object_ids

    def get_anchors(self) -> Optional[Dict[str, Union[str, IUIElementInterface]]]:
        """
        A dictionary containing all the anchors defining what the relative rect is relative to

        :return: A dictionary containing all the anchors defining what the relative rect is relative to
        """
        return self.anchors

    def set_anchors(
        self, anchors: Optional[Dict[str, Union[str, IUIElementInterface]]]
    ) -> None:
        """
        Wraps the setting of the anchors with some validation

        :param anchors: A dictionary of anchors defining what the relative rect is relative to
        :return: None
        """
        old_anchors = None
        if self.anchors is not None:
            old_anchors = self.anchors.copy()

        self.anchors = {}

        if anchors is not None:
            if "center" in anchors and anchors["center"] == "center":
                self.anchors["center"] = "center"
            else:
                if self._validate_horizontal_anchors(anchors):
                    self._set_three_anchors(anchors, "left", "right", "centerx")
                else:
                    self.anchors["left"] = "left"

                if self._validate_vertical_anchors(anchors):
                    self._set_three_anchors(anchors, "top", "bottom", "centery")
                else:
                    self.anchors["top"] = "top"

            self._set_three_anchors(
                anchors, "left_target", "right_target", "top_target"
            )
            self._set_three_anchors(
                anchors, "bottom_target", "centerx_target", "centery_target"
            )
        else:
            self.anchors = {"left": "left", "top": "top"}

        if self.anchors != old_anchors and self.ui_container is not None:
            self.ui_container.get_container().on_contained_elements_changed(self)

    def _set_three_anchors(self, anchors, anchor_1_name, anchor_2_name, anchor_3_name):
        if anchor_1_name in anchors:
            self.anchors[anchor_1_name] = anchors[anchor_1_name]
        if anchor_2_name in anchors:
            self.anchors[anchor_2_name] = anchors[anchor_2_name]
        if anchor_3_name in anchors:
            self.anchors[anchor_3_name] = anchors[anchor_3_name]

    def _create_valid_ids(
        self,
        container: Optional[IContainerLikeInterface],
        parent_element: Optional[IUIElementInterface],
        object_id: Optional[ObjectID | str],
        element_id: str,
        element_base_id: Optional[str] = None,
    ):
        """
        Creates valid id lists for an element. It will assert if users supply object IDs that
        won't work such as those containing full stops. These ID lists are used by the theming
        system to identify what theming parameters to apply to which element.

        :param container: The container for this element. If parent is None the container will be
                          used as the parent.
        :param parent_element: Element that this element 'belongs to' in theming. Elements inherit
                               colours from parents.
        :param object_id: An optional set of IDs to help distinguish this element
                         from other elements.
        :param element_id: A string ID representing this element's class.

        """
        id_parent: Optional[IContainerAndContainerLike | IUIElementInterface] = None
        if parent_element is not None:
            id_parent = parent_element
        elif (
            container is not None
            and isinstance(container, IUIElementInterface)
            and self.ui_manager is not None
            and container is not self.ui_manager.get_root_container()
        ):
            id_parent = container

        if isinstance(object_id, str):
            if object_id is not None and ("." in object_id or " " in object_id):
                raise ValueError(
                    f"Object ID cannot contain fullstops or spaces: {str(object_id)}"
                )
            obj_id = object_id
            class_id = None
        elif isinstance(object_id, ObjectID):
            obj_id = object_id.object_id
            class_id = object_id.class_id
        else:
            obj_id = None
            class_id = None

        if id_parent is not None:
            self.element_base_ids = id_parent.get_element_base_ids().copy()
            self.element_ids = id_parent.get_element_ids().copy()
            self.class_ids = id_parent.get_class_ids().copy()
            self.object_ids = id_parent.get_object_ids().copy()

            self.element_base_ids.append(element_base_id)
            self.element_ids.append(element_id)
            self.class_ids.append(class_id)
            self.object_ids.append(obj_id)
        else:
            self.element_base_ids = [element_base_id]
            self.element_ids = [element_id]
            self.class_ids = [class_id]
            self.object_ids = [obj_id]

        self.combined_element_ids = self.ui_manager.get_theme().build_all_combined_ids(
            self.element_base_ids, self.element_ids, self.class_ids, self.object_ids
        )

        self.most_specific_combined_id = self.combined_element_ids[0]

    def change_object_id(self, new_object_id: Union[ObjectID, str, None]):
        """
        Allows for easy switching of an element's ObjectID used for theming and events.

        Will rebuild the element after switching the ID

        :param new_object_id: The new ID to use for this element.
        :return:
        """
        self._create_valid_ids(
            container=self.ui_container,
            parent_element=self.parent_element,
            object_id=new_object_id,
            element_id=self.element_ids[-1],
            element_base_id=self.element_base_ids[-1],
        )

        self.rebuild_from_changed_theme_data()

    @staticmethod
    def _calc_top_offset(
        container: IContainerLikeInterface,
        anchors: Dict[str, Union[str, IUIElementInterface]],
    ) -> int:
        return int(
            anchors["top_target"].get_abs_rect().bottom
            if (
                "top_target" in anchors
                and isinstance(anchors["top_target"], IUIElementInterface)
            )
            else container.get_container().get_abs_rect().top
        )

    @staticmethod
    def _calc_bottom_offset(
        container: IContainerLikeInterface,
        anchors: Dict[str, Union[str, IUIElementInterface]],
    ) -> int:
        return int(
            anchors["bottom_target"].get_abs_rect().top
            if (
                "bottom_target" in anchors
                and isinstance(anchors["bottom_target"], IUIElementInterface)
            )
            else container.get_container().get_abs_rect().bottom
        )

    @staticmethod
    def _calc_centery_offset(
        container: IContainerLikeInterface,
        anchors: Dict[str, Union[str, IUIElementInterface]],
    ) -> int:
        return int(
            anchors["centery_target"].get_abs_rect().centery
            if (
                "centery_target" in anchors
                and isinstance(anchors["centery_target"], IUIElementInterface)
            )
            else container.get_container().get_abs_rect().centery
        )

    @staticmethod
    def _calc_left_offset(
        container: IContainerLikeInterface,
        anchors: Dict[str, Union[str, IUIElementInterface]],
    ) -> int:
        return int(
            anchors["left_target"].get_abs_rect().right
            if (
                "left_target" in anchors
                and isinstance(anchors["left_target"], IUIElementInterface)
            )
            else container.get_container().get_abs_rect().left
        )

    @staticmethod
    def _calc_right_offset(
        container: IContainerLikeInterface,
        anchors: Dict[str, Union[str, IUIElementInterface]],
    ) -> int:
        return int(
            anchors["right_target"].get_abs_rect().left
            if (
                "right_target" in anchors
                and isinstance(anchors["right_target"], IUIElementInterface)
            )
            else container.get_container().get_abs_rect().right
        )

    @staticmethod
    def _calc_centerx_offset(
        container: IContainerLikeInterface,
        anchors: Dict[str, Union[str, IUIElementInterface]],
    ) -> int:
        return int(
            anchors["centerx_target"].get_abs_rect().centerx
            if (
                "centerx_target" in anchors
                and isinstance(anchors["centerx_target"], IUIElementInterface)
            )
            else container.get_container().get_abs_rect().centerx
        )

    @staticmethod
    def _calc_abs_rect_pos_from_rel_rect(
        relative_rect: pygame.Rect,
        container: IContainerLikeInterface,
        anchors: Dict[str, Union[str, IUIElementInterface]],
        relative_right_margin: Optional[int] = None,
        relative_bottom_margin: Optional[int] = None,
        dynamic_width: bool = False,
        dynamic_height: bool = False,
    ) -> Tuple[pygame.Rect, Optional[int], Optional[int]]:
        """
        Use this function to get the absolute rect position, given the relative rect, container and the anchors.
        All values are assumed to be valid.

        :param relative_rect: A Rect relative to the container/anchors
        :param container: Defines the container of the rect
        :param anchors: Defines what the Rect is relative to
        :param relative_right_margin: The margin from the right. If not given or None, then it will be calculated
        :param relative_bottom_margin: The margin from the bottom. If not given or None, then it will be calculated
        :param dynamic_width: If the width of the rect is dynamic or not.
                              If not width will be clamped to minimum of 0.
        :param dynamic_height: If the height of the rect is dynamic or not.
                               If not height will be clamped to minimum of 0.
        :return: A tuple containing a Rect representing the absolute position of the rect from the screen, and the
        relative right and bottom margins
        """
        new_top = 0
        new_bottom = 0
        top_offset = UIElement._calc_top_offset(container, anchors)
        bottom_offset = UIElement._calc_bottom_offset(container, anchors)
        center_x_and_y = "center" in anchors and anchors["center"] == "center"
        if ("centery" in anchors and anchors["centery"] == "centery") or center_x_and_y:
            centery_offset = UIElement._calc_centery_offset(container, anchors)
            new_top = relative_rect.top - relative_rect.height // 2 + centery_offset
            new_bottom = (
                relative_rect.bottom - relative_rect.height // 2 + centery_offset
            )

        if "top" in anchors:
            if anchors["top"] == "top":
                new_top = relative_rect.top + top_offset
                new_bottom = relative_rect.bottom + top_offset
            elif anchors["top"] == "bottom":
                new_top = relative_rect.top + bottom_offset

                if relative_bottom_margin is None:
                    relative_bottom_margin = bottom_offset - (
                        new_top + relative_rect.height
                    )
                new_bottom = bottom_offset - relative_bottom_margin

        if "bottom" in anchors:
            if anchors["bottom"] == "top":
                new_top = relative_rect.top + top_offset
                new_bottom = relative_rect.bottom + top_offset
            elif anchors["bottom"] == "bottom":
                if "top" not in anchors or anchors["top"] != "top":
                    new_top = relative_rect.top + bottom_offset

                if relative_bottom_margin is None:
                    relative_bottom_margin = bottom_offset - (
                        new_top + relative_rect.height
                    )
                new_bottom = bottom_offset - relative_bottom_margin

        new_left = 0
        new_right = 0
        left_offset = UIElement._calc_left_offset(container, anchors)
        right_offset = UIElement._calc_right_offset(container, anchors)

        if ("centerx" in anchors and anchors["centerx"] == "centerx") or center_x_and_y:
            centerx_offset = UIElement._calc_centerx_offset(container, anchors)
            new_left = relative_rect.left - relative_rect.width // 2 + centerx_offset
            new_right = relative_rect.right - relative_rect.width // 2 + centerx_offset

        if "left" in anchors:
            if anchors["left"] == "left":
                new_left = relative_rect.left + left_offset
                new_right = relative_rect.right + left_offset
            elif anchors["left"] == "right":
                new_left = relative_rect.left + right_offset

                if relative_right_margin is None:
                    relative_right_margin = right_offset - (
                        new_left + relative_rect.width
                    )
                new_right = right_offset - relative_right_margin

        if "right" in anchors:
            if anchors["right"] == "left":
                new_left = relative_rect.left + left_offset
                new_right = relative_rect.right + left_offset
            elif anchors["right"] == "right":
                if "left" not in anchors or anchors["left"] != "left":
                    new_left = relative_rect.left + right_offset

                if relative_right_margin is None:
                    relative_right_margin = right_offset - (
                        new_left + relative_rect.width
                    )
                new_right = right_offset - relative_right_margin

        if dynamic_height:
            new_height = new_bottom - new_top
        else:
            new_height = max(0, new_bottom - new_top)

        if dynamic_width:
            new_width = new_right - new_left
        else:
            new_width = max(0, new_right - new_left)

        rect = pygame.Rect(new_left, new_top, new_width, new_height)
        return rect, relative_right_margin, relative_bottom_margin

    def _update_absolute_rect_position_from_anchors(self, recalculate_margins=False):
        """
        Called when our element's relative position has changed.
        """
        relative_right_margin = (
            None if recalculate_margins else self.relative_right_margin
        )
        relative_bottom_margin = (
            None if recalculate_margins else self.relative_bottom_margin
        )

        rect, self.relative_right_margin, self.relative_bottom_margin = (
            self._calc_abs_rect_pos_from_rel_rect(
                self.relative_rect,
                self.ui_container,
                self.anchors,
                relative_right_margin,
                relative_bottom_margin,
                self.dynamic_width,
                self.dynamic_height,
            )
        )

        new_left, new_top = rect.topleft
        new_width, new_height = rect.size

        self.rect.left = new_left
        self.rect.top = new_top

        new_width, new_height = self._get_clamped_to_minimum_dimensions(
            (new_width, new_height)
        )
        if (new_height != self.relative_rect.height) or (
            new_width != self.relative_rect.width
        ):
            self.set_dimensions((new_width, new_height))

    def _update_relative_rect_position_from_anchors(self, recalculate_margins=False):
        """
        Called when our element's absolute position has been forcibly changed.
        """

        # This is a bit easier to calculate than getting the absolute position from the
        # relative one, because the absolute position rectangle is always relative to the top
        # left of the screen.

        # Setting these to None means we are always recalculating the margins in here.
        self.relative_bottom_margin = None
        self.relative_right_margin = None

        new_top = 0
        new_bottom = 0
        top_offset = self._calc_top_offset(self.ui_container, self.anchors)
        bottom_offset = self._calc_bottom_offset(self.ui_container, self.anchors)

        center_x_and_y = "center" in self.anchors and self.anchors["center"] == "center"
        if (
            "centery" in self.anchors and self.anchors["centery"] == "centery"
        ) or center_x_and_y:
            centery_offset = self._calc_centery_offset(self.ui_container, self.anchors)
            new_top = self.rect.top + self.relative_rect.height // 2 - centery_offset
            new_bottom = (
                self.rect.bottom + self.relative_rect.height // 2 - centery_offset
            )

        if "top" in self.anchors:
            if self.anchors["top"] == "top":
                new_top = self.rect.top - top_offset
                new_bottom = self.rect.bottom - top_offset
            elif self.anchors["top"] == "bottom":
                new_top = self.rect.top - bottom_offset
                if self.relative_bottom_margin is None or recalculate_margins:
                    self.relative_bottom_margin = bottom_offset - self.rect.bottom
                new_bottom = self.rect.bottom - bottom_offset

        if "bottom" in self.anchors:
            if self.anchors["bottom"] == "top":
                new_top = self.rect.top - top_offset
                new_bottom = self.rect.bottom - top_offset
            elif self.anchors["bottom"] == "bottom":
                if "top" not in self.anchors or self.anchors["top"] != "top":
                    new_top = self.rect.top - bottom_offset
                if self.relative_bottom_margin is None or recalculate_margins:
                    self.relative_bottom_margin = bottom_offset - self.rect.bottom
                new_bottom = self.rect.bottom - bottom_offset

        new_left = 0
        new_right = 0
        left_offset = self._calc_left_offset(self.ui_container, self.anchors)
        right_offset = self._calc_right_offset(self.ui_container, self.anchors)

        if (
            "centerx" in self.anchors and self.anchors["centerx"] == "centerx"
        ) or center_x_and_y:
            centerx_offset = self._calc_centerx_offset(self.ui_container, self.anchors)
            new_left = self.rect.left + self.relative_rect.width // 2 - centerx_offset
            new_right = self.rect.right + self.relative_rect.width // 2 - centerx_offset

        if "left" in self.anchors:
            if self.anchors["left"] == "left":
                new_left = self.rect.left - left_offset
                new_right = self.rect.right - left_offset
            elif self.anchors["left"] == "right":
                new_left = self.rect.left - right_offset
                if self.relative_right_margin is None or recalculate_margins:
                    self.relative_right_margin = right_offset - self.rect.right
                new_right = self.rect.right - right_offset

        if "right" in self.anchors:
            if self.anchors["right"] == "left":
                new_left = self.rect.left - left_offset
                new_right = self.rect.right - left_offset
            elif self.anchors["right"] == "right":
                if "left" not in self.anchors or self.anchors["left"] != "left":
                    new_left = self.rect.left - right_offset
                if self.relative_right_margin is None or recalculate_margins:
                    self.relative_right_margin = right_offset - self.rect.right
                new_right = self.rect.right - right_offset

        # set bottom and right first in case these are only anchors available
        self.relative_rect.bottom = new_bottom
        self.relative_rect.right = new_right

        # set top and left last to give these priority, in most cases where all anchors are set
        # we want relative_rect parameters to be correct for whatever the top & left sides are
        # anchored to. The data for the bottom and right in cases where left is anchored
        # differently to right and/or top is anchored differently to bottom should be captured by
        # the bottom and right margins.
        self.relative_rect.left = new_left
        self.relative_rect.top = new_top

    def _update_container_clip(self):
        """
        Creates a clipping rectangle for the element's image surface based on whether this
        element is inside its container, part-way in it, or all the way out of it.

        """
        if self.ui_container.get_container().get_image_clipping_rect() is not None:
            container_clip_rect = (
                self.ui_container.get_container().get_image_clipping_rect().copy()
            )
            container_clip_rect.left += (
                self.ui_container.get_container().get_rect().left
            )
            container_clip_rect.top += self.ui_container.get_container().get_rect().top
            if not container_clip_rect.contains(self.rect):
                self._calculate_image_clip_rect(container_clip_rect)
            else:
                self._restore_container_clipped_images()

        elif not self.ui_container.get_container().get_rect().contains(self.rect):
            self._calculate_image_clip_rect(
                self.ui_container.get_container().get_rect()
            )
        else:
            self._restore_container_clipped_images()

    def _calculate_image_clip_rect(self, container_clip_rect):
        left = max(0, container_clip_rect.left - self.rect.left)
        right = max(
            0, self.rect.width - max(0, self.rect.right - container_clip_rect.right)
        )
        top = max(0, container_clip_rect.top - self.rect.top)
        bottom = max(
            0, self.rect.height - max(0, self.rect.bottom - container_clip_rect.bottom)
        )
        clip_rect = pygame.Rect(left, top, max(0, right - left), max(0, bottom - top))
        self._clip_images_for_container(clip_rect)

    def update_containing_rect_position(self):
        """
        Updates the position of this element based on the position of its container. Usually
        called when the container has moved.
        """
        self._update_absolute_rect_position_from_anchors()

        if self.drawable_shape is not None:
            self.drawable_shape.set_position(self.rect.topleft)

        self._update_container_clip()

    def set_relative_position(self, position: Coordinate):
        """
        Method to directly set the relative rect position of an element.

        :param position: The new position to set.

        """
        self.relative_rect.x = int(position[0])
        self.relative_rect.y = int(position[1])

        self._update_absolute_rect_position_from_anchors(recalculate_margins=True)

        if self.drawable_shape is not None:
            self.drawable_shape.set_position(self.rect.topleft)

        self._update_container_clip()
        if self.ui_container is not None:
            self.ui_container.get_container().on_contained_elements_changed(self)

    def set_position(self, position: Coordinate):
        """
        Method to directly set the absolute screen rect position of an element.

        :param position: The new position to set.

        """
        self.rect.x = int(position[0])
        self.rect.y = int(position[1])
        self._update_relative_rect_position_from_anchors(recalculate_margins=True)

        if self.drawable_shape is not None:
            self.drawable_shape.set_position(self.rect.topleft)
        self._update_container_clip()
        if self.ui_container is not None:
            self.ui_container.get_container().on_contained_elements_changed(self)

    def set_minimum_dimensions(self, dimensions: Coordinate):
        """
        If this window is resizable, then the dimensions we set here will be the minimum that
        users can change the window to. They are also used as the minimum size when
        'set_dimensions' is called.

        :param dimensions: The new minimum dimension for the window.

        """
        if self.ui_container is not None:
            self.minimum_dimensions = (
                min(
                    self.ui_container.get_container().get_rect().width,
                    int(dimensions[0]),
                ),
                min(
                    self.ui_container.get_container().get_rect().height,
                    int(dimensions[1]),
                ),
            )

        if (self.rect.width < self.minimum_dimensions[0]) or (
            self.rect.height < self.minimum_dimensions[1]
        ):
            new_width = max(self.minimum_dimensions[0], self.rect.width)
            new_height = max(self.minimum_dimensions[1], self.rect.height)
            self.set_dimensions((new_width, new_height))

    def set_dimensions(self, dimensions: Coordinate, clamp_to_container: bool = False):
        """
        Method to directly set the dimensions of an element. And set whether the elements are dynamic.

        NOTE: Using this on elements inside containers with non-default anchoring arrangements
        may make a mess of them.

        :param dimensions: The new dimensions to set. If it is a negative value, the element will become
                            dynamically sized, otherwise it will become statically sized.
        :param clamp_to_container: Whether we should clamp the dimensions to the
                                   dimensions of the container or not.
        """
        is_dynamic = False
        if dimensions[0] < 0:
            self._set_dynamic_width()
            is_dynamic = True
        else:
            self._set_dynamic_width(False)

        if dimensions[1] < 0:
            self._set_dynamic_height()
            is_dynamic = True
        else:
            self._set_dynamic_height(False)

        if is_dynamic:
            self.rebuild()
        else:
            self._set_dimensions(dimensions, clamp_to_container)

    def _set_dimensions(self, dimensions: Coordinate, clamp_to_container: bool = False):
        """
        Method to directly set the dimensions of an element.
        Dimensions must be positive values.

        :param dimensions: The new dimensions to set.
        :param clamp_to_container: Whether we should clamp the dimensions to the
                                   dimensions of the container or not.
        """
        dimensions = self._get_clamped_to_minimum_dimensions(
            dimensions, clamp_to_container
        )
        self.relative_rect.width = int(dimensions[0])
        self.relative_rect.height = int(dimensions[1])
        self.rect.size = self.relative_rect.size

        if self.relative_rect.width >= 0 and self.relative_rect.height >= 0:
            self._update_absolute_rect_position_from_anchors(recalculate_margins=True)

            if self.drawable_shape is not None and self.drawable_shape.set_dimensions(
                self.relative_rect.size
            ):
                self._set_image(self.drawable_shape.get_fresh_surface())

            self._update_container_clip()
            if self.ui_container is not None:
                self.ui_container.get_container().on_contained_elements_changed(self)

    def update(self, time_delta: float):
        """
        Updates this element's drawable shape, if it has one.

        :param time_delta: The time passed between frames, measured in seconds.

        """
        if self.alive() and self.drawable_shape is not None:
            self.drawable_shape.update(time_delta)
            if self.drawable_shape.has_fresh_surface():
                self.on_fresh_drawable_shape_ready()

    def change_layer(self, new_layer: int):
        """
        Changes the layer this element is on.

        :param new_layer: The layer to change this element to.

        """
        if new_layer != self._layer:
            self.ui_group.change_layer(self, new_layer)
            self._layer = new_layer

    def kill(self):
        """
        Overriding regular sprite kill() method to remove the element from its container.
        Will also kill any tooltips belonging to this element.
        """
        if self.tool_tip is not None:
            self.tool_tip.kill()
        self.ui_container.get_container().remove_element(self)
        self.remove_element_from_focus_set(self)
        super().kill()

    def check_hover(self, time_delta: float, hovered_higher_element: bool) -> bool:
        """
        A method that helps us to determine which, if any, UI Element is currently being hovered
        by the mouse.

        :param time_delta: A float, the time in seconds between the last call to this function
                           and now (roughly).
        :param hovered_higher_element: A boolean, representing whether we have already hovered a
                                       'higher' element.

        :return bool: A boolean that is true if we have hovered a UI element, either just now or
                      before this method.
        """
        should_block_hover = False
        if self.alive():
            mouse_x, mouse_y = self.ui_manager.get_mouse_position()
            mouse_pos = pygame.math.Vector2(mouse_x, mouse_y)

            if self.hover_point(mouse_x, mouse_y) and not hovered_higher_element:
                should_block_hover = True

                if self.can_hover():
                    if not self.hovered:
                        self.hovered = True
                        self.on_hovered()

                    self.while_hovering(time_delta, mouse_pos)
                elif self.hovered:
                    self.hovered = False
                    self.on_unhovered()
            elif self.hovered:
                self.hovered = False
                self.on_unhovered()
        elif self.hovered:
            self.hovered = False
        return should_block_hover

    def on_fresh_drawable_shape_ready(self):
        """
        Called when our drawable shape has finished rebuilding the active surface. This is needed
        because sometimes we defer rebuilding until a more advantageous (read quieter) moment.
        """
        self._set_image(self.drawable_shape.get_fresh_surface())

    def on_hovered(self):
        """
        Called when this UI element first enters the 'hovered' state.
        """
        self.hover_time = 0.0

    def on_unhovered(self):
        """
        Called when this UI element leaves the 'hovered' state.
        """
        if self.tool_tip is not None:
            self.tool_tip.kill()
            self.tool_tip = None

    def while_hovering(
        self,
        time_delta: float,
        mouse_pos: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]],
    ):
        """
        Called while we are in the hover state. It will create a tool tip if we've been in the
        hover state for a while, the text exists to create one, and we haven't created one already.

        :param time_delta: Time in seconds between calls to update.
        :param mouse_pos: The current position of the mouse.

        """
        if (
            self.tool_tip is None
            and self.tool_tip_text is not None
            and self.hover_time > self.tool_tip_delay
        ):
            hover_height = int(self.rect.height / 2)
            self.tool_tip = self.ui_manager.create_tool_tip(
                text=self.tool_tip_text,
                position=(int(mouse_pos[0]), int(self.rect.centery)),
                hover_distance=(0, hover_height),
                parent_element=self,
                object_id=self.tool_tip_object_id,
                wrap_width=self.tool_tip_wrap_width,
                text_kwargs=self.tool_tip_text_kwargs,
            )

        self.hover_time += time_delta

    def can_hover(self) -> bool:
        """
        A stub method to override. Called to test if this method can be hovered.
        """
        return self.alive()

    def hover_point(self, hover_x: float, hover_y: float) -> bool:
        """
        Test if a given point counts as 'hovering' this UI element. Normally that is a
        straightforward matter of seeing if a point is inside the rectangle. Occasionally it
        will also check if we are in a wider zone around a UI element once it is already active,
        this makes it easier to move scroll bars and the like.

        :param hover_x: The x (horizontal) position of the point.
        :param hover_y: The y (vertical) position of the point.

        :return: Returns True if we are hovering this element.

        """

        container_clip_rect = pygame.Rect(0, 0, 0, 0)
        if self.ui_container is not None:
            container_clip_rect = self.ui_container.get_container().get_rect().copy()
            image_clip_rect = (
                self.ui_container.get_container().get_image_clipping_rect()
            )
            if image_clip_rect is not None:
                container_clip_rect.size = image_clip_rect.size
                container_clip_rect.left += image_clip_rect.left
                container_clip_rect.top += image_clip_rect.top

        if self.drawable_shape is not None:
            return self.drawable_shape.collide_point((hover_x, hover_y)) and bool(
                container_clip_rect.collidepoint(hover_x, hover_y)
            )

        return bool(self.rect.collidepoint(hover_x, hover_y)) and bool(
            container_clip_rect.collidepoint(hover_x, hover_y)
        )

    # pylint: disable=unused-argument
    def process_event(self, event: pygame.event.Event) -> bool:
        """
        A stub to override. Gives UI Elements access to pygame events.

        :param event: The event to process.

        :return: Should return True if this element makes use of this event.

        """
        return False

    def focus(self):
        """
        A stub to override. Called when we focus this UI element.
        """
        self._is_focused = True

    def unfocus(self):
        """
        A stub to override. Called when we stop focusing this UI element.
        """
        self._is_focused = False

    def rebuild_from_changed_theme_data(self):
        """
        A stub to override when we want to rebuild from theme data.
        """

    def rebuild(self):
        """
        Takes care of rebuilding this element. Most derived elements are going to override this,
        and hopefully call the super() class method.

        """
        if self._visual_debug_mode:
            self._set_image(self.pre_debug_image)
            self.pre_debug_image = None

    def set_visual_debug_mode(self, activate_mode: bool):
        """
        Enables a debug mode for the element which displays layer information on top of it in
        a tiny font.

        :param activate_mode: True or False to enable or disable the mode.

        """
        if activate_mode:
            default_font = (
                self.ui_manager.get_theme().get_font_dictionary().get_default_font()
            )
            layer_text_render = render_white_text_alpha_black_bg(
                default_font, f"UI Layer: {self._layer}"
            )

            if self.image is not None:
                self._put_visual_debug_text_onto_element(layer_text_render)
            else:
                self._set_image(layer_text_render)
            self._visual_debug_mode = True
        else:
            self.rebuild()
            self._visual_debug_mode = False

    def _put_visual_debug_text_onto_element(self, layer_text_render):
        self.pre_debug_image = self.image.copy()
        # check if our surface is big enough to hold the debug info,
        # if not make a new, bigger copy
        make_new_larger_surface = False
        surf_width = self.image.get_width()
        surf_height = self.image.get_height()
        if self.image.get_width() < layer_text_render.get_width():
            make_new_larger_surface = True
            surf_width = layer_text_render.get_width()
        if self.image.get_height() < layer_text_render.get_height():
            make_new_larger_surface = True
            surf_height = layer_text_render.get_height()

        if make_new_larger_surface:
            new_surface = pygame.surface.Surface(
                (surf_width, surf_height), flags=pygame.SRCALPHA, depth=32
            )
            basic_blit(new_surface, self.image, (0, 0))
            self._set_image(new_surface)
        basic_blit(self.image, layer_text_render, (0, 0))

    def _clip_images_for_container(self, clip_rect: Union[pygame.Rect, None]):
        """
        Set the current image clip based on the container.

        :param clip_rect: The clipping rectangle.

        """
        self._set_image_clip(clip_rect)

    def _restore_container_clipped_images(self):
        """
        Clear the image clip.

        """
        self._set_image_clip(None)

    def _set_image_clip(self, rect: Union[pygame.Rect, None]):
        """
        Sets a clipping rectangle on this element's image determining what portion of it will
        actually be displayed when this element is blitted to the screen.

        :param rect: A clipping rectangle, or None to clear the clip.

        """
        if rect is not None:
            rect.width = max(rect.width, 0)
            rect.height = max(rect.height, 0)

            if self._pre_clipped_image is None and self.image is not None:
                self._pre_clipped_image = self.image.copy()

            self._image_clip = rect
            if self.image is not None and self._pre_clipped_image is not None:
                if self.image.get_size() != self._pre_clipped_image.get_size():
                    self.image = pygame.Surface(
                        self._pre_clipped_image.get_size(),
                        flags=pygame.SRCALPHA,
                        depth=32,
                    )
                self.image.fill(pygame.Color("#00000000"))
                basic_blit(
                    self.image,
                    self._pre_clipped_image,
                    self._image_clip,
                    self._image_clip,
                )

        elif self._image_clip is not None:
            self._image_clip = None
            self._set_image(self._pre_clipped_image)
        else:
            self._image_clip = None

    def _get_pre_clipped_image_size(self) -> Coordinate:
        if self._pre_clipped_image is not None:
            return self._pre_clipped_image.get_size()
        else:
            return 0, 0

    def get_image_clipping_rect(self) -> Union[pygame.Rect, None]:
        """
        Obtain the current image clipping rect.

        :return: The current clipping rect. Maybe None.

        """
        return self._image_clip

    def set_image(self, new_image: Union[pygame.surface.Surface, None]):
        """
        This used to be the way to set the proper way to set the .image property of a UIElement (inherited from
        pygame.Sprite), but it is intended for internal use in the library - not for adding actual images/pictures
        on UIElements. As such I've renamed the original function to make it protected and not part of the interface
        and deprecated this one for most elements.

        :return:
        """
        warnings.warn(
            "This method will be removed for most elements from version 0.8.0",
            DeprecationWarning,
            stacklevel=2,
        )
        self._set_image(new_image)

    def _set_image(self, new_image: Union[pygame.surface.Surface, None]):
        """
        Wraps setting the image variable of this element so that we also set the current image
        clip on the image at the same time.

        :param new_image: The new image to set.

        """
        image_clipping_rect = self.get_image_clipping_rect()
        if image_clipping_rect is not None and new_image is not None:
            self._pre_clipped_image = new_image
            if image_clipping_rect.width == 0 and image_clipping_rect.height == 0:
                self.image = self.ui_manager.get_universal_empty_surface()
            else:
                self.image = pygame.surface.Surface(
                    self._pre_clipped_image.get_size(), flags=pygame.SRCALPHA, depth=32
                )
                self.image.fill(pygame.Color("#00000000"))
                basic_blit(
                    self.image,
                    self._pre_clipped_image,
                    image_clipping_rect,
                    image_clipping_rect,
                )
        else:
            self.image = new_image.copy() if new_image is not None else None
            self._pre_clipped_image = None

    def get_top_layer(self) -> int:
        """
        Assuming we have correctly calculated the 'thickness' of it, this method will
        return the top of this element.

        :return int: An integer representing the current highest layer being used by this element.

        """
        return self._layer + self.layer_thickness

    def get_starting_height(self) -> int:
        """
        Get the starting layer height of this element. (i.e. the layer we start placing it on
        *above* its container, it may use more layers above this layer)

        :return: an integer representing the starting layer height.

        """
        return self.starting_height

    def _check_shape_theming_changed(self, defaults: Dict[str, Any]) -> bool:
        """
        Checks all the standard miscellaneous shape theming parameters.

        :param defaults: A dictionary of default values
        :return: True if any have changed.
        """
        has_any_changed = False

        if self._check_misc_theme_data_changed(
            "border_width", defaults["border_width"], int
        ):
            has_any_changed = True

        if self._check_misc_theme_data_changed(
            "shadow_width", defaults["shadow_width"], int
        ):
            has_any_changed = True

        if self._check_misc_theme_data_changed(
            "border_overlap", defaults["border_overlap"], int
        ):
            has_any_changed = True

        # corner radius
        temp_corner_radius = [0, 0, 0, 0]
        try:
            str_corner_radius = self.ui_theme.get_misc_data(
                "shape_corner_radius", self.combined_element_ids
            )
            if isinstance(str_corner_radius, str):
                corner_radii_list = str_corner_radius.split(",")
                if len(corner_radii_list) == 4:
                    temp_corner_radius[0] = int(corner_radii_list[0])
                    temp_corner_radius[1] = int(corner_radii_list[1])
                    temp_corner_radius[2] = int(corner_radii_list[2])
                    temp_corner_radius[3] = int(corner_radii_list[3])
                if len(corner_radii_list) == 1:
                    temp_corner_radius[0] = int(corner_radii_list[0])
                    temp_corner_radius[1] = int(corner_radii_list[0])
                    temp_corner_radius[2] = int(corner_radii_list[0])
                    temp_corner_radius[3] = int(corner_radii_list[0])
        except (LookupError, ValueError):
            self.shape_corner_radius = defaults["shape_corner_radius"]
        finally:
            if temp_corner_radius != self.shape_corner_radius:
                self.shape_corner_radius = temp_corner_radius
                has_any_changed = True

        return has_any_changed

    def _check_misc_theme_data_changed(
        self,
        attribute_name: str,
        default_value: Any,
        casting_func: Callable[[Any], Any],
        allowed_values: Union[List, None] = None,
    ) -> bool:
        """
        Checks if the value of a pieces of miscellaneous theming data has changed, and if it has,
        updates the corresponding attribute on the element and returns True.

        :param attribute_name: The name of the attribute.
        :param default_value: The default value for the attribute.
        :param casting_func: The function to cast to the type of the data.

        :return: True if the attribute has changed.

        """
        has_changed = False
        attribute_value = default_value
        try:
            attribute_value = casting_func(
                self.ui_theme.get_misc_data(attribute_name, self.combined_element_ids)
            )
        except (LookupError, ValueError):
            attribute_value = default_value
        finally:
            if allowed_values and attribute_value not in allowed_values:
                attribute_value = default_value

            if attribute_value != getattr(self, attribute_name, default_value):
                setattr(self, attribute_name, attribute_value)
                has_changed = True
        return has_changed

    def disable(self):
        """
        Disables elements so they are no longer interactive.
        This is just a default fallback implementation for elements that don't define their own.

        Elements should handle their own enabling and disabling.
        """
        self.is_enabled = False

    def enable(self):
        """
        Enables elements so they are interactive again.
        This is just a default fallback implementation for elements that don't define their own.

        Elements should handle their own enabling and disabling.
        """
        self.is_enabled = True

    def show(self):
        """
        Shows the widget, which means the widget will get drawn and will process events.
        """
        self.visible = True

    def hide(self):
        """
        Hides the widget, which means the widget will not get drawn and will not process events.
        Clear hovered state.
        """
        self.visible = False

        self.hovered = False
        self.hover_time = 0.0

    def _get_appropriate_state_name(self):
        """
        Returns a string representing the appropriate state for the widgets DrawableShapes.
        Currently only returns either 'normal' or 'disabled' based on is_enabled.
        """

        return "normal" if self.is_enabled else "disabled"

    def on_locale_changed(self):
        pass

    def get_anchor_targets(self) -> list:
        targets = []
        if self.anchors is not None:
            if "left_target" in self.anchors:
                targets.append(self.anchors["left_target"])
            if "right_target" in self.anchors:
                targets.append(self.anchors["right_target"])
            if "top_target" in self.anchors:
                targets.append(self.anchors["top_target"])
            if "bottom_target" in self.anchors:
                targets.append(self.anchors["bottom_target"])

        return targets

    @staticmethod
    def tuple_extract(str_data: str) -> Tuple[int, int]:
        """
        Used for parsing pairs of coordinates in themes from string data into numerical tuples.
        e.g. 5,10

        :param str_data: the comma separated string of two numbers to parse.

        :return: a tuple of two ints
        """
        x, y = str_data.split(",")
        return int(x), int(y)

    def update_theming(self, new_theming_data: str):
        """
        Update the theming for this element using the most specific ID assigned to it.

        If you have not given this element a unique ID, this function will also update the theming of other elements
        of this theming class or of this element type.

        :param new_theming_data: the new theming data in a json string
        """
        self.ui_theme.update_single_element_theming(
            self.most_specific_combined_id, new_theming_data
        )
        self.rebuild_from_changed_theme_data()

    def set_tooltip(
        self,
        text: Optional[str] = None,
        object_id: Optional[ObjectID] = None,
        text_kwargs: Optional[Dict[str, str]] = None,
        delay: Optional[float] = None,
        wrap_width: Optional[int] = None,
    ):
        """
        Setup floating tool tip data for this UI element.

        :param text: the text for the tool tip.
        :param object_id: an object ID for the tooltip - useful for theming
        :param text_kwargs: key word arguments for the tool tip text
        :param delay: how long it takes the tooltip to appear when statically hovering the UI element
        :param wrap_width: how wide the tooltip will grow before wrapping.
        :return:
        """
        self.tool_tip_text = text
        self.tool_tip_text_kwargs = {}
        if text_kwargs is not None:
            self.tool_tip_text_kwargs = text_kwargs
        self.tool_tip_object_id = object_id

        if delay is not None:
            self.tool_tip_delay = delay

        self.tool_tip_wrap_width = wrap_width
