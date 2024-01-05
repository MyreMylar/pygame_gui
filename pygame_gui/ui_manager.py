import os
from typing import Tuple, List, Dict, Union, Set, Optional

import pygame
import i18n

from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.core.interfaces.appearance_theme_interface import IUIAppearanceThemeInterface
from pygame_gui.core.interfaces import IUIElementInterface, IUIContainerInterface
from pygame_gui.core.interfaces.window_stack_interface import IUIWindowStackInterface
from pygame_gui.core.interfaces.tool_tip_interface import IUITooltipInterface

from pygame_gui.core.ui_appearance_theme import UIAppearanceTheme
from pygame_gui.core.ui_window_stack import UIWindowStack
from pygame_gui.core.ui_container import UIContainer
from pygame_gui.core.resource_loaders import IResourceLoader, BlockingThreadedResourceLoader
from pygame_gui.core.utility import PackageResource, get_default_manager, set_default_manager
from pygame_gui.core.layered_gui_group import LayeredGUIGroup
from pygame_gui.core import ObjectID

from pygame_gui.elements import UITooltip


class UIManager(IUIManagerInterface):
    """
    The UI Manager class helps keep track of all the moving parts in the pygame_gui system.

    Before doing anything else with pygame_gui create a UIManager and remember to update it every
    frame.

    :param window_resolution: window resolution.
    :param theme_path: relative file path to theme.
    :param enable_live_theme_updates: Lets the theme update in-game after we edit the theme file
    """

    def __init__(self,
                 window_resolution: Tuple[int, int],
                 theme_path: Optional[Union[str, PackageResource]] = None,
                 enable_live_theme_updates: bool = True,
                 resource_loader: Optional[IResourceLoader] = None,
                 starting_language: str = 'en',
                 translation_directory_paths: Optional[List[str]] = None):

        if get_default_manager() is None:
            set_default_manager(self)
        # Translation stuff
        self._locale = starting_language
        root_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        translations_path = os.path.normpath(os.path.join(root_path,
                                                          'pygame_gui/data/translations/'))
        i18n.set('file_format', 'json')
        i18n.load_path.append(translations_path)
        if translation_directory_paths is not None:
            for path in translation_directory_paths:
                # check this is a valid path
                i18n.load_path.append(path)

        i18n.set('locale', self._locale)

        # Threaded loading
        if resource_loader is None:
            auto_load = True
            self.resource_loader = BlockingThreadedResourceLoader()
        else:
            auto_load = False
            self.resource_loader = resource_loader

        self.window_resolution = window_resolution
        self.ui_theme = UIAppearanceTheme(self.resource_loader, self._locale)
        if theme_path is not None:
            self.ui_theme.load_theme(theme_path)

        self.universal_empty_surface = pygame.surface.Surface((0, 0),
                                                              flags=pygame.SRCALPHA,
                                                              depth=32)
        self.ui_group = LayeredGUIGroup()

        self.focused_set = None
        self.root_container = None
        self.root_container = UIContainer(pygame.Rect((0, 0), self.window_resolution),
                                          self, starting_height=1,
                                          container=None, parent_element=None,
                                          object_id='#root_container')
        self.root_container.set_focus_set(None)

        self.ui_window_stack = UIWindowStack(self.window_resolution, self.root_container)

        self.live_theme_updates = enable_live_theme_updates
        self.theme_update_acc = 0.0
        self.theme_update_check_interval = 1.0

        self.mouse_double_click_time = 0.5
        self.mouse_position = (0, 0)
        self.mouse_pos_scale_factor = [1.0, 1.0]

        self.visual_debug_active = False

        self.resizing_window_cursors = None
        self._load_default_cursors()
        self.active_user_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)
        self._active_cursor = self.active_user_cursor
        self.text_input_hovered = False
        self.hovering_any_ui_element = False

        if auto_load:
            self.resource_loader.start()
            # If we are using a blocking loader this will only return when loading is complete
            self.resource_loader.update()

    def get_double_click_time(self) -> float:
        """
        Returns time between clicks that counts as a double click.

        :return: A float, time measured in seconds.
        """
        return self.mouse_double_click_time

    def get_root_container(self) -> IUIContainerInterface:
        """
        Returns the 'root' container. The one all UI elements are placed in by default if they are
        not placed anywhere else, fills the whole OS/pygame window.

        :return: A container.
        """
        return self.root_container

    def get_theme(self) -> IUIAppearanceThemeInterface:
        """
        Gets the theme so the data in it can be accessed.

        :return: The theme data used by this UIManager
        """
        return self.ui_theme

    def get_sprite_group(self) -> pygame.sprite.LayeredDirty:
        """
        Gets the sprite group used by the entire UI to keep it in the correct order for drawing and
        processing input.

        :return: The UI's sprite group.
        """
        return self.ui_group

    def get_window_stack(self) -> IUIWindowStackInterface:
        """
        The UIWindowStack organises any windows in the UI Manager so that they are correctly sorted
        and move windows we interact with to the top of the stack.

        :return: The stack of windows.
        """
        return self.ui_window_stack

    def get_shadow(self, size: Tuple[int, int], shadow_width: int = 2,
                   shape: str = 'rectangle', corner_radius: int = 2) -> pygame.surface.Surface:
        """
        Returns a 'shadow' surface scaled to the requested size.

        :param size: The size of the object we are shadowing + it's shadow.
        :param shadow_width: The width of the shadowed edge.
        :param shape: The shape of the requested shadow.
        :param corner_radius: The radius of the shadow corners if this is a rectangular shadow.
        :return: A shadow as a pygame Surface.
        """
        return self.ui_theme.shadow_generator.find_closest_shadow_scale_to_size(size,
                                                                                shadow_width,
                                                                                shape,
                                                                                corner_radius)

    def set_window_resolution(self, window_resolution: Tuple[int, int]):
        """
        Sets the window resolution.

        :param window_resolution: the resolution to set.
        """
        self.window_resolution = window_resolution
        self.ui_window_stack.window_resolution = window_resolution
        self.root_container.set_dimensions(window_resolution)

    def clear_and_reset(self):
        """
        Clear all existing windows and the root container, which should get rid of all created UI
        elements. We then recreate the UIWindowStack and the root container.
        """
        self.root_container.kill()
        # need to reset to None before recreating otherwise the old container will linger around.
        self.root_container = None
        self.root_container = UIContainer(pygame.Rect((0, 0), self.window_resolution),
                                          self, starting_height=1,
                                          container=None, parent_element=None,
                                          object_id='#root_container')
        self.ui_window_stack = UIWindowStack(self.window_resolution, self.root_container)

    def process_events(self, event: pygame.event.Event):
        """
        This is the top level method through which all input to UI elements is processed and
        reacted to.

        One of the key things it controls is the currently 'focused' element of which there
        can be only one at a time. It also manages 'consumed events' these events will not be
        passed on to elements below them in the GUI hierarchy and helps us stop buttons underneath
        windows from receiving input.

        :param event:  pygame.event.Event - the event to process.
        :return: A boolean indicating whether the event was consumed.
        """
        consumed_event = False
        sorting_consumed_event = False
        sorted_layers = sorted(self.ui_group.layers(), reverse=True)
        for layer in sorted_layers:
            sprites_in_layer = self.ui_group.get_sprites_from_layer(layer)
            if not sorting_consumed_event:
                windows_in_layer = [window for window in sprites_in_layer
                                    if 'window' in window.element_ids[-1]]
                for window in windows_in_layer:
                    if not sorting_consumed_event:
                        sorting_consumed_event = window.check_clicked_inside_or_blocking(event)
            if not consumed_event:
                for ui_element in sprites_in_layer:
                    if ui_element.visible:
                        # Only process events for visible elements - ignore hidden elements
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            mouse_x, mouse_y = self.calculate_scaled_mouse_position(event.pos)
                            if ui_element.hover_point(mouse_x, mouse_y):
                                self.set_focus_set(ui_element.get_focus_set())

                        consumed_event = ui_element.process_event(event)
                        if consumed_event:
                            # Generally clicks should only be handled by the top layer of whatever
                            # GUI thing we are  clicking on. I am trusting UIElments to decide
                            # whether they need to consume the events they respond to. Hopefully
                            # this is not a mistake.

                            break
        return consumed_event

    def update(self, time_delta: float):
        """
        From here all our UI elements are updated and which element is currently 'hovered' is
        checked; which means the mouse pointer is overlapping them. This is managed centrally so
        we aren't ever overlapping two elements at once.

        It also updates the shape cache to continue storing already created elements shapes in the
        long term cache, in case we need them later.

        Finally, if live theme updates are enabled, it checks to see if the theme file has been
        modified and triggers all the UI elements to rebuild if it has.

        :param time_delta: The time passed since the last call to update, in seconds.
        """

        if self.live_theme_updates:
            self.theme_update_acc += time_delta
            if self.theme_update_acc > self.theme_update_check_interval:
                self.theme_update_acc = 0.0
                if self.ui_theme.check_need_to_reload():
                    for sprite in self.ui_group.sprites():
                        sprite.rebuild_from_changed_theme_data()

        if self.ui_theme.check_need_to_rebuild_data_manually_changed():
            for sprite in self.ui_group.sprites():
                sprite.rebuild_from_changed_theme_data()

        self.ui_theme.update_caching(time_delta)

        self._update_mouse_position()
        self._handle_hovering(time_delta)

        self.set_text_input_hovered(False)  # reset the text hovered status each loop

        self.ui_group.update(time_delta)

        # handle mouse cursors
        if self.text_input_hovered:
            new_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_IBEAM)
            if new_cursor != self._active_cursor:
                self._active_cursor = new_cursor
                try:
                    pygame.mouse.set_cursor(self._active_cursor)
                except pygame.error:
                    pass

        any_window_edge_hovered = False
        for window in self.ui_window_stack.stack:
            if window.should_use_window_edge_resize_cursor():
                any_window_edge_hovered = True
                new_cursor = self.resizing_window_cursors[window.get_hovering_edge_id()]

                if new_cursor != self._active_cursor:
                    self._active_cursor = new_cursor
                    try:
                        pygame.mouse.set_cursor(self._active_cursor)
                    except pygame.error:
                        pass

        if (not any_window_edge_hovered and not self.text_input_hovered and
                self._active_cursor != self.active_user_cursor):
            self._active_cursor = self.active_user_cursor
            try:
                pygame.mouse.set_cursor(self._active_cursor)
            except pygame.error:
                pass

    def _handle_hovering(self, time_delta):
        hover_handled = False
        sorted_layers = sorted(self.ui_group.layers(), reverse=True)
        for layer in sorted_layers:
            for ui_element in self.ui_group.get_sprites_from_layer(layer):
                if ui_element.visible:
                    # Only check hover for visible elements - ignore hidden elements
                    # we need to check hover even after already found what we are hovering
                    # so we can unhover previously hovered stuff
                    element_is_hovered = ui_element.check_hover(time_delta, hover_handled)
                    if element_is_hovered and ui_element != self.root_container:
                        hover_handled = True
                        self.hovering_any_ui_element = True
                    elif element_is_hovered and ui_element == self.root_container:
                        # if we are just hovering over the root container
                        # set 'hovering any' to False
                        self.hovering_any_ui_element = False

    def get_mouse_position(self) -> Tuple[int, int]:
        """
        Wrapping pygame mouse position so we can mess with it.
        """
        return self.mouse_position

    def draw_ui(self, window_surface: pygame.surface.Surface):
        """
        Draws all the UI elements on the screen. Generally you want this to be after the rest of
        your game sprites have been drawn.

        If you want to do something particularly unusual with drawing you may have to write your
        own UI manager.

        :param window_surface: The screen or window surface on which we are going to draw all of
         our UI Elements.

        """
        self.ui_group.draw(window_surface)

    def add_font_paths(self, font_name: str, regular_path: str, bold_path: str = None,
                       italic_path: str = None, bold_italic_path: str = None):
        """
        Add file paths for custom fonts you want to use in the UI. For each font name you add you
        can specify font files for different styles. Fonts with designed styles tend to render a
        lot better than fonts that are forced to make use of pygame's bold and italic styling
        effects, so if you plan to use bold and italic text at small sizes - find fonts with these
        styles available as separate files.

        The font name you specify here can be used to choose the font in the blocks of HTML-subset
        formatted text, available in some of the UI elements like the UITextBox.

        It is recommended that you also pre-load any fonts you use at an appropriate moment in your
        project rather than letting the library dynamically load them when they are required. That
        is because dynamic loading of large font files can cause UI elements with a lot of font
        usage to appear rather slowly as they are waiting for the fonts they need to load.

        :param font_name: The name of the font that will be used to reference it elsewhere in
                          the GUI.
        :param regular_path: The path of the font file for this font with no styles applied.
        :param bold_path: The path of the font file for this font with just bold style applied.
        :param italic_path: The path of the font file for this font with just italic style applied.
        :param bold_italic_path: The path of the font file for this font with bold & italic style
               applied.

        """
        self.get_theme().get_font_dictionary().add_font_path(font_name,
                                                             regular_path,
                                                             bold_path,
                                                             italic_path,
                                                             bold_italic_path)

    def preload_fonts(self, font_list: List[Dict[str, Union[str, int, float]]]):
        """
        It's a good idea to pre-load the exact fonts your program uses during the loading phase of
        your program. By default the pygame_gui library will still work, but will spit out reminder
        warnings when you haven't done this. Loading fonts on the fly will slow down the apparent
        responsiveness when creating UI elements that use a lot of different fonts.

        To pre-load custom fonts, or to use custom fonts at all (i.e. ones that aren't the default
        'fira_code' font) you must first add the paths to the files for those fonts, then load the
        specific fonts with a list of font descriptions in a dictionary form like so:

            ``{'name': 'fira_code', 'point_size': 12, 'style': 'bold_italic', 'antialiased': 1}``

        You can specify size either in pygame.Font point sizes with 'point_size', or in HTML style
        sizes with 'html_size'. Style options are:

        - ``'regular'``
        - ``'italic'``
        - ``'bold'``
        - ``'bold_italic'``

        The name parameter here must match the one you used when you added the file paths.

        :param font_list: A list of font descriptions in dictionary format as described above.

        """
        for font in font_list:
            name = 'fira_code'
            bold = False
            italic = False
            size = 14
            antialiased = True
            if 'name' in font:
                name = font['name']
            if 'style' in font:
                if 'bold' in font['style']:
                    bold = True
                if 'italic' in font['style']:
                    italic = True
            if 'antialiased' in font:
                antialiased = bool(int(font['antialiased']))
            if 'html_size' in font:
                font_dict = self.ui_theme.get_font_dictionary()
                size = font_dict.convert_html_to_point_size(font['html_size'])
            elif 'point_size' in font:
                size = font['point_size']

            self.ui_theme.get_font_dictionary().preload_font(size, name, bold, italic, False, antialiased)

    def print_unused_fonts(self):
        """
        Helps you identify which pre-loaded fonts you are actually still using in your project
        after you've fiddled around with the text a lot by printing out a list of fonts that have
        not been used yet at the time this function is called.

        Of course if you don't run the code path in which a particular font is used before calling
        this function then it won't be of much use, so take it's results under advisement rather
        than as gospel.

        """
        self.ui_theme.get_font_dictionary().print_unused_loaded_fonts()

    def get_focus_set(self):
        return self.focused_set

    def set_focus_set(self, focus: Union[IUIElementInterface, Set[IUIElementInterface]]):
        """
        Set a set of element as the focused set.

        :param focus: The set of element to focus on.
        """
        if focus is self.focused_set:
            return
        if self.focused_set is not None:
            for item in self.focused_set:
                if isinstance(focus, set):
                    if item not in focus:
                        item.unfocus()
                    # do nothing if the item is also in new focus set
                else:
                    item.unfocus()
            self.focused_set = None

        if self.focused_set is None:
            if focus is not None:
                if isinstance(focus, IUIElementInterface):
                    self.focused_set = focus.get_focus_set()
                elif isinstance(focus, set):
                    self.focused_set = focus
            else:
                self.focused_set = None

            if self.focused_set is not None:
                for item in self.focused_set:
                    if not item.is_focused:
                        item.focus()

    def set_visual_debug_mode(self, is_active: bool):
        """
        Loops through all our UIElements to turn visual debug mode on or off. Also calls
        print_layer_debug()

        :param is_active: True to activate visual debug and False to turn it off.
        """
        if self.visual_debug_active and not is_active:
            self.visual_debug_active = False
            for layer in self.ui_group.layers():
                for element in self.ui_group.get_sprites_from_layer(layer):
                    element.set_visual_debug_mode(self.visual_debug_active)
        elif not self.visual_debug_active and is_active:
            self.visual_debug_active = True
            # preload the debug font if it's not already loaded
            self.get_theme().get_font_dictionary().ensure_debug_font_loaded()

            for layer in self.ui_group.layers():
                for element in self.ui_group.get_sprites_from_layer(layer):
                    element.set_visual_debug_mode(self.visual_debug_active)

            # Finally print a version of the current layers to the console:
            self.print_layer_debug()

    def print_layer_debug(self):
        """
        Print some formatted information on the current state of the UI Layers.

        Handy for debugging layer problems.
        """
        for layer in self.ui_group.layers():
            print("Layer: " + str(layer))
            print("-----------------------")
            for element in self.ui_group.get_sprites_from_layer(layer):
                if element.element_ids[-1] == 'container':
                    print(str(element.most_specific_combined_id) +
                          ': thickness - ' + str(element.layer_thickness))
                else:
                    print(str(element.most_specific_combined_id))
            print(' ')

    def set_active_cursor(self, cursor: pygame.cursors.Cursor):
        """
        This is for users of the library to set the currently active cursor, it will be currently
        only be overridden by the resizing cursors.

        The expected input is a pygame.cursors.Cursor::

            manager.set_active_cursor(pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW))

        """

        self.active_user_cursor = cursor

    def get_universal_empty_surface(self) -> pygame.surface.Surface:
        """
        Sometimes we want to hide sprites or just have sprites with no visual component, when we
        do we can just use this empty surface to save having lots of empty surfaces all over memory.

        :return: An empty, and therefore invisible pygame.surface.Surface
        """
        return self.universal_empty_surface

    def create_tool_tip(self,
                        text: str,
                        position: Tuple[int, int],
                        hover_distance: Tuple[int, int],
                        parent_element: IUIElementInterface,
                        object_id: ObjectID,
                        *,
                        wrap_width: Optional[int] = None,
                        text_kwargs: Optional[Dict[str, str]] = None) -> IUITooltipInterface:
        """
        Creates a tool tip ands returns it. Have hidden this away in the manager so we can call it
        from other UI elements and create tool tips without creating cyclical import problems.

        :param text: The tool tips text, can utilise the HTML subset used in all UITextBoxes.
        :param position: The screen position to create the tool tip for.
        :param hover_distance: The distance we should hover away from our target position.
        :param parent_element: The UIElement that spawned this tool tip.
        :param object_id: the object_id of the tooltip.
        :param wrap_width: an optional width for the tool tip, will overwrite any value from the theme file.
        :param text_kwargs: a dictionary of variable arguments to pass to the translated string
                            useful when you have multiple translations that need variables inserted
                            in the middle.

        :return: A tool tip placed somewhere on the screen.
        """
        tool_tip = UITooltip(text, hover_distance, self, text_kwargs=text_kwargs,
                             parent_element=parent_element, object_id=object_id, wrap_width=wrap_width)
        tool_tip.find_valid_position(pygame.math.Vector2(position[0], position[1]))
        return tool_tip

    def _update_mouse_position(self):
        """
        Wrapping pygame mouse position so we can mess with it.
        """
        self.mouse_position = self.calculate_scaled_mouse_position(pygame.mouse.get_pos())

    def calculate_scaled_mouse_position(self, position: Tuple[int, int]) -> Tuple[int, int]:
        """
        Scaling an input mouse position by a scale factor.
        """
        return (int(self.mouse_pos_scale_factor[0] * position[0]),
                int(self.mouse_pos_scale_factor[1] * position[1]))

    def _load_default_cursors(self):
        """
        'Loads' the default cursors we use in the GUI for resizing windows. No actual files are
        opened as this is all string date compiled into pygame cursor images.

        """
        # cursors for resizing windows
        self.resizing_window_cursors = {'xl': pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_SIZEWE),
                                        'xr': pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_SIZEWE),
                                        'yt': pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_SIZENS),
                                        'yb': pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_SIZENS),
                                        'xy': pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_SIZENWSE),
                                        'yx': pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_SIZENESW)}

    def set_locale(self, locale: str):
        self._locale = locale
        i18n.set('locale', self._locale)
        self.ui_theme.set_locale(self._locale)
        self.ui_theme.get_font_dictionary().set_locale(self._locale)
        for sprite in self.ui_group.sprites():
            if isinstance(sprite, IUIElementInterface):
                sprite.on_locale_changed()

    def get_locale(self):
        return self._locale

    def set_text_input_hovered(self, hovering_text_input: bool):
        self.text_input_hovered = hovering_text_input

    def get_hovering_any_element(self) -> bool:
        return self.hovering_any_ui_element
