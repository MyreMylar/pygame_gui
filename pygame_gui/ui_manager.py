import pygame
from typing import Tuple, List, Dict, Union

from pygame_gui.core.ui_appearance_theme import UIAppearanceTheme
from pygame_gui.core.ui_window_stack import UIWindowStack
from pygame_gui.core.ui_window import UIWindow
from pygame_gui.core.ui_element import UIElement


class UIManager:
    """
    The UI Manager class helps keep track of all the moving parts in the pygame_gui system.

    Before doing anything else with pygame_gui create a UIManager and remember to update it every frame.
    """

    def __init__(self, window_resolution: Tuple[int, int], theme_path: str = None, enable_live_theme_updates=True):
        self.window_resolution = window_resolution
        self.ui_theme = UIAppearanceTheme()
        if theme_path is not None:
            self.ui_theme.load_theme(theme_path)
        self.ui_group = pygame.sprite.LayeredUpdates()

        self.select_focused_element = None
        self.last_focused_vertical_scrollbar = None

        self.ui_window_stack = UIWindowStack(self.window_resolution)
        UIWindow(pygame.Rect((0, 0), self.window_resolution), self, ['root_window'])

        self.live_theme_updates = enable_live_theme_updates
        self.theme_update_acc = 0.0
        self.theme_update_check_interval = 1.0

    def get_theme(self) -> UIAppearanceTheme:
        """
        Gets the theme so the data in it can be accessed.
        :return: UIAppearanceTheme - the theme data used by this UIManager
        """
        return self.ui_theme

    def get_sprite_group(self) -> pygame.sprite.LayeredUpdates:
        """
        Gets the sprite group used by the entire UI to keep it in the correct order for drawing and processing input.
        :return : pygame.sprite.LayeredUpdates -
        """
        return self.ui_group

    def get_window_stack(self) -> UIWindowStack:
        """
        The UIWindowStack organises any windows in the UI Manager so that they are correctly sorted and move windows
        we interact with to the top of the stack.
        :return: UIWindowStack
        """
        return self.ui_window_stack

    def get_shadow(self, size: Tuple[int, int], shadow_width: int = 2,
                   shape: str = 'rectangle', corner_radius: int = 2) -> pygame.Surface:
        """
        Returns a 'shadow' surface scaled to the requested size.


        :param size: The size of the object we are shadowing + it's shadow.
        :param shadow_width: The width of the shadowed edge.
        :param shape: The shape of the requested shadow
        :param corner_radius: The radius of the shadow corners if this is a rectangular shadow.
        :return: A shadow.
        """
        return self.ui_theme.shadow_generator.find_closest_shadow_scale_to_size(size, shadow_width,
                                                                                shape, corner_radius)

    def set_window_resolution(self, window_resolution):
        self.window_resolution = window_resolution

    def clear_and_reset(self):
        """
        Clear all existing windows, including the root window, which should get rid of all created UI elements.
        We then recreate the UIWindowStack and the root window.
        """
        self.ui_window_stack.clear()
        self.ui_window_stack = UIWindowStack(self.window_resolution)
        UIWindow(pygame.Rect((0, 0), self.window_resolution), self, ['root_window'])

    def process_events(self, event: pygame.event.Event):
        """
        This is the top level method through which all input to UI elements is processed and reacted to.

        One of the key things it controls is the currently 'focused' or 'selected' element of which there
        can be only one at a time.

        :param event:  pygame.event.Event - the event to process.
        """
        event_handled = False
        window_sorting_event_handled = False
        sorted_layers = sorted(self.ui_group.layers(), reverse=True)
        for layer in sorted_layers:
            sprites_in_layer = self.ui_group.get_sprites_from_layer(layer)
            # a little bit of code to pop windows we start messing with to the front
            if not window_sorting_event_handled:
                windows_in_layer = [window for window in sprites_in_layer if (
                        'window' in window.element_ids[-1]) and (self.ui_window_stack.get_root_window() is not window)]
                for window in windows_in_layer:
                    if not window_sorting_event_handled:
                        window_sorting_event_handled = window.check_clicked_inside(event)
            if not event_handled:
                for ui_element in sprites_in_layer:
                    if not event_handled:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:
                                mouse_x, mouse_y = event.pos
                                if ui_element.rect.collidepoint(mouse_x, mouse_y):
                                    if ui_element is not self.select_focused_element:
                                        self.unselect_focus_element()
                                        self.select_focus_element(ui_element)

                        event_handled = ui_element.process_event(event)

    def update(self, time_delta: float):
        """
        From here all our UI elements are updated and which element is currently 'hovered' is checked; which means
        the mouse pointer is overlapping them. This is managed centrally so we aren't ever overlapping two elements at
        once.

        It also updates the shape cache to continue storing already created elements shapes in the long term cache, in
        case we need them later.

        Finally, if live theme updates are enabled, it checks to see if the theme file has been modified and triggers
        all the UI elements to rebuild if it has.

        :param time_delta: The time passed since the last call to update, in seconds.
        """

        if self.live_theme_updates:
            self.theme_update_acc += time_delta
            if self.theme_update_acc > self.theme_update_check_interval:
                self.theme_update_acc = 0.0
                if self.ui_theme.check_need_to_reload():
                    for sprite in self.ui_group.sprites():
                        sprite.rebuild_from_changed_theme_data()

        self.ui_theme.update_shape_cache()

        hover_handled = False
        sorted_layers = sorted(self.ui_group.layers(), reverse=True)
        for layer in sorted_layers:
            for ui_element in self.ui_group.get_sprites_from_layer(layer):
                element_handled_hover = ui_element.check_hover(time_delta, hover_handled)
                if element_handled_hover:
                    hover_handled = True

        self.ui_group.update(time_delta)

    def draw_ui(self, window_surface: pygame.Surface):
        """
        Draws all the UI elements on the screen. Generally you want this to be after the rest of your game sprites
        have been drawn.

        If you want to do something particularly unusual with drawing you may have to write your own UI manager.

        :param window_surface: The screen or window surface on which we are going to draw all of our UI Elements.

        """
        self.ui_group.draw(window_surface)

    def add_font_paths(self, font_name: str, regular_path: str, bold_path: str = None,
                       italic_path: str = None, bold_italic_path: str = None):
        """
        Add file paths for custom fonts you want to use in the UI. For each font name you add you can specify
        font files for different styles. Fonts with designed styles tend to render a lot better than fonts that are
        forced to make use of pygame's bold and italic styling effects, so if you plan to use bold and italic text
        at small sizes - find fonts with these styles available as separate files.

        The font name you specify here can be used to choose the font in the blocks of HTML-subset formatted text,
        available in some of the UI elements like the UITextBox.

        It is recommended that you also pre-load any fonts you use at an appropriate moment in your project
        rather than letting the library dynamically load them when they are required. That is because dynamic loading
        of large font files can cause UI elements with a lot of font usage to appear rather slowly as they are waiting
        for the fonts they need to load.

        :param font_name: The name of the font that will be used to reference it elsewhere in the GUI.
        :param regular_path: The path of the font file for this font with no styles applied.
        :param bold_path: The path of the font file for this font with just bold style applied.
        :param italic_path: The path of the font file for this font with just italic style applied.
        :param bold_italic_path: The path of the font file for this font with bold & italic style applied.

        """
        self.get_theme().get_font_dictionary().add_font_path(font_name,
                                                             regular_path,
                                                             bold_path,
                                                             italic_path,
                                                             bold_italic_path)

    def preload_fonts(self, font_list: List[Dict[str, Union[str, int, float]]]):
        """
        It's a good idea to pre-load the exact fonts your program uses during the loading phase of your program.
        By default the pygame_gui library will still work, but will spit out reminder warnings when you haven't
        done this. Loading fonts on the fly will slow down the apparent responsiveness when creating UI elements
        that use a lot of different fonts.

        To pre-load custom fonts, or to use custom fonts at all (i.e. ones that aren't the default 'fira_code' font)
        you must first add the paths to the files for those fonts, then load the specific fonts with a list of font
        descriptions in a dictionary form like so:

        code:`{'name': 'fira_code', 'point_size': 12, 'style': 'bold_italic'}`

        You can specify size either in pygame.Font point sizes with 'point_size', or in HTML style sizes with
        'html_size'. Style options are:

        - 'regular'
        - 'italic'
        - 'bold'
        - 'bold_italic'

        The name parameter here must match the one you used when you added the file paths.

        :param font_list: A list of font descriptions in dictionary format as described above.

        """
        for font in font_list:
            name = 'fira_code'
            bold = False
            italic = False
            size = 14
            if 'name' in font:
                name = font['name']
            if 'style' in font:
                if 'bold' in font['style']:
                    bold = True
                if 'italic' in font['style']:
                    italic = True
            if 'html_size' in font:
                size = self.ui_theme.get_font_dictionary().convert_html_size_to_point_size(font['html_size'])
            elif 'point_size' in font:
                size = font['point_size']

            self.ui_theme.get_font_dictionary().preload_font(size, name, bold, italic)

    def print_unused_fonts(self):
        """
        Helps you identify which pre-loaded fonts you are actually still using in your project after you've
        fiddled around with the text a lot by printing out a list of fonts that have not been used yet at the
        time this function is called.

        Of course if you don't run the code path in which a particular font is used before calling this function
        then it won't be of much use, so take it's results under advisement rather than as gospel.

        """
        self.ui_theme.get_font_dictionary().print_unused_loaded_fonts()

    def unselect_focus_element(self):
        """
        Unselect and clear the currently focused element.
        """
        if self.select_focused_element is not None:
            self.select_focused_element.unselect()
            self.select_focused_element = None

    def select_focus_element(self, ui_element: UIElement):
        """
        Set an element as the focused element.

        If the element is a scroll bar we also keep track of that.

        :param ui_element: The element to focus on.
        """
        if self.select_focused_element is None:
            self.select_focused_element = ui_element
            self.select_focused_element.select()

            if 'vertical_scroll_bar' in self.select_focused_element.element_ids:
                self.last_focused_vertical_scrollbar = self.select_focused_element

    def clear_last_focused_from_vert_scrollbar(self, vert_scrollbar):
        """
        Clears the last scrollbar that we used.

        :param vert_scrollbar: A scrollbar UIElement.
        """
        if vert_scrollbar is self.last_focused_vertical_scrollbar:
            self.last_focused_vertical_scrollbar = None

    def get_last_focused_vert_scrollbar(self):
        """
        Gets the last scrollbar that we used.

        :return: A UIElement.
        """
        return self.last_focused_vertical_scrollbar
