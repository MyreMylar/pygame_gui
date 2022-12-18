import json
import io
import os
import warnings

from contextlib import contextmanager
from typing import Union, List, Dict, Any, Iterable, Optional, Callable

import pygame

from pygame_gui.core.interfaces.font_dictionary_interface import IUIFontDictionaryInterface
from pygame_gui.core.interfaces.colour_gradient_interface import IColourGradientInterface
from pygame_gui.core.interfaces.appearance_theme_interface import IUIAppearanceThemeInterface
from pygame_gui.core.utility import create_resource_path, PackageResource
from pygame_gui.core.utility import ImageResource, SurfaceResource
from pygame_gui.core.ui_font_dictionary import UIFontDictionary
from pygame_gui.core.ui_shadow import ShadowGenerator
from pygame_gui.core.surface_cache import SurfaceCache
from pygame_gui.core.colour_gradient import ColourGradient
from pygame_gui.core.resource_loaders import IResourceLoader
from pygame_gui._constants import __colourNames__
from pygame_gui.core.colour_parser import parse_colour_or_gradient_string, get_commas_outside_enclosing_glyphs

import enum

# First try importlib
# Then importlib_resources
try:
    from importlib.resources import path, read_text
except ImportError:
    try:
        from importlib_resources import path, read_text
    except ImportError as no_import_lib:
        raise ImportError from no_import_lib




