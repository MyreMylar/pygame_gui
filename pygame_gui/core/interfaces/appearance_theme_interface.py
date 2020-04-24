import io

from abc import ABCMeta, abstractmethod
from typing import List, Union, Dict, Any
try:
    from os import PathLike  # for Python 3.6
except ImportError:
    PathLike = None

import pygame

from pygame_gui.core.interfaces.font_dictionary_interface import IUIFontDictionaryInterface
from pygame_gui.core.interfaces.colour_gradient_interface import IColourGradientInterface


class IUIAppearanceThemeInterface(metaclass=ABCMeta):
    """
    A meta class that defines the interface that a UI Appearance Theme uses.

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
    def build_all_combined_ids(self,
                               element_ids: Union[None, List[str]],
                               object_ids: Union[None, List[Union[str, None]]]) -> List[str]:
        """
        Construct a list of combined element ids from the element's various accumulated ids.

        :param element_ids: All the ids of elements this element is contained within.
        :param object_ids: All the ids of objects this element is contained within.

        :return: A list of IDs that reference this element in order of decreasing specificity.
        """

    @abstractmethod
    def get_image(self, combined_element_ids: List[str], image_id: str) -> pygame.Surface:
        """
        Will raise an exception if no image with the ids specified is found. UI elements that have
        an optional image display will need to handle the exception.

        :param combined_element_ids: A list of IDs representing an element's location in a
                                     hierarchy of elements.
        :param image_id: The id identifying the particular image spot in the UI we are looking for
                         an image to add to.

        :return: A pygame.Surface
        """

    @abstractmethod
    def get_font_info(self, combined_element_ids: List[str]) -> Dict[str, Any]:
        """
        Uses some data about a UIElement to get font data as dictionary

        :param combined_element_ids: A list of IDs representing an element's location in a
                                     interleaved hierarchy of elements.

        :return dictionary: Data about the font requested
        """

    @abstractmethod
    def get_font(self, combined_element_ids: List[str]) -> pygame.font.Font:
        """
        Uses some data about a UIElement to get a font object.

        :param combined_element_ids: A list of IDs representing an element's location in a
                                     interleaved hierarchy of elements.

        :return pygame.font.Font: A pygame font object.
        """

    @abstractmethod
    def get_misc_data(self, combined_element_ids: List[str], misc_data_id: str) -> Union[str, Dict]:
        """
        Uses data about a UI element and a specific ID to try and find a piece of miscellaneous
        theming data. Raises an exception if it can't find the data requested, UI elements
        requesting optional data will need to handle this exception.

        :param combined_element_ids: A list of IDs representing an element's location in a
                                     interleaved hierarchy of elements.
        :param misc_data_id: The id for the specific piece of miscellaneous data we are looking for.

        :return Any: Returns a string or a Dict
        """

    @abstractmethod
    def get_colour(self, combined_element_ids: List[str], colour_id: str) -> pygame.Color:
        """
        Uses data about a UI element and a specific ID to find a colour from our theme.

        :param combined_element_ids: A list of IDs representing an element's location in a
                                     hierarchy of elements.
        :param colour_id: The id for the specific colour we are looking for.
        :return pygame.Color: A pygame colour.
        """

    @abstractmethod
    def get_colour_or_gradient(self, combined_element_ids: List[str],
                               colour_id: str) -> Union[pygame.Color, IColourGradientInterface]:
        """
        Uses data about a UI element and a specific ID to find a colour, or a gradient,
        from our theme. Use this function if the UIElement can handle either type.

        :param combined_element_ids: A list of IDs representing an element's location in a
                                     hierarchy of elements.
        :param colour_id: The id for the specific colour we are looking for.

        :return pygame.Color or ColourGradient: A colour or a gradient object.
        """

    @abstractmethod
    def load_theme(self, file_path: Union[str, PathLike, io.StringIO]):
        """
        Loads a theme file, and currently, all associated data like fonts and images required
        by the theme.

        :param file_path: The path to the theme we want to load.

        """
