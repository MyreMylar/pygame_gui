import pygame
import warnings
from typing import List, Union, Tuple, Dict

from pygame_gui.core.interfaces import IContainerInterface, IUIManagerInterface


class UIElement(pygame.sprite.Sprite):
    """
    A base class for UI elements. You shouldn't create UI Element objects, instead all UI Element classes should
    derive from this class. Inherits from pygame.sprite.Sprite.

    :param relative_rect: A rectangle shape of the UI element, the position is relative to the element's container.
    :param manager: The UIManager that manages this UIElement.
    :param container: A container that this element is contained in.
    :param starting_height: Used to record how many layers above it's container this element should be. Normally 1.
    :param layer_thickness: Used to record how 'thick' this element is in layers. Normally 1.
    :param element_ids: A list of ids that describe the 'hierarchy' of UIElements that this UIElement is part of.
    :param object_ids: A list of custom defined IDs that describe the 'hierarchy' that this UIElement is part of.
    """
    def __init__(self, relative_rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 container: Union[IContainerInterface, None],
                 *,
                 starting_height: int,
                 layer_thickness: int,
                 object_ids: Union[List[Union[str, None]], None] = None,
                 element_ids: Union[List[str], None] = None,
                 anchors: Dict[str, str] = None):

        self._layer = 0
        self.ui_manager = manager
        super().__init__(self.ui_manager.get_sprite_group())
        self.relative_rect = relative_rect
        self.ui_group = self.ui_manager.get_sprite_group()
        self.ui_theme = self.ui_manager.get_theme()
        self.object_ids = object_ids
        self.element_ids = element_ids

        combined_ids = self.ui_manager.get_theme().build_all_combined_ids(self.element_ids, self.object_ids)
        if combined_ids is not None and len(combined_ids) > 0:
            self.most_specific_combined_id = combined_ids[0]
        else:
            self.most_specific_combined_id = 'no_id'

        self.layer_thickness = layer_thickness
        self.starting_height = starting_height

        if container is None:
            if self.ui_manager.get_root_container() is not None:
                container = self.ui_manager.get_root_container()
            else:
                container = self

        if isinstance(container, IContainerInterface):
            self.ui_container = container.get_container()

        if self.ui_container is not None and self.ui_container is not self:
            self.ui_container.add_element(self)

        self.anchors = anchors
        if self.anchors is None:
            self.anchors = {'left': 'left',
                            'top': 'top',
                            'right': 'left',
                            'bottom': 'top'}

        self.rect = self.relative_rect.copy()
        self.drawable_shape = None  # type: Union['DrawableShape', None]
        self.image = None

        self.relative_bottom_margin = None
        self.relative_right_margin = None
        self._update_absolute_rect_position_from_anchors()

        self.is_enabled = True
        self.hovered = False
        self.is_focused = False
        self.hover_time = 0.0

        self.pre_debug_image = None
        self._pre_clipped_image = None

        self._image_clip = None
        self._update_container_clip()

    def _update_absolute_rect_position_from_anchors(self):
        """
        Called when our element's relative position has changed.
        """
        new_top = 0
        if self.anchors['top'] == 'top':
            new_top = self.relative_rect.top + self.ui_container.rect.top
        elif self.anchors['top'] == 'bottom':
            new_top = self.relative_rect.top + self.ui_container.rect.bottom
        else:
            warnings.warn('Unsupported anchor top target: ' + self.anchors['top'])

        new_bottom = 0
        if self.anchors['bottom'] == 'top':
            new_bottom = self.relative_rect.bottom + self.ui_container.rect.top
        elif self.anchors['bottom'] == 'bottom':
            if self.relative_bottom_margin is None:
                self.relative_bottom_margin = self.ui_container.rect.bottom - (new_top + self.relative_rect.height)
            new_bottom = self.ui_container.rect.bottom - self.relative_bottom_margin
        else:
            warnings.warn('Unsupported anchor bottom target: ' + self.anchors['bottom'])

        new_left = 0
        if self.anchors['left'] == 'left':
            new_left = self.relative_rect.left + self.ui_container.rect.left
        elif self.anchors['left'] == 'right':
            new_left = self.relative_rect.left + self.ui_container.rect.right
        else:
            warnings.warn('Unsupported anchor top target: ' + self.anchors['left'])

        new_right = 0
        if self.anchors['right'] == 'left':
            new_right = self.relative_rect.right + self.ui_container.rect.left
        elif self.anchors['right'] == 'right':
            if self.relative_right_margin is None:
                self.relative_right_margin = self.ui_container.rect.right - (new_left + self.relative_rect.width)
            new_right = self.ui_container.rect.right - self.relative_right_margin
        else:
            warnings.warn('Unsupported anchor bottom target: ' + self.anchors['right'])

        new_height = new_bottom - new_top
        new_width = new_right - new_left
        if (new_height != self.relative_rect.height) or (new_width != self.relative_rect.width):
            self.set_dimensions((new_width, new_height))

        self.rect.left = new_left
        self.rect.right = new_right
        self.rect.top = new_top
        self.rect.bottom = new_bottom

    def _update_relative_rect_position_from_anchors(self):
        """
        Called when our element's absolute position has been forcibly changed.
        """

        # This is a bit easier to calculate than getting the absolute position from the relative one, because the
        # absolute position rectangle is always relative to the top left of the screen.
        self.relative_bottom_margin = None
        self.relative_right_margin = None

        new_top = 0
        if self.anchors['top'] == 'top':
            new_top = self.rect.top - self.ui_container.rect.top
        elif self.anchors['top'] == 'bottom':
            new_top = self.rect.top - self.ui_container.rect.bottom
        else:
            warnings.warn('Unsupported anchor top target: ' + self.anchors['top'])

        new_bottom = 0
        if self.anchors['bottom'] == 'top':
            new_bottom = self.rect.bottom - self.ui_container.rect.top
        elif self.anchors['bottom'] == 'bottom':
            if self.relative_bottom_margin is None:
                self.relative_bottom_margin = self.ui_container.rect.bottom - self.rect.bottom
            new_bottom = self.rect.bottom - self.ui_container.rect.bottom
        else:
            warnings.warn('Unsupported anchor bottom target: ' + self.anchors['bottom'])

        new_left = 0
        if self.anchors['left'] == 'left':
            new_left = self.rect.left - self.ui_container.rect.left
        elif self.anchors['left'] == 'right':
            new_left = self.rect.left - self.ui_container.rect.right
        else:
            warnings.warn('Unsupported anchor top target: ' + self.anchors['left'])

        new_right = 0
        if self.anchors['right'] == 'left':
            new_right = self.rect.right - self.ui_container.rect.left
        elif self.anchors['right'] == 'right':
            if self.relative_right_margin is None:
                self.relative_right_margin = self.ui_container.rect.right - self.rect.right
            new_right = self.rect.right - self.ui_container.rect.right
        else:
            warnings.warn('Unsupported anchor bottom target: ' + self.anchors['right'])

        self.relative_rect.left = new_left
        self.relative_rect.right = new_right
        self.relative_rect.top = new_top
        self.relative_rect.bottom = new_bottom

    @staticmethod
    def create_valid_ids(container: Union[IContainerInterface, None], parent_element: Union[None, 'UIElement'],
                         object_id: str, element_id: str):
        """
        Creates valid id lists for an element. It will assert if users supply object IDs that won't work such as those
        containing full stops. These ID lists are used by the theming system to identify what theming parameters to
        apply to which element.

        :param container: The container for this element. If parent is None and the container is not then by default the container will be used as the parent.
        :param parent_element: Element that this element 'belongs to' in theming. Elements inherit colours from parents.
        :param object_id: An optional ID to help distinguish this element from other elements of the same class.
        :param element_id: A string ID representing this element's class.
        :return:
        """
        if parent_element is None and container is not None:
            id_parent = container
        else:
            id_parent = parent_element
        if object_id is not None and ('.' in object_id or ' ' in object_id):
            raise ValueError('Object ID cannot contain fullstops or spaces: ' + str(object_id))

        if id_parent is not None:
            new_element_ids = id_parent.element_ids.copy()
            new_element_ids.append(element_id)

            new_object_ids = id_parent.object_ids.copy()
            new_object_ids.append(object_id)
        else:
            new_element_ids = [element_id]
            new_object_ids = [object_id]

        return new_element_ids, new_object_ids

    def update_containing_rect_position(self):
        """
        Updates the position of this element based on the position of it's container. Usually called when the container
        has moved.
        """
        self._update_absolute_rect_position_from_anchors()

        if self.drawable_shape is not None:
            self.drawable_shape.set_position(self.rect.topleft)

        self._update_container_clip()

    def _update_container_clip(self):
        if self.ui_container.get_image_clipping_rect() is not None:
            container_clip_rect = self.ui_container.get_image_clipping_rect().copy()
            container_clip_rect.left += self.ui_container.rect.left
            container_clip_rect.top += self.ui_container.rect.top
            if not container_clip_rect.contains(self.rect):
                left = max(0, container_clip_rect.left - self.rect.left)
                right = max(0, self.rect.width - max(0, self.rect.right - container_clip_rect.right))
                top = max(0, container_clip_rect.top - self.rect.top)
                bottom = max(0, self.rect.height - max(0, self.rect.bottom - container_clip_rect.bottom))
                clip_rect = pygame.Rect(left, top,
                                        right - left,
                                        bottom - top)
                self._clip_images_for_container(clip_rect)
            else:
                self._restore_container_clipped_images()

        elif not self.ui_container.rect.contains(self.rect):
            left = max(0, self.ui_container.rect.left - self.rect.left)
            right = max(0, self.rect.width - max(0, self.rect.right - self.ui_container.rect.right))
            top = max(0, self.ui_container.rect.top - self.rect.top)
            bottom = max(0, self.rect.height - max(0, self.rect.bottom - self.ui_container.rect.bottom))
            clip_rect = pygame.Rect(left, top,
                                    right - left,
                                    bottom - top)
            self._clip_images_for_container(clip_rect)
        else:
            self._restore_container_clipped_images()

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
        Overriding regular sprite kill() method to remove the element from it's container.
        """
        self.ui_container.remove_element(self)
        super().kill()

    def check_hover(self, time_delta: float, hovered_higher_element: bool) -> bool:
        """
        A method that helps us to determine which, if any, UI Element is currently being hovered by the mouse.

        :param time_delta: A float, the time in seconds between the last call to this function and now (roughly).
        :param hovered_higher_element: A boolean, representing whether we have already hovered a 'higher' element.
        :return bool: A boolean that is true if we have hovered a UI element, either just now or before this method.
        """
        if self.alive() and self.can_hover():
            mouse_x, mouse_y = self.ui_manager.get_mouse_position()
            mouse_pos = pygame.math.Vector2(mouse_x, mouse_y)

            if self.is_enabled and self.hover_point(mouse_x, mouse_y) and not hovered_higher_element:
                if not self.hovered:
                    self.hovered = True
                    self.on_hovered()

                hovered_higher_element = True
                self.while_hovering(time_delta, mouse_pos)

            else:
                if self.hovered:
                    self.hovered = False
                    self.on_unhovered()
        elif self.hovered:
            self.hovered = False
        return hovered_higher_element

    def set_relative_position(self, position: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        """
        Method to directly set the relative rect position of an element.

        :param position: The new position to set.
        """
        self.relative_rect.x = int(position[0])
        self.relative_rect.y = int(position[1])
        self._update_absolute_rect_position_from_anchors()

        if self.drawable_shape is not None:
            self.drawable_shape.set_position(self.rect.topleft)

        self._update_container_clip()

    def set_position(self, position: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        """
        Method to directly set the absolute screen rect position of an element.

        :param position: The new position to set.
        """
        self.rect.x = int(position[0])
        self.rect.y = int(position[1])
        self._update_relative_rect_position_from_anchors()

        if self.drawable_shape is not None:
            self.drawable_shape.set_position(self.rect.topleft)

        self._update_container_clip()

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]):
        """
        Method to directly set the dimensions of an element.

        NOTE: Using this on elements inside containers with non-default anchoring arrangements may make a mess of them.

        :param dimensions: The new dimensions to set.
        """
        self.relative_rect.width = int(dimensions[0])
        self.relative_rect.height = int(dimensions[1])
        self.rect.size = self.relative_rect.size

        if self.relative_right_margin is not None:
            self.relative_right_margin = self.ui_container.rect.right - self.rect.right

        if self.relative_bottom_margin is not None:
            self.relative_bottom_margin = self.ui_container.rect.bottom - self.rect.bottom

        if self.drawable_shape is not None:
            self.drawable_shape.set_dimensions(self.relative_rect.size)
            self.set_image(self.drawable_shape.get_fresh_surface())  # needed to stop resizing 'lag'

        self._update_container_clip()

    def update(self, time_delta: float):
        """
        Updates this element's drawable shape, if it has one.

        :param time_delta: The time passed between frames, measured in seconds.
        """
        if self.alive() and self.drawable_shape is not None:
            self.drawable_shape.update(time_delta)
            if self.drawable_shape.has_fresh_surface():
                self.on_fresh_drawable_shape_ready()

    def on_fresh_drawable_shape_ready(self):
        self.set_image(self.drawable_shape.get_fresh_surface())

    def on_hovered(self):
        """
        A stub to override. Called when this UI element first enters the 'hovered' state.
        """
        pass

    def while_hovering(self, time_delta: float, mouse_pos: pygame.math.Vector2):
        """
        A stub method to override. Called when this UI element is currently hovered.

        :param time_delta: A float, the time in seconds between the last call to this function and now (roughly).
        :param mouse_pos: The current position of the mouse as 2D Vector.
        """
        pass

    def hover_point(self, x: float, y: float) -> bool:
        """
        Test if a given point counts as 'hovering' this UI element. Normally that is a straightforward matter of
        seeing if a point is inside the rectangle. Occasionally it will also check if we are in a wider zone around
        a UI element once it is already active, this makes it easier to move scroll bars and the like.

        :param x: The x (horizontal) position of the point.
        :param y: The y (vertical) position of the point.
        :return bool: Returns True if we are hovering this element.
        """
        if self.drawable_shape is not None:
            return self.drawable_shape.collide_point((x, y)) and bool(self.ui_container.rect.collidepoint(x, y))
        else:
            return bool(self.rect.collidepoint(x, y)) and bool(self.ui_container.rect.collidepoint(x, y))

    def on_unhovered(self):
        """
        A stub to override. Called when this UI element leaves the 'hovered' state.
        """
        pass

    def can_hover(self) -> bool:
        """
        A stub method to override. Called to test if this method can be hovered.
        """
        return True

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        A stub to override. Gives UI Elements access to pygame events.

        :param event: The event to process.
        :return bool: Should return True if this element makes use of this event.
        """
        if self is not None:
            return False

    def focus(self):
        """
        A stub to override. Called when we focus this UI element.
        """
        self.is_focused = True

    def unfocus(self):
        """
        A stub to override. Called when we stop focusing this UI element.
        """
        self.is_focused = False

    def rebuild_from_changed_theme_data(self):
        pass

    def rebuild(self):
        if self.pre_debug_image is not None:
            self.set_image(self.pre_debug_image)
            self.pre_debug_image = None

    def set_visual_debug_mode(self, activate_mode):
        if activate_mode:
            font_dict = self.ui_manager.get_theme().get_font_dictionary()
            default_font = font_dict.find_font(font_size=font_dict.debug_font_size,
                                               font_name=font_dict.default_font_name)
            layer_text_render = default_font.render("UI Layer: " + str(self._layer),
                                                    True, pygame.Color('#FFFFFFFF'))

            if self.image is not None:
                self.pre_debug_image = self.image.copy()
                # check if our surface is big enough to hold the debug info, if not make a new, bigger copy
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
                    new_surface = pygame.Surface((surf_width, surf_height), flags=pygame.SRCALPHA, depth=32)
                    new_surface.blit(self.image, (0, 0))
                    self.set_image(new_surface)
                self.image.blit(layer_text_render, (0, 0))
            else:
                self.set_image(layer_text_render)
        else:
            self.rebuild()

    def _clip_images_for_container(self, clip_rect):
        self.set_image_clip(clip_rect)

    def _restore_container_clipped_images(self):
        self.set_image_clip(None)

    def set_image_clip(self, rect):
        if rect is not None and self._pre_clipped_image is None and self.image is not None:
            self._pre_clipped_image = self.image.copy()

        if self._image_clip is not None and rect is None:
            self._image_clip = None
            self.set_image(self._pre_clipped_image)
        elif rect is not None:
            self._image_clip = rect
            if self.image is not None:
                self.image.fill(pygame.Color('#00000000'))
                self.image.blit(self._pre_clipped_image, self._image_clip, self._image_clip)
        else:
            self._image_clip = None

    def get_image_clipping_rect(self):
        return self._image_clip

    def set_image(self, new_image):
        if self._image_clip is not None and new_image is not None:
            self._pre_clipped_image = new_image
            if self._image_clip.width == 0 and self._image_clip.height == 0:
                self.image = self.ui_manager.get_universal_empty_surface()
            else:
                self.image = pygame.Surface(self._pre_clipped_image.get_size(), flags=pygame.SRCALPHA, depth=32)
                self.image.fill(pygame.Color('#00000000'))
                self.image.blit(self._pre_clipped_image, self._image_clip, self._image_clip)
        else:
            self.image = new_image.copy() if new_image is not None else None
            self._pre_clipped_image = None

    def get_top_layer(self):
        """
        Assuming we have correctly calculated the 'thickness' of this container, this method will return the top of
        this element.

        :return int: An integer representing the current highest layer being used by this element.
        """
        return self._layer + self.layer_thickness