class UIAppearanceTheme(IUIAppearanceThemeInterface):
    """
    The Appearance Theme class handles all the data that styles and generally dictates the
    appearance of UI elements across the whole UI.

    The styling is split into four general areas:

    - colours - spelled in the British English fashion with a 'u'.
    - font - specifying a font to use for a UIElement where that is a relevant consideration.
    - images - describing any images to be used in a UIElement.
    - misc - covering all other types of data and stored as strings.

    To change the theming for the UI you normally specify a theme file when creating the UIManager.
    For more information on theme files see the specific documentation elsewhere.
    """

    def __init__(self, resource_loader: IResourceLoader, locale: str):

        self._resource_loader = resource_loader
        self._locale = locale
        # the base colours are the default colours all UI elements use if they
        # don't have a more specific colour defined for their element
        self.base_colours = {}

        # colours for specific elements stored by element id then colour id
        self.ui_element_colours = {}
        self.font_dict = UIFontDictionary(self._resource_loader, locale)
        self.shadow_generator = ShadowGenerator()
        self.shape_cache = SurfaceCache()

        self.unique_theming_ids = {}

        self.ui_element_fonts_info = {}
        self.ui_element_image_locs = {}
        self.ele_font_res = {}
        self.ui_element_image_surfaces = {}
        self.ui_element_misc_data = {}
        self.image_resources = {}  # type: Dict[str,ImageResource]
        self.surface_resources = {}  # type: Dict[str,SurfaceResource]

        self._theme_file_last_modified = None
        self._theme_file_path = None

        self._load_default_theme_file()

        self.st_cache_duration = 10.0
        self.st_cache_clear_timer = 0.0

        self.need_to_rebuild_data_manually_changed = False

    def _load_default_theme_file(self):
        """
        Loads the default theme file.
        """
        self.load_theme(PackageResource('pygame_gui.data', 'default_theme.json'))

    def get_font_dictionary(self) -> IUIFontDictionaryInterface:
        """
        Lets us grab the font dictionary, which is created by the theme object, so we can access
        it directly.

        :return: The font dictionary.
        """
        return self.font_dict

    def check_need_to_rebuild_data_manually_changed(self) -> bool:
        if self.need_to_rebuild_data_manually_changed:
            self.need_to_rebuild_data_manually_changed = False
            return True
        return False

    def update_theming(self, new_theming_data: str, rebuild_all: bool = True):
        # parse new_theming data
        theme_dict = json.loads(new_theming_data)
        self._parse_theme_data_from_json_dict(theme_dict)
        if rebuild_all:
            self.need_to_rebuild_data_manually_changed = True

    def update_single_element_theming(self, element_name: str, new_theming_data: str):
        element_theming_dict = json.loads(new_theming_data)

        self._parse_single_element_data(element_name, element_theming_dict)
        self._load_fonts()
        self._load_images()
        self._preload_shadow_edges()

    def check_need_to_reload(self) -> bool:
        """
        Check if we need to reload our theme file because it's been modified. If so, trigger a
        reload and return True so that the UIManager can trigger elements to rebuild from
        the theme data.

        :return bool: True if we need to reload elements because the theme data has changed.
        """
        if self._theme_file_path is None:
            return False

        need_to_reload = False
        try:
            if isinstance(self._theme_file_path, PackageResource):
                with path(self._theme_file_path.package,
                          self._theme_file_path.resource) as package_file_path:
                    stamp = os.stat(package_file_path).st_mtime
            else:
                stamp = os.stat(self._theme_file_path).st_mtime
        except(pygame.error, FileNotFoundError, OSError):
            need_to_reload = False
        else:
            if stamp != self._theme_file_last_modified:
                self._theme_file_last_modified = stamp
                self.reload_theming()
                need_to_reload = True

        return need_to_reload

    def update_caching(self, time_delta: float):
        """
        Updates the various surface caches.
        """
        if self.st_cache_clear_timer > self.st_cache_duration:
            self.st_cache_clear_timer = 0.0
            self.shadow_generator.clear_short_term_caches()
        else:
            self.st_cache_clear_timer += time_delta

        self.shape_cache.update()

    def reload_theming(self):
        """
        We need to load our theme file to see if anything expensive has changed, if so trigger
        it to reload/rebuild.
        """
        self.load_theme(self._theme_file_path)

    def _load_fonts(self):
        """
        Loads all fonts specified in our loaded theme.
        """
        for element_key, locale_font_info in self.ui_element_fonts_info.items():
            for locale_key, font_info in locale_font_info.items():
                if 'regular_path' in font_info:
                    regular_path = font_info['regular_path']
                    self.font_dict.add_font_path(font_info['name'],
                                                 regular_path,
                                                 font_info.get('bold_path', None),
                                                 font_info.get('italic_path', None),
                                                 font_info.get('bold_italic_path', None))
                elif 'regular_resource' in font_info:
                    bold_resource = None
                    italic_resource = None
                    bld_it_resource = None
                    reg_res_data = font_info['regular_resource']
                    regular_resource = PackageResource(package=reg_res_data['package'],
                                                       resource=reg_res_data['resource'])

                    if 'bold_resource' in font_info:
                        bold_res_data = font_info['bold_resource']
                        bold_resource = PackageResource(package=bold_res_data['package'],
                                                        resource=bold_res_data['resource'])
                    if 'italic_resource' in font_info:
                        italic_res_data = font_info['italic_resource']
                        italic_resource = PackageResource(package=italic_res_data['package'],
                                                          resource=italic_res_data['resource'])
                    if 'bold_italic_resource' in font_info:
                        bld_it_res_data = font_info['bold_italic_resource']
                        bld_it_resource = PackageResource(package=bld_it_res_data['package'],
                                                          resource=bld_it_res_data['resource'])

                    self.font_dict.add_font_path(font_info['name'],
                                                 regular_resource,
                                                 bold_resource,
                                                 italic_resource,
                                                 bld_it_resource)

                font_id = self.font_dict.create_font_id(font_info['size'],
                                                        font_info['name'],
                                                        font_info['bold'],
                                                        font_info['italic'])

                if font_id not in self.font_dict.loaded_fonts:
                    self.font_dict.preload_font(font_info['size'],
                                                font_info['name'],
                                                font_info['bold'],
                                                font_info['italic'])

                if element_key not in self.ele_font_res:
                    self.ele_font_res[element_key] = {}
                self.ele_font_res[element_key][locale_key] = self.font_dict.find_font_resource(
                    font_info['size'],
                    font_info['name'],
                    font_info['bold'],
                    font_info['italic'])

    def _load_images(self):
        """
        Loads all images in our loaded theme.
        """
        for element_key, image_ids_dict in self.ui_element_image_locs.items():
            if element_key not in self.ui_element_image_surfaces:
                self.ui_element_image_surfaces[element_key] = {}
            for image_id in image_ids_dict:
                image_resource_data = image_ids_dict[image_id]
                if image_resource_data['changed']:
                    image_resource = None
                    if 'package' in image_resource_data and 'resource' in image_resource_data:
                        image_resource = self._load_image_resource(image_resource_data)
                    elif 'path' in image_resource_data:
                        image_resource = self._load_image_from_path(image_resource_data)
                    else:
                        warnings.warn('Unable to find image with id: ' + str(image_id))

                    if image_resource is not None:
                        if 'sub_surface_rect' in image_resource_data:
                            surface_id = (image_resource.image_id +
                                          str(image_resource_data['sub_surface_rect']))
                            if surface_id in self.surface_resources:
                                surf_resource = self.surface_resources[surface_id]
                            else:
                                surf_resource = SurfaceResource(
                                    image_resource=image_resource,
                                    sub_surface_rect=image_resource_data['sub_surface_rect'])
                                self.surface_resources[surface_id] = surf_resource
                                if self._resource_loader.started():
                                    error = surf_resource.load()
                                    if error is not None:
                                        warnings.warn(str(error))
                                else:
                                    self._resource_loader.add_resource(surf_resource)
                        else:
                            surface_id = image_resource.image_id
                            if surface_id in self.surface_resources:
                                surf_resource = self.surface_resources[surface_id]
                            else:
                                surf_resource = SurfaceResource(image_resource=image_resource)
                                self.surface_resources[surface_id] = surf_resource
                                surf_resource.surface = surf_resource.image_resource.loaded_surface

                        self.ui_element_image_surfaces[element_key][image_id] = surf_resource

    def _load_image_from_path(self, res_data):
        resource_id = res_data['path']
        if resource_id in self.image_resources:
            image_resource = self.image_resources[resource_id]
        else:
            image_resource = ImageResource(resource_id, res_data['path'])
            if self._resource_loader.started():
                error = image_resource.load()
                if error is not None:
                    warnings.warn(str(error))
            else:
                self._resource_loader.add_resource(image_resource)

            self.image_resources[resource_id] = image_resource
        return image_resource

    def _load_image_resource(self, res_data):
        resource_id = (str(res_data['package']) + '/' + str(res_data['resource']))
        if resource_id in self.image_resources:
            image_resource = self.image_resources[resource_id]
        else:
            package_resource = PackageResource(res_data['package'], res_data['resource'])
            image_resource = ImageResource(resource_id, package_resource)
            if self._resource_loader.started():
                error = image_resource.load()
                if error is not None:
                    warnings.warn(str(error))
            else:
                self._resource_loader.add_resource(image_resource)
            self.image_resources[resource_id] = image_resource
        return image_resource

    def _preload_shadow_edges(self):
        """
        Looks through the theming data for any shadow edge combos we haven't loaded yet and
        tries to pre-load them. This helps stop the UI from having to create the complicated
        parts of the shadows dynamically which can be noticeably slow (e.g. waiting a second
        for a window to appear).

        For this to work correctly the theme file shouldn't contain any 'invalid' data that is
        later clamped by the UI, plus, it is helpful if any rounded rectangles that set a corner
        radius also set a shadow width at the same time.
        """
        for _, misc_data in self.ui_element_misc_data.items():

            shape = 'rectangle'
            shadow_width = 2
            shape_corner_radius = 2
            element_misc_data = misc_data
            if 'shape' in element_misc_data:
                shape = element_misc_data['shape']

            if 'shadow_width' in element_misc_data:
                try:
                    shadow_width = int(element_misc_data['shadow_width'])
                except ValueError:
                    shadow_width = 2
                    warnings.warn(
                        "Invalid value: " + element_misc_data['shadow_width'] +
                        " for shadow_width")

            if 'shape_corner_radius' in element_misc_data:
                try:
                    shape_corner_radius = int(element_misc_data['shape_corner_radius'])
                except ValueError:
                    shape_corner_radius = 2
                    warnings.warn(
                        "Invalid value: " +
                        misc_data['shape_corner_radius'] +
                        " for shape_corner_radius")

            if shape in ['rounded_rectangle', 'rectangle'] and shadow_width > 0:
                if ('shadow_width' in misc_data and
                        'shape_corner_radius' in misc_data):
                    shadow_id = str(shadow_width) + 'x' + str(shadow_width + shape_corner_radius)
                    if shadow_id not in self.shadow_generator.preloaded_shadow_corners:
                        self.shadow_generator.create_shadow_corners(shadow_width,
                                                                    shadow_width +
                                                                    shape_corner_radius)
                elif 'shadow_width' in misc_data:
                    # have a shadow width but no idea on the corners, try most common -
                    shadow_id_1 = str(shadow_width) + 'x' + str(2)
                    if shadow_id_1 not in self.shadow_generator.preloaded_shadow_corners:
                        self.shadow_generator.create_shadow_corners(shadow_width, 2)
                    shadow_id_2 = str(shadow_width) + 'x' + str(shadow_width)
                    if shadow_id_2 not in self.shadow_generator.preloaded_shadow_corners:
                        self.shadow_generator.create_shadow_corners(shadow_width, shadow_width)
                elif 'shape_corner_radius' in misc_data:
                    # have a corner radius but no idea on the shadow width, try most common -
                    shadow_id_1 = str(1) + 'x' + str(1 + shape_corner_radius)
                    if shadow_id_1 not in self.shadow_generator.preloaded_shadow_corners:
                        self.shadow_generator.create_shadow_corners(1, 1 + shape_corner_radius)
                    shadow_id_2 = str(2) + 'x' + str(2 + shape_corner_radius)
                    if shadow_id_2 not in self.shadow_generator.preloaded_shadow_corners:
                        self.shadow_generator.create_shadow_corners(2, 2 + shape_corner_radius)
                    shadow_id_3 = str(shape_corner_radius) + 'x' + str(shape_corner_radius)
                    if shadow_id_3 not in self.shadow_generator.preloaded_shadow_corners:
                        self.shadow_generator.create_shadow_corners(shape_corner_radius,
                                                                    shape_corner_radius)

    def _get_next_id_node(self, current_node: Union[Dict[str, Union[str, Dict]], None],
                          element_ids: List[str],
                          class_ids: List[Union[str, None]],
                          object_ids: List[Union[str, None]],
                          index: int,
                          tree_size: int,
                          combined_ids: List[str]):
        """
        Use a recursive algorithm to build up a list of IDs that describe a particular UI object
        to ever decreasing degrees of accuracy.

        We first iterate forward through the ID strings building up parent->child relationships
        and then unwind them backwards to create the final string IDs. We pick object IDs over
        class IDs, then class IDs over element IDs when available placing those IDs containing
        object IDs highest up in our list.

        :param current_node: The current 'node' we are at in the recursive algorithm.
        :param element_ids: A hierarchical list of all element IDs that apply to our element,
                            this includes parents.
        :param element_ids: A hierarchical list of all class IDs that apply to our element,
                            this includes parents.
        :param object_ids: A hierarchical list of all object IDs that apply to our element,
                           this includes parents.
        :param index: The current index in the two ID lists.
        :param tree_size: The size of both lists.
        :param combined_ids: The final list of combined IDs.
        """
        if index < tree_size:
            # add any Object IDs first...
            if (object_ids is not None
                    and index < len(object_ids)
                    and object_ids[index] is not None):
                next_node = {'id': object_ids[index], 'parent': current_node}
                self._get_next_id_node(next_node, element_ids, class_ids, object_ids,
                                       index + 1, tree_size, combined_ids)
            # then any class IDs...
            if (class_ids is not None
                    and index < len(class_ids)
                    and class_ids[index] is not None):
                next_node = {'id': class_ids[index], 'parent': current_node}
                self._get_next_id_node(next_node, element_ids, class_ids, object_ids,
                                       index + 1, tree_size, combined_ids)
            # Finally add the required element IDs.
            next_node_2 = {'id': element_ids[index], 'parent': current_node}
            self._get_next_id_node(next_node_2, element_ids, class_ids, object_ids, index + 1,
                                   tree_size, combined_ids)
        else:
            # unwind
            gathered_ids = []
            unwind_node = current_node
            while unwind_node is not None:
                gathered_ids.append(unwind_node['id'])
                unwind_node = unwind_node['parent']
            gathered_ids.reverse()
            combined_id = gathered_ids[0]
            for gathered_index in range(1, len(gathered_ids)):
                combined_id += '.'
                combined_id += gathered_ids[gathered_index]
            combined_ids.append(combined_id)

    def build_all_combined_ids(self, element_ids: Union[None, List[str]],
                               class_ids: Union[None, List[Union[str, None]]],
                               object_ids: Union[None, List[Union[str, None]]]) -> List[str]:
        """
        Construct a list of combined element ids from the element's various accumulated ids.

        :param element_ids: All the ids of elements this element is contained within.
        :param class_ids: All the ids of 'classes' that this element is contained within.
        :param object_ids: All the ids of objects this element is contained within.

        :return: A list of IDs that reference this element in order of decreasing specificity.
        """
        combined_id = str(element_ids).join(str(class_ids)).join(str(object_ids))
        if combined_id in self.unique_theming_ids:
            return self.unique_theming_ids[combined_id]

        combined_ids = []
        if object_ids is not None and element_ids is not None and class_ids is not None:
            if len(object_ids) != len(element_ids) or len(class_ids) != len(element_ids):
                raise ValueError("Object & class ID hierarchy is not equal "
                                 "in length to Element ID hierarchy"
                                 "Element IDs: " +
                                 str(element_ids) +
                                 "\nClass IDs: " +
                                 str(class_ids) + "\n"
                                 "\nObject IDs: " +
                                 str(object_ids) + "\n")
            if len(element_ids) != 0:
                self._get_next_id_node(None, element_ids, class_ids, object_ids,
                                       0, len(element_ids), combined_ids)

            current_ids = combined_ids[:]

            found_all_ids = False
            while not found_all_ids:
                if len(current_ids) > 0:
                    for index, current_id in enumerate(current_ids):
                        found_full_stop_index = current_id.find('.')
                        if found_full_stop_index == -1:
                            found_all_ids = True
                        else:
                            current_ids[index] = current_id[found_full_stop_index + 1:]
                            combined_ids.append(current_ids[index])
                else:
                    found_all_ids = True

        self.unique_theming_ids[combined_id] = combined_ids
        return combined_ids

    def get_image(self, image_id: str, combined_element_ids: List[str]) -> pygame.surface.Surface:
        """
        Will raise an exception if no image with the ids specified is found. UI elements that have
        an optional image display will need to handle the exception.

        :param combined_element_ids: A list of IDs representing an element's location in a
                                     hierarchy of elements.
        :param image_id: The id identifying the particular image spot in the UI we are looking for
                         an image to add to.

        :return: A pygame.surface.Surface
        """

        for combined_element_id in combined_element_ids:
            if (combined_element_id in self.ui_element_image_surfaces and
                    image_id in self.ui_element_image_surfaces[combined_element_id]):
                return self.ui_element_image_surfaces[combined_element_id][image_id].surface

        raise LookupError('Unable to find any image with id: ' + str(image_id) +
                          ' with combined_element_ids: ' + str(combined_element_ids))

    def get_font_info(self, combined_element_ids: List[str]) -> Dict[str, Any]:
        """
        Uses some data about a UIElement to get font data as dictionary

        :param combined_element_ids: A list of IDs representing an element's location in a
                                     interleaved hierarchy of elements.

        :return dictionary: Data about the font requested
        """
        for combined_element_id in combined_element_ids:
            if combined_element_id in self.ui_element_fonts_info:
                if self._locale in self.ui_element_fonts_info[combined_element_id]:
                    return self.ui_element_fonts_info[combined_element_id][self._locale]
                else:
                    return self.ui_element_fonts_info[combined_element_id]['en']

        return self.font_dict.default_font.info

    def get_font(self, combined_element_ids: List[str]) -> pygame.freetype.Font:
        """
        Uses some data about a UIElement to get a font object.

        :param combined_element_ids: A list of IDs representing an element's location in a
                                     interleaved hierarchy of elements.

        :return pygame.freetype.Font: A pygame font object.
        """
        # set the default font as the final fall back
        font = self.font_dict.get_default_font()

        for combined_element_id in combined_element_ids:
            if combined_element_id in self.ele_font_res:
                if self._locale in self.ele_font_res[combined_element_id]:
                    return self.ele_font_res[combined_element_id][self._locale].loaded_font
                else:
                    return self.ele_font_res[combined_element_id]['en'].loaded_font

        return font

    def get_misc_data(self, misc_data_id: str, combined_element_ids: List[str]) -> Union[str, Dict]:
        """
        Uses data about a UI element and a specific ID to try and find a piece of miscellaneous
        theming data. Raises an exception if it can't find the data requested, UI elements
        requesting optional data will need to handle this exception.

        :param combined_element_ids: A list of IDs representing an element's location in a
                                     hierarchy of elements.
        :param misc_data_id: The id for the specific piece of miscellaneous data we are looking for.

        :return Any: Returns a string or a Dict
        """

        for combined_element_id in combined_element_ids:
            if (combined_element_id in self.ui_element_misc_data and
                    misc_data_id in self.ui_element_misc_data[combined_element_id]):
                return self.ui_element_misc_data[combined_element_id][misc_data_id]

        raise LookupError('Unable to find any data with id: ' + str(misc_data_id) +
                          ' with combined_element_ids: ' + str(combined_element_ids))

    def get_colour(self, colour_id: str, combined_element_ids: List[str] = None) -> pygame.Color:
        """
        Uses data about a UI element and a specific ID to find a colour from our theme.

        :param combined_element_ids: A list of IDs representing an element's location in a
                                     hierarchy of elements.
        :param colour_id: The id for the specific colour we are looking for.
        :return pygame.Color: A pygame colour.
        """
        colour_or_gradient = self.get_colour_or_gradient(colour_id, combined_element_ids)
        if isinstance(colour_or_gradient, ColourGradient):
            gradient = colour_or_gradient
            colour = gradient.colour_1
        elif isinstance(colour_or_gradient, pygame.Color):
            colour = colour_or_gradient
        else:
            colour = pygame.Color('#000000')
        return colour

    def get_colour_or_gradient(self, colour_id: str,
                               combined_ids: List[str] = None) -> Union[pygame.Color,
                                                                        IColourGradientInterface]:
        """
        Uses data about a UI element and a specific ID to find a colour, or a gradient,
        from our theme. Use this function if the UIElement can handle either type.

        :param combined_ids: A list of IDs representing an element's location in a
                                     hierarchy of elements.
        :param colour_id: The id for the specific colour we are looking for.

        :return pygame.Color or ColourGradient: A colour or a gradient object.
        """
        if combined_ids is not None:
            for combined_id in combined_ids:
                if (combined_id in self.ui_element_colours and
                        colour_id in self.ui_element_colours[combined_id]):
                    return self.ui_element_colours[combined_id][colour_id]

        # then fall back on default colour with same id
        if colour_id in self.base_colours:
            return self.base_colours[colour_id]

        # if all else fails find a colour with the most similar id words
        colour_parts = colour_id.split('_')
        best_fit_key_count = 0
        best_fit_colour = self.base_colours['normal_bg']
        for key, colour in self.base_colours.items():
            key_words = key.split('_')
            count = sum(el in colour_parts for el in key_words)
            if count > best_fit_key_count:
                best_fit_key_count = count
                best_fit_colour = colour
        return best_fit_colour

    @staticmethod
    @contextmanager
    def _opened_w_error(filename: Any, mode: str = "rt", encoding: str = "utf-8"):
        """
        Wraps file open in some exception handling.
        """
        if not isinstance(filename, io.StringIO):
            try:
                file = open(filename, mode, encoding=encoding)
            except IOError as err:
                yield None, err
            else:
                try:
                    yield file, None
                finally:
                    file.close()
        else:
            file = filename
            try:
                yield file, None
            finally:
                file.close()

    def load_theme(self, file_path: Union[str, os.PathLike, io.StringIO, PackageResource]):
        """
        Loads a theme file, and currently, all associated data like fonts and images required
        by the theme.

        :param file_path: The path to the theme we want to load.
        """
        if isinstance(file_path, PackageResource):
            used_file_path = io.StringIO(read_text(file_path.package, file_path.resource))
            self._theme_file_path = file_path
            with path(file_path.package, file_path.resource) as package_file_path:
                self._theme_file_last_modified = os.stat(package_file_path).st_mtime

        elif not isinstance(file_path, io.StringIO):
            self._theme_file_path = create_resource_path(file_path)
            try:
                self._theme_file_last_modified = os.stat(self._theme_file_path).st_mtime
            except(pygame.error, FileNotFoundError, OSError):
                self._theme_file_last_modified = 0
            used_file_path = self._theme_file_path
        else:
            used_file_path = file_path

        with self._opened_w_error(used_file_path, 'rt') as (theme_file, error):
            if error:
                warnings.warn("Failed to open theme file at path:" + str(file_path))
                load_success = False
            else:
                try:
                    theme_dict = json.load(theme_file)
                except json.decoder.JSONDecodeError:
                    warnings.warn("Failed to load current theme file, check syntax", UserWarning)
                    load_success = False
                else:
                    load_success = True

                if load_success:
                    self._parse_theme_data_from_json_dict(theme_dict)

    def _parse_theme_data_from_json_dict(self, theme_dict):
        for element_name in theme_dict.keys():
            if element_name == 'defaults':
                self._load_colour_defaults_from_theme(theme_dict)
            else:
                self._load_prototype(element_name, theme_dict)
                element_theming = theme_dict[element_name]
                self._parse_single_element_data(element_name, element_theming)

        self._load_fonts()  # save to trigger load with the same data as it won't do anything
        self._load_images()
        self._preload_shadow_edges()

    def _parse_single_element_data(self, element_name, element_theming):
        for data_type in element_theming:
            if data_type == 'font':
                file_dict = element_theming[data_type]
                if isinstance(file_dict, list):
                    for item in file_dict:
                        self._load_element_font_data_from_theme(item,
                                                                element_name)
                else:
                    self._load_element_font_data_from_theme(file_dict,
                                                            element_name)

            if data_type == 'colours':
                self._load_element_colour_data_from_theme(data_type,
                                                          element_name,
                                                          element_theming)

            elif data_type == 'images':
                self._load_element_image_data_from_theme(data_type,
                                                         element_name,
                                                         element_theming)

            elif data_type == 'misc':
                self._load_element_misc_data_from_theme(data_type,
                                                        element_name,
                                                        element_theming)

    def _load_prototype(self, element_name: str, theme_dict: Dict[str, Any]):
        """
        Loads a prototype theme block for our current theme element if any exists. Prototype
        blocks must be above their 'production' elements in the theme file.

        :param element_name: The element to load a prototype for.
        :param theme_dict: The theme file dictionary.
        """
        if 'prototype' not in theme_dict[element_name]:
            return
        prototype_id = theme_dict[element_name]['prototype']

        found_prototypes = []

        if prototype_id in self.ui_element_fonts_info:
            prototype_font = self.ui_element_fonts_info[prototype_id]
            if element_name not in self.ui_element_fonts_info:
                self.ui_element_fonts_info[element_name] = {}

            for locale_key in prototype_font:
                if locale_key not in self.ui_element_fonts_info:
                    self.ui_element_fonts_info[element_name][locale_key] = {}

                for data_key in prototype_font[locale_key]:
                    self.ui_element_fonts_info[element_name][locale_key][data_key] = (
                        prototype_font[locale_key][data_key])
            found_prototypes.append(prototype_font)

        if prototype_id in self.ui_element_colours:
            prototype_colours = self.ui_element_colours[prototype_id]
            if element_name not in self.ui_element_colours:
                self.ui_element_colours[element_name] = {}
            for col_key in prototype_colours:
                self.ui_element_colours[element_name][col_key] = prototype_colours[col_key]
            found_prototypes.append(prototype_colours)

        if prototype_id in self.ui_element_image_locs:
            prototype_images = self.ui_element_image_locs[prototype_id]
            if element_name not in self.ui_element_image_locs:
                self.ui_element_image_locs[element_name] = {}
            for image_key in prototype_images:
                self.ui_element_image_locs[element_name][image_key] = prototype_images[image_key]
            found_prototypes.append(prototype_images)

        if prototype_id in self.ui_element_misc_data:
            prototype_misc = self.ui_element_misc_data[prototype_id]
            if element_name not in self.ui_element_misc_data:
                self.ui_element_misc_data[element_name] = {}
            for misc_key in prototype_misc:
                self.ui_element_misc_data[element_name][misc_key] = prototype_misc[misc_key]
            found_prototypes.append(prototype_misc)

        if not found_prototypes:
            warnings.warn("Failed to find any prototype data with ID: " + prototype_id, UserWarning)

    def _load_element_misc_data_from_theme(self,
                                           data_type: str,
                                           element_name: str,
                                           element_theming: Dict[str, Any]):
        """
        Load miscellaneous theming data direct from the theme file's data dictionary into our
        misc data dictionary.

        Data is stored by it's combined element ID and an ID specific to the type of data it is.

        :param data_type: The type of misc data as described by a string.
        :param element_name: The theming element ID that this data belongs to.
        :param element_theming: The data dictionary from the theming file to load data from.
        """
        if element_name not in self.ui_element_misc_data:
            self.ui_element_misc_data[element_name] = {}
        misc_dict = element_theming[data_type]
        for misc_data_key in misc_dict:
            if isinstance(misc_dict[misc_data_key], (dict, str)):
                self.ui_element_misc_data[element_name][misc_data_key] = misc_dict[misc_data_key]

    def _load_element_image_data_from_theme(self,
                                            data_type: str,
                                            element_name: str,
                                            element_theming: Dict[str, Any]):
        """
        Load image theming data direct from the theme file's data dictionary into our image
        data dictionary.

        Data is stored by it's combined element ID and an ID specific to the type of data it is.

        :param data_type: The type of image data as described by a string.
        :param element_name: The theming element ID that this data belongs to.
        :param element_theming: The data dictionary from the theming file to load data from.
        """
        if element_name not in self.ui_element_image_locs:
            self.ui_element_image_locs[element_name] = {}
        loaded_img_dict = element_theming[data_type]
        for image_key in loaded_img_dict:
            if image_key not in self.ui_element_image_locs[element_name]:
                self.ui_element_image_locs[element_name][image_key] = {}
                self.ui_element_image_locs[element_name][image_key]['changed'] = True
            else:
                self.ui_element_image_locs[element_name][image_key]['changed'] = False

            img_res_dict = self.ui_element_image_locs[element_name][image_key]
            if 'package' in loaded_img_dict[image_key] and 'resource' in loaded_img_dict[image_key]:
                package = str(loaded_img_dict[image_key]['package'])
                resource = str(loaded_img_dict[image_key]['resource'])
                if 'package' in img_res_dict and package != img_res_dict['package']:
                    img_res_dict['changed'] = True
                if 'resource' in img_res_dict and resource != img_res_dict['resource']:
                    img_res_dict['changed'] = True
                img_res_dict['package'] = package
                img_res_dict['resource'] = resource
            elif 'path' in loaded_img_dict[image_key]:
                image_path = str(loaded_img_dict[image_key]['path'])
                if 'path' in img_res_dict and image_path != img_res_dict['path']:
                    img_res_dict['changed'] = True
                img_res_dict['path'] = image_path
            if 'sub_surface_rect' in loaded_img_dict[image_key]:
                rect_list = str(loaded_img_dict[image_key]['sub_surface_rect']).strip().split(',')
                if len(rect_list) == 4:
                    try:
                        top_left = (int(rect_list[0].strip()), int(rect_list[1].strip()))
                        size = (int(rect_list[2].strip()), int(rect_list[3].strip()))
                    except (ValueError, TypeError):
                        rect = pygame.Rect((0, 0), (10, 10))
                        warnings.warn("Unable to create subsurface rectangle from string: "
                                      "" + loaded_img_dict[image_key]['sub_surface_rect'])
                    else:
                        rect = pygame.Rect(top_left, size)

                    if ('sub_surface_rect' in img_res_dict and
                            rect != img_res_dict['sub_surface_rect']):
                        img_res_dict['changed'] = True
                    img_res_dict['sub_surface_rect'] = rect

    def _load_element_colour_data_from_theme(self,
                                             data_type: str,
                                             element_name: str,
                                             element_theming: Dict[str, Any]):
        """
        Load colour/gradient theming data direct from the theme file's data dictionary into our
        colour data dictionary.

        Data is stored by it's combined element ID and an ID specific to the type of data it is.

        :param data_type: The type of colour data as described by a string.
        :param element_name: The theming element ID that this data belongs to.
        :param element_theming: The data dictionary from the theming file to load data from.
        """

        if element_name not in self.ui_element_colours:
            self.ui_element_colours[element_name] = {}
        colours_dict = element_theming[data_type]
        for colour_key in colours_dict:
            colour = self._load_colour_or_gradient_from_theme(colours_dict, colour_key)
            self.ui_element_colours[element_name][colour_key] = colour

    def _load_element_font_data_from_theme(self,
                                           file_dict,
                                           element_name: str):
        """
        Load font theming data direct from the theme file's data dictionary into our font
        data dictionary. Data is stored by it's combined element ID and an ID specific to the
        type of data it is.

        :param element_name: The theming element ID that this data belongs to.
        :param file_dict: The file dictionary from the theming file to load data from.
        """

        if element_name not in self.ui_element_fonts_info:
            self.ui_element_fonts_info[element_name] = {}

        locale = 'en'
        if 'locale' in file_dict:
            locale = file_dict['locale']

        if locale not in self.ui_element_fonts_info[element_name]:
            self.ui_element_fonts_info[element_name][locale] = {}

        font_info_dict = self.ui_element_fonts_info[element_name][locale]
        font_info_dict['name'] = file_dict['name']
        try:
            font_info_dict['size'] = int(file_dict['size'])
        except ValueError:
            default_size = self.font_dict.default_font.size
            font_info_dict['size'] = default_size
        if 'bold' in file_dict:
            try:
                font_info_dict['bold'] = bool(int(file_dict['bold']))
            except ValueError:
                font_info_dict['bold'] = False
        else:
            font_info_dict['bold'] = False
        if 'italic' in file_dict:
            try:
                font_info_dict['italic'] = bool(int(file_dict['italic']))
            except ValueError:
                font_info_dict['italic'] = False
        else:
            font_info_dict['italic'] = False
        if 'regular_path' in file_dict:
            font_info_dict['regular_path'] = file_dict['regular_path']
        if 'bold_path' in file_dict:
            font_info_dict['bold_path'] = file_dict['bold_path']
        if 'italic_path' in file_dict:
            font_info_dict['italic_path'] = file_dict['italic_path']
        if 'bold_italic_path' in file_dict:
            bold_italic_path = file_dict['bold_italic_path']
            font_info_dict['bold_italic_path'] = bold_italic_path

        if 'regular_resource' in file_dict:
            resource_data = {'package': file_dict['regular_resource']['package'],
                             'resource': file_dict['regular_resource']['resource']}
            font_info_dict['regular_resource'] = resource_data
        if 'bold_resource' in file_dict:
            resource_data = {'package': file_dict['bold_resource']['package'],
                             'resource': file_dict['bold_resource']['resource']}
            font_info_dict['bold_resource'] = resource_data
        if 'italic_resource' in file_dict:
            resource_data = {'package': file_dict['italic_resource']['package'],
                             'resource': file_dict['italic_resource']['resource']}
            font_info_dict['italic_resource'] = resource_data
        if 'bold_italic_resource' in file_dict:
            resource_data = {'package': file_dict['bold_italic_resource']['package'],
                             'resource': file_dict['bold_italic_resource']['resource']}
            font_info_dict['bold_italic_resource'] = resource_data

    def _load_colour_defaults_from_theme(self, theme_dict: Dict[str, Any]):
        """
        Load the default colours for this theme.

        :param theme_dict: The data dictionary from the theming file to load data from.
        """
        for data_type in theme_dict['defaults']:
            if data_type == 'colours':
                colours_dict = theme_dict['defaults'][data_type]
                for colour_key in colours_dict:
                    colour = self._load_colour_or_gradient_from_theme(colours_dict,
                                                                      colour_key)
                    self.base_colours[colour_key] = colour


    @staticmethod
    def _load_colour_or_gradient_from_theme(theme_colours_dictionary: Dict[str, str],
                                            colour_id: str) -> Union[pygame.Color, ColourGradient]:
        """
        Load a single colour, or gradient, from theming file data.

        :param theme_colours_dictionary: Part of the theming file data relating to colours.
        :param colour_id: The ID of the colour or gradient to load.
        """
        # loaded_colour_or_gradient = None
        string_data = theme_colours_dictionary[colour_id]
        colour: Optional[Union[pygame.Color, ColourGradient]] = parse_colour_or_gradient_string(string_data)
        if colour is None:
            if len(get_commas_outside_enclosing_glyphs(string_data)) > 0: # Was probably meant to be a gradient
                warnings.warn("Invalid gradient: " + string_data + " for id:" + colour_id + " in theme file")
            else:
                if string_data.startswith("#"):
                    warnings.warn("Colour hex code: " + string_data + " for id:" + colour_id + " invalid in theme file")
                else:
                    warnings.warn("Colour: " + string_data + " for id:" + colour_id + " invalid in theme file" )
            return pygame.Color("#000000")
        return colour

    def set_locale(self, locale: str):
        """
        Set the locale used in the appearance theme.

        :param locale: a two letter ISO country code.
        """
        self._locale = locale
