import os
import pygame
import pytest

from tests.shared_comparators import compare_surfaces

from pygame_gui.ui_manager import UIManager
from pygame_gui.windows.ui_console_window import UIConsoleWindow

try:
    # mouse button constants not defined in pygame 1.9.3
    pygame.BUTTON_LEFT
    pygame.BUTTON_MIDDLE
    pygame.BUTTON_RIGHT
except AttributeError:
    pygame.BUTTON_LEFT = 1
    pygame.BUTTON_MIDDLE = 2
    pygame.BUTTON_RIGHT = 3


class TestUIConsoleWindow:
    def test_creation(self, _init_pygame, default_ui_manager,
                      _display_surface_return_none):

        UIConsoleWindow(
            rect=pygame.rect.Rect((0, 0), (700, 500)),
            manager=default_ui_manager)

    def test_command_entry_finished(self, _init_pygame, default_ui_manager,
                                    _display_surface_return_none):
        console_window = UIConsoleWindow(rect=pygame.rect.Rect((0, 0), (700, 500)),
                                         manager=default_ui_manager)

        console_window.command_entry.set_text('<b>A line of text to log</b>')

        event_data = {'button': pygame.BUTTON_LEFT,
                      'pos': console_window.command_entry.rect.center}
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_data))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP, event_data))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYDOWN,
                                                             {'key': pygame.K_RETURN}))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYUP,
                                                             {'key': pygame.K_RETURN}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        logged_line = console_window.log_prefix + '&lt;b&gt;A line of text to log&lt;/b&gt;<br>'

        assert console_window.log.html_text == logged_line
        assert console_window.command_entry.get_text() == ''

        console_window.set_logged_commands_escape_html(should_escape=False)
        console_window.command_entry.set_text('<b>A second line of text to log</b>')

        event_data = {'button': pygame.BUTTON_LEFT,
                      'pos': console_window.command_entry.rect.center}
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_data))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP, event_data))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYDOWN,
                                                             {'key': pygame.K_RETURN}))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYUP,
                                                             {'key': pygame.K_RETURN}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        logged_lines = (console_window.log_prefix + '&lt;b&gt;A line of text to log&lt;/b&gt;<br>' +
                        console_window.log_prefix + '<b>A second line of text to log</b><br>')

        assert console_window.log.html_text == logged_lines
        assert console_window.command_entry.get_text() == ''

    def test_log_prefix(self, _init_pygame, default_ui_manager,
                        _display_surface_return_none):
        console_window = UIConsoleWindow(rect=pygame.rect.Rect((0, 0), (700, 500)),
                                         manager=default_ui_manager)

        console_window.set_log_prefix('++ ')
        console_window.command_entry.set_text('A line of text to log')

        event_data = {'button': pygame.BUTTON_LEFT,
                      'pos': console_window.command_entry.rect.center}
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_data))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP, event_data))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYDOWN,
                                                             {'key': pygame.K_RETURN}))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYUP,
                                                             {'key': pygame.K_RETURN}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        logged_line = '++ A line of text to log<br>'

        assert console_window.log.html_text == logged_line

        console_window.set_log_prefix('-- ')

        console_window.command_entry.set_text('A second line of text to log')

        event_data = {'button': pygame.BUTTON_LEFT,
                      'pos': console_window.command_entry.rect.center}
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_data))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP, event_data))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYDOWN,
                                                             {'key': pygame.K_RETURN}))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYUP,
                                                             {'key': pygame.K_RETURN}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        logged_lines = '++ A line of text to log<br>-- A second line of text to log<br>'

        assert console_window.log.html_text == logged_lines

        console_window.restore_default_prefix()

        console_window.command_entry.set_text('A third line of text to log')

        event_data = {'button': pygame.BUTTON_LEFT,
                      'pos': console_window.command_entry.rect.center}
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_data))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP, event_data))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYDOWN,
                                                             {'key': pygame.K_RETURN}))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYUP,
                                                             {'key': pygame.K_RETURN}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        logged_lines = ('++ A line of text to log<br>'
                        '-- A second line of text to log<br>'
                        '> A third line of text to log<br>')

        assert console_window.log.html_text == logged_lines

    def test_add_output_line_to_log(self, _init_pygame, default_ui_manager,
                                    _display_surface_return_none):
        console_window = UIConsoleWindow(rect=pygame.rect.Rect((0, 0), (700, 500)),
                                         manager=default_ui_manager)

        console_window.add_output_line_to_log('line to add')

        assert console_window.log.html_text == '<b>line to add</b><br>'

        console_window.add_output_line_to_log('second line to add, no line break',
                                              is_bold=False,
                                              remove_line_break=True)

        assert console_window.log.html_text == ('<b>line to add</b><br>'
                                                'second line to add, no line break')

        console_window.add_output_line_to_log('third <i>line</i> to add, escape html',
                                              escape_html=True)

        assert console_window.log.html_text == ('<b>line to add</b><br>'
                                                'second line to add, no line break'
                                                '<b>third &lt;i&gt;line&lt;/i&gt; to add,'
                                                ' escape html</b><br>')

    def test_scroll_log_with_arrow_keys(self, _init_pygame, default_ui_manager,
                                        _display_surface_return_none):
        console_window = UIConsoleWindow(rect=pygame.rect.Rect((0, 0), (700, 500)),
                                         manager=default_ui_manager)

        console_window.command_entry.set_text('A first command')

        event_data = {'button': pygame.BUTTON_LEFT,
                      'pos': console_window.command_entry.rect.center}
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_data))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP, event_data))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYDOWN,
                                                             {'key': pygame.K_RETURN}))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYUP,
                                                             {'key': pygame.K_RETURN}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        console_window.command_entry.set_text('A second command')

        event_data = {'button': pygame.BUTTON_LEFT,
                      'pos': console_window.command_entry.rect.center}
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_data))
        default_ui_manager.process_events(pygame.event.Event(pygame.MOUSEBUTTONUP, event_data))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYDOWN,
                                                             {'key': pygame.K_RETURN}))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYUP,
                                                             {'key': pygame.K_RETURN}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert console_window.command_entry.get_text() == ""

        default_ui_manager.process_events(pygame.event.Event(pygame.KEYDOWN,
                                                             {'key': pygame.K_UP}))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYUP,
                                                             {'key': pygame.K_UP}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert console_window.command_entry.get_text() == 'A second command'

        default_ui_manager.process_events(pygame.event.Event(pygame.KEYDOWN,
                                                             {'key': pygame.K_UP}))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYUP,
                                                             {'key': pygame.K_UP}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert console_window.command_entry.get_text() == 'A first command'

        default_ui_manager.process_events(pygame.event.Event(pygame.KEYDOWN,
                                                             {'key': pygame.K_DOWN}))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYUP,
                                                             {'key': pygame.K_DOWN}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert console_window.command_entry.get_text() == 'A second command'

        default_ui_manager.process_events(pygame.event.Event(pygame.KEYDOWN,
                                                             {'key': pygame.K_UP}))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYUP,
                                                             {'key': pygame.K_UP}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert console_window.command_entry.get_text() == 'A first command'

        default_ui_manager.process_events(pygame.event.Event(pygame.KEYDOWN,
                                                             {'key': pygame.K_BACKSPACE}))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYUP,
                                                             {'key': pygame.K_BACKSPACE}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert console_window.command_entry.get_text() == 'A first comman'

        default_ui_manager.process_events(pygame.event.Event(pygame.KEYDOWN,
                                                             {'key': pygame.K_UP}))
        default_ui_manager.process_events(pygame.event.Event(pygame.KEYUP,
                                                             {'key': pygame.K_UP}))

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        for event in pygame.event.get():
            default_ui_manager.process_events(event)

        assert console_window.command_entry.get_text() == 'A second command'


if __name__ == '__main__':
    pytest.console_main()

