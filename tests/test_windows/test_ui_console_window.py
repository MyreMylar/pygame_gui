import os
import pygame
import pytest

from tests.shared_comparators import compare_surfaces

from pygame_gui.ui_manager import UIManager
from pygame_gui.windows.ui_console_window import UIConsoleWindow


class TestUIConsoleWindow:
    def test_creation(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        pygame.display.set_mode((800, 600))
        UIConsoleWindow(
            rect=pygame.rect.Rect((0, 0), (700, 500)),
            manager=default_ui_manager)

    def test_command_entry_finished(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        pygame.display.set_mode((800, 600))
        console_window = UIConsoleWindow(rect=pygame.rect.Rect((0, 0), (300, 200)),
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

        assert console_window.log.appended_text == logged_line
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

        assert console_window.log.appended_text == logged_lines
        assert console_window.command_entry.get_text() == ''

        # add a lot of text
        console_window.command_entry.set_text('More text to fill up the log, blah, blah, blah, blah. '
                                              'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
                                              ' Nunc accumsan aliquet massa a pharetra. Nam ultricies '
                                              'non est in ultrices. Pellentesque blandit vulputate augue'
                                              ' ac porta. Maecenas porta ex ut erat semper, a efficitur '
                                              'lectus vehicula. Proin finibus id tortor eu finibus. '
                                              'Pellentesque sodales est semper sem condimentum, quis '
                                              'ultricies odio ultrices. Nulla aliquet est sed blandit '
                                              'congue. Sed quam justo, consequat ac orci et, pharetra '
                                              'elementum massa. Ut pulvinar varius nulla, eu elementum '
                                              'nisi tempor quis. Nulla ante sapien, elementum tincidunt '
                                              'nulla a, blandit lobortis urna. Ut ut tortor lacinia, '
                                              'malesuada nunc faucibus, maximus est. Etiam ornare '
                                              'molestie nisi eu condimentum. Class aptent taciti '
                                              'sociosqu ad litora torquent per conubia nostra, '
                                              'per inceptos himenaeos. Suspendisse ut euismod lorem, '
                                              'eget consequat velit.')

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

        # add a lot of text again
        console_window.command_entry.set_text('More text to fill up the log, blah, blah, blah, blah. '
                                              'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
                                              ' Nunc accumsan aliquet massa a pharetra. Nam ultricies '
                                              'non est in ultrices. Pellentesque blandit vulputate augue'
                                              ' ac porta. Maecenas porta ex ut erat semper, a efficitur '
                                              'lectus vehicula. Proin finibus id tortor eu finibus. '
                                              'Pellentesque sodales est semper sem condimentum, quis '
                                              'ultricies odio ultrices. Nulla aliquet est sed blandit '
                                              'congue. Sed quam justo, consequat ac orci et, pharetra '
                                              'elementum massa. Ut pulvinar varius nulla, eu elementum '
                                              'nisi tempor quis. Nulla ante sapien, elementum tincidunt '
                                              'nulla a, blandit lobortis urna. Ut ut tortor lacinia, '
                                              'malesuada nunc faucibus, maximus est. Etiam ornare '
                                              'molestie nisi eu condimentum. Class aptent taciti '
                                              'sociosqu ad litora torquent per conubia nostra, '
                                              'per inceptos himenaeos. Suspendisse ut euismod lorem, '
                                              'eget consequat velit.')

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

    def test_log_prefix(self, _init_pygame, _display_surface_return_none, default_ui_manager):
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

        assert console_window.log.appended_text == logged_line

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

        assert console_window.log.appended_text == logged_lines

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

        assert console_window.log.appended_text == logged_lines

    def test_add_output_line_to_log(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        console_window = UIConsoleWindow(rect=pygame.rect.Rect((0, 0), (700, 500)),
                                         manager=default_ui_manager)

        console_window.add_output_line_to_log('line to add')

        assert console_window.log.appended_text == '<b>line to add</b><br>'

        console_window.add_output_line_to_log('second line to add, no line break',
                                              is_bold=False,
                                              remove_line_break=True)

        assert console_window.log.appended_text == ('<b>line to add</b><br>'
                                                    'second line to add, no line break')

        console_window.add_output_line_to_log('third <i>line</i> to add, escape html',
                                              escape_html=True)

        assert console_window.log.appended_text == ('<b>line to add</b><br>'
                                                    'second line to add, no line break'
                                                    '<b>third &lt;i&gt;line&lt;/i&gt; to add,'
                                                    ' escape html</b><br>')

    def test_scroll_log_with_arrow_keys(self, _init_pygame, _display_surface_return_none, default_ui_manager):
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

    def test_clear_log(self, _init_pygame, _display_surface_return_none, default_ui_manager):
        console_window = UIConsoleWindow(rect=pygame.rect.Rect((0, 0), (700, 500)),
                                         manager=default_ui_manager)

        console_window.command_entry.set_text('<b>A line of text to log</b>')

        console_window.add_output_line_to_log('line to add')

        console_window.clear_log()

        assert console_window.logged_commands_above == []
        assert console_window.current_logged_command is None
        assert console_window.logged_commands_below == []


if __name__ == '__main__':
    pytest.console_main()
