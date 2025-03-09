import io

from abc import ABCMeta, abstractmethod
from typing import Optional, List, Union, Dict, Any
from os import PathLike


import pygame

from pygame_gui.core.interfaces.font_dictionary_interface import (
    IUIFontDictionaryInterface,
)
from pygame_gui.core.interfaces.colour_gradient_interface import (
    IColourGradientInterface,
)
from pygame_gui.core.interfaces.gui_font_interface import IGUIFontInterface
from pygame_gui.core.package_resource import PackageResource
from pygame_gui.core.surface_cache import SurfaceCache
from pygame_gui.core.ui_shadow import ShadowGenerator


class IUIAppearanceThemeInterface(metaclass=ABCMeta):
    """
    A metaclass that defines the interface that a UI Appearance Theme uses.

    Interfaces like this help us evade cyclical import problems by allowing us to define the
    actual manager class later on and have it make use of the classes that use the interface.
    """

    @abstractmethod
    def get_font_dictionary(self) -> IUIFontDictionaryInterface:
        """
        Lets us grab the font dictionary, which is created by the theme object, so we can access
        it directly.

        :return UIFontDictionary: The font dictionary.
        """

    @abstractmethod
    def check_need_to_reload(self) -> bool:
        """
        Check if we need to reload our theme file because it's been modified. If so, trigger a
        reload and return True so that the UIManager can trigger elements to rebuild from
        the theme data.

        :return bool: True if we need to reload elements because the theme data has changed.
        """

    @abstractmethod
    def update_caching(self, time_delta: float):
        """
        Updates the various surface caches.

        """

    @abstractmethod
    def reload_theming(self):
        """
        We need to load our theme file to see if anything expensive has changed, if so trigger
        it to reload/rebuild.

        """

    @abstractmethod
    def build_all_combined_ids(
        self,
        element_base_ids: Union[None, List[Union[str, None]]],
        element_ids: Union[None, List[str]],
        class_ids: Union[None, List[Union[str, None]]],
        object_ids: Union[None, List[Union[str, None]]],
    ) -> List[str]:
        """
        Construct a list of combined element ids from the element's various accumulated ids.

        :param element_base_ids: when an element is also another element (e.g. a file dialog is also a window)
        :param element_ids: All the ids of elements this element is contained within.
        :param class_ids: All the ids of 'classes' that this element is contained within.
        :param object_ids: All the ids of objects this element is contained within.

        :return: A list of IDs that reference this element in order of decreasing specificity.
        """

    @abstractmethod
    def get_image(
        self, image_id: str, combined_element_ids: List[str]
    ) -> pygame.surface.Surface:
        """
        Will raise an exception if no image with the ids specified is found. UI elements that have
        an optional image display will need to handle the exception.

        :param combined_element_ids: A list of IDs representing an element's location in a
                                     hierarchy of elements.
        :param image_id: The id identifying the particular image spot in the UI we are looking for
                         an image to add to.

        :return: A pygame.surface.Surface
        """

    @abstractmethod
    def get_font_info(self, combined_element_ids: List[str]) -> Dict[str, Any]:
        """
        Uses some data about a UIElement to get font data as dictionary

        :param combined_element_ids: A list of IDs representing an element's location in an
                                     interleaved hierarchy of elements.

        :return dictionary: Data about the font requested
        """

    @abstractmethod
    def get_font(self, combined_element_ids: List[str]) -> IGUIFontInterface:
        """
        Uses some data about a UIElement to get a font object.

        :param combined_element_ids: A list of IDs representing an element's location in an
                                     interleaved hierarchy of elements.

        :return IGUIFontInterface: An interface to a pygame font object wrapper.
        """

    @abstractmethod
    def get_misc_data(
        self, misc_data_id: str, combined_element_ids: List[str]
    ) -> Union[str, Dict]:
        """
        Uses data about a UI element and a specific ID to try and find a piece of miscellaneous
        theming data. Raises an exception if it can't find the data requested, UI elements
        requesting optional data will need to handle this exception.

        :param combined_element_ids: A list of IDs representing an element's location in an
                                     interleaved hierarchy of elements.
        :param misc_data_id: The id for the specific piece of miscellaneous data we are looking for.

        :return Any: Returns a string or a Dict
        """

    @abstractmethod
    def get_colour(
        self, colour_id: str, combined_element_ids: Optional[List[str]] = None
    ) -> pygame.Color:
        """
        Uses data about a UI element and a specific ID to find a colour from our theme.

        :param combined_element_ids: A list of IDs representing an element's location in a
                                     hierarchy of elements.
        :param colour_id: The id for the specific colour we are looking for.
        :return pygame.Color: A pygame colour.
        """

    @abstractmethod
    def get_colour_or_gradient(
        self, colour_id: str, combined_ids: Optional[List[str]] = None
    ) -> Union[pygame.Color, IColourGradientInterface]:
        """
        Uses data about a UI element and a specific ID to find a colour, or a gradient,
        from our theme. Use this function if the UIElement can handle either type.

        :param combined_ids: A list of IDs representing an element's location in a
                             hierarchy of elements.
        :param colour_id: The id for the specific colour we are looking for.

        :return pygame.Color or ColourGradient: A colour or a gradient object.
        """

    @abstractmethod
    def load_theme(
        self, file_path: Union[str, PathLike, io.StringIO, PackageResource, dict]
    ):
        """
        Loads a theme, and currently, all associated data like fonts and images required
        by the theme.

        :param file_path: The location of the theme, or the theme data we want to load.

        """

    @abstractmethod
    def update_theming(self, new_theming_data: str, rebuild_all: bool = True):
        """
        Update theming data, via string - for the whole UI.

        :param new_theming_data:
        :param rebuild_all:
        :return:
        """

    @abstractmethod
    def update_single_element_theming(self, element_name: str, new_theming_data: str):
        """
        Update theming data, via string - for a single element.
        :param element_name:
        :param new_theming_data:
        :return:
        """

    @property
    @abstractmethod
    def shape_cache(self) -> SurfaceCache:
        """

        :return:
        """

    @shape_cache.setter
    @abstractmethod
    def shape_cache(self, new_cache: SurfaceCache):
        """

        :param new_cache:
        :return:
        """

    @abstractmethod
    def check_need_to_rebuild_data_manually_changed(self) -> bool:
        """
        Checks and resets a flag for whether we need to trigger a rebuild of all the UI elements after a manual
        change in the data.

        :return: A boolean that indicates whether we should rebuild or not.
        """

    @abstractmethod
    def set_locale(self, locale: str):
        """
        Set the locale used in the appearance theme.

        :param locale: a two-letter ISO country code.
        """

    @abstractmethod
    def get_shadow_generator(self) -> ShadowGenerator:
        """

        :return:
        """
