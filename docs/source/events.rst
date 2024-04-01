.. _events:

GUI events
===========

Some of the UI Elements produce a :py:func:`pygame.Event <pygame:pygame.event.Event>` when they are interacted with. These events
all follow a common structure that looks something like this:

 - **'type'** : An id for the specific event that has happened. e.g. 'pygame_gui.UI_BUTTON_PRESSED'
 - **'ui_element'** : The UI element that fired this event.
 - **'ui_object_id'** : The most unique ID that applies to the UI element that fired this event. e.g. 'hud_window.#sell_button'

Though some of the events also have additional data relevant to that event.

Event list
----------

A list of all the different events by element.

:class:`UIButton <pygame_gui.elements.UIButton>` - UI_BUTTON_PRESSED
....................................................................

Fired when a user presses a button by clicking on it with a mouse, and releasing the mouse button while still
hovering over it.

 - **'type'** : pygame_gui.UI_BUTTON_PRESSED
 - **'ui_element'** : The :class:`UIButton <pygame_gui.elements.UIButton>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the button that fired this event.
 - **'mouse_button'** : The mouse button that did the pressing (pygame.BUTTON_LEFT etc).
                        You have to enable button events for buttons other than the left mouse button which is
                        enabled by default.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
         if event.type == pygame_gui.UI_BUTTON_PRESSED:
             if event.ui_element == test_button:
                 print('Test button pressed')

:class:`UIButton <pygame_gui.elements.UIButton>` - UI_BUTTON_START_PRESS
........................................................................

Fired when a user first presses down a button by clicking on it with a mouse. This is fired before you release the
mouse button.

 - **'type'** : pygame_gui.UI_BUTTON_START_PRESS
 - **'ui_element'** : The :class:`UIButton <pygame_gui.elements.UIButton>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the button that fired this event.
 - **'mouse_button'** : The mouse button that did the pressing (pygame.BUTTON_LEFT etc).
                        You have to enable button events for buttons other than the left mouse button which is
                        enabled by default.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
         if event.type == pygame_gui.UI_BUTTON_PRESSED:
             if event.ui_element == test_button:
                 print('Test button pressed')



:class:`UIButton <pygame_gui.elements.UIButton>` - UI_BUTTON_DOUBLE_CLICKED
...........................................................................

Fired when a user double clicks on a button by left clicking on it with a mouse, then left clicking on it again quickly.

 - **'type'** : pygame_gui.UI_BUTTON_DOUBLE_CLICKED
 - **'ui_element'** : The :class:`UIButton <pygame_gui.elements.UIButton>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the button that fired this event.
 - **'mouse_button'** : The mouse button that did the pressing (pygame.BUTTON_LEFT etc).
                        You have to enable button events for buttons other than the left mouse button which is
                        enabled by default.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
         if event.type == pygame_gui.UI_BUTTON_DOUBLE_CLICKED:
             if event.ui_element == test_button:
                 print('Test button pressed')

:class:`UIButton <pygame_gui.elements.UIButton>` - UI_BUTTON_ON_HOVERED
...........................................................................

Fired when a user starts hovering over a button with the mouse.

 - **'type'** : pygame_gui.UI_BUTTON_ON_HOVERED
 - **'ui_element'** : The :class:`UIButton <pygame_gui.elements.UIButton>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the button that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
         if event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
             if event.ui_element == test_button:
                 print('Test button hovered')

:class:`UIButton <pygame_gui.elements.UIButton>` - UI_BUTTON_ON_UNHOVERED
...........................................................................

Fired when a user stops hovering over a button with the mouse.

 - **'type'** : pygame_gui.UI_BUTTON_ON_UNHOVERED
 - **'ui_element'** : The :class:`UIButton <pygame_gui.elements.UIButton>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the button that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
         if event.type == pygame_gui.UI_BUTTON_ON_UNHOVERED:
             if event.ui_element == test_button:
                 print('Test button unhovered')

:class:`UITextBox <pygame_gui.elements.UITextBox>` - UI_TEXT_BOX_LINK_CLICKED
.............................................................................

Fired when a user clicks on a HTML link in a text box.

 - **'type'** : pygame_gui.UI_TEXT_BOX_LINK_CLICKED,
 - **'link_target'** : The 'href' parameter of the clicked link.
 - **'ui_element'** : The :class:`UITextBox <pygame_gui.elements.UITextBox>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the text box that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
         if event.type == pygame_gui.UI_TEXT_BOX_LINK_CLICKED:
             print(event.link_target)

:class:`UITextEntryLine <pygame_gui.elements.UITextEntryLine>` - UI_TEXT_ENTRY_CHANGED
.......................................................................................

Fired when a user changes the text in a text entry element by entering of deleting text. Not fired when set_text() is
used.

 - **'type'** : pygame_gui.UI_TEXT_ENTRY_CHANGED,
 - **'text'** : The user entered text in the text entry line.
 - **'ui_element'** : The :class:`UITextEntryLine <pygame_gui.elements.UITextEntryLine>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the text entry line that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
        if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            print("Changed text:", event.text)

:class:`UITextEntryLine <pygame_gui.elements.UITextEntryLine>` - UI_TEXT_ENTRY_FINISHED
.......................................................................................

Fired when a user presses the enter key with a text entry element active for entry.

 - **'type'** : pygame_gui.UI_TEXT_ENTRY_FINISHED,
 - **'text'** : The user entered text in the text entry line.
 - **'ui_element'** : The :class:`UITextEntryLine <pygame_gui.elements.UITextEntryLine>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the text entry line that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
         if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
             print("Entered text:", event.text)

:class:`UIDropDownMenu <pygame_gui.elements.UIDropDownMenu>` - UI_DROP_DOWN_MENU_CHANGED
........................................................................................

Fired when a user selects an option in a drop down menu.

 - **'type'** : pygame_gui.UI_DROP_DOWN_MENU_CHANGED,
 - **'text'** : The text of the selected option.
 - **'ui_element'** : The :class:`UIDropDownMenu <pygame_gui.elements.UIDropDownMenu>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the drop down menu that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
         if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
             print("Selected option:", event.text)



:class:`UIHorizontalSlider <pygame_gui.elements.UIHorizontalSlider>` - UI_HORIZONTAL_SLIDER_MOVED
.................................................................................................

Fired when a user moves a horizontal slider by pressing an arrow button or dragging the sliding button.

 - **'type'** : pygame_gui.UI_HORIZONTAL_SLIDER_MOVED
 - **'value'** : The current value the slider is set to.
 - **'ui_element'** : The :class:`UIHorizontalSlider <pygame_gui.elements.UIHorizontalSlider>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the button that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
         if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
             if event.ui_element == test_slider:
                 print('current slider value:', event.value)

:class:`UISelectionList <pygame_gui.elements.UISelectionList>` - UI_SELECTION_LIST_NEW_SELECTION
................................................................................................

Fired when a user selects a new item in a selection list.

 - **'type'** : pygame_gui.UI_SELECTION_LIST_NEW_SELECTION,
 - **'text'** : The text of the selected item.
 - **'ui_element'** : The :class:`UISelectionList <pygame_gui.elements.UISelectionList>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the element that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
        if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if event.ui_element == test_selection_list:
                print("Selected item:", event.text)

:class:`UISelectionList <pygame_gui.elements.UISelectionList>` - UI_SELECTION_LIST_DROPPED_SELECTION
....................................................................................................

Fired when a user un-selects an item, dropping it from a selection list.

 - **'type'** : pygame_gui.UI_SELECTION_LIST_DROPPED_SELECTION,
 - **'text'** : The text of the dropped item.
 - **'ui_element'** : The :class:`UISelectionList <pygame_gui.elements.UISelectionList>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the element that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
         if event.type == pygame_gui.UI_SELECTION_LIST_DROPPED_SELECTION:
             if event.ui_element == test_selection_list:
                 print("Dropped item:", event.text)

:class:`UISelectionList <pygame_gui.elements.UISelectionList>` - UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION
...........................................................................................................

Fired when a user double clicks on an item in a selection list.

 - **'type'** : pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION,
 - **'text'** : The text of the double clicked item.
 - **'ui_element'** : The :class:`UISelectionList <pygame_gui.elements.UISelectionList>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the element that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
        if event.type == pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION:
            if event.ui_element == test_selection_list:
                print("Double clicked item:", event.text)

:class:`UIWindow <pygame_gui.elements.UIWindow>` - UI_WINDOW_CLOSE
..................................................................

Fired when a window is closed.

 - **'type'** : pygame_gui.UI_WINDOW_CLOSE,
 - **'ui_element'** : The :class:`UIWindow <pygame_gui.elements.UIWindow>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the element that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == window:
                print("Window closed")

:class:`UIWindow <pygame_gui.elements.UIWindow>` - UI_WINDOW_MOVED_TO_FRONT
...........................................................................

Fired when a UI window is moved to the top of the stack. This happens when they are newly created and when they are
clicked on by a user.

 - **'type'** : pygame_gui.UI_WINDOW_MOVED_TO_FRONT,
 - **'ui_element'** : The :class:`UIWindow <pygame_gui.elements.UIWindow>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the element that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
        if event.type == pygame_gui.UI_WINDOW_MOVED_TO_FRONT:
            if event.ui_element == window:
                print("Window moved to front")

:class:`UIWindow <pygame_gui.elements.UIWindow>` - UI_WINDOW_RESIZED
..................................................................

Fired when a window is resized.

 - **'type'** : pygame_gui.UI_WINDOW_RESIZED,
 - **'ui_element'** : The :class:`UIWindow <pygame_gui.elements.UIWindow>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the element that fired this event.
 - **'external_size'** : The total size of the window including title bar, borders & shadows.
 - **'internal_size'** : The size inside the window where other elements are place (excluding title bar, borders & shadows).

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
        if event.type == pygame_gui.UI_WINDOW_RESIZED:
            if event.ui_element == window:
                print("Window resized")

:class:`UIConfirmationDialog <pygame_gui.windows.UIConfirmationDialog>` - UI_CONFIRMATION_DIALOG_CONFIRMED
...........................................................................................................

Fired when the 'confirm' button is chosen in a confirmation dialog.

 - **'type'** : pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED,
 - **'ui_element'** : The :class:`UIConfirmationDialog <pygame_gui.windows.UIConfirmationDialog>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the element that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
        if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if event.ui_element == confirmation_dialog:
                print("Confirming action.")

:class:`UIFileDialog <pygame_gui.windows.UIFileDialog>` - UI_FILE_DIALOG_PATH_PICKED
.....................................................................................

Fired when a path has been chosen in a file dialog.

 - **'type'** : pygame_gui.UI_FILE_DIALOG_PATH_PICKED
 - **'text'** : The path picked.
 - **'ui_element'** : The :class:`UIFileDialog <pygame_gui.windows.UIFileDialog>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the element that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
        if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            if event.ui_element == file_dialog:
                print("Path picked:", event.text)

:class:`UIColourPickerDialog <pygame_gui.windows.UIColourPickerDialog>` - UI_COLOUR_PICKER_COLOUR_PICKED
.........................................................................................................

Fired when a colour has been chosen in a colour picker dialog.

 - **'type'** : pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED
 - **'colour'** : The colour picked.
 - **'ui_element'** : The :class:`UIColourPickerDialog <pygame_gui.windows.UIColourPickerDialog>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the element that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
        if event.type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED:
            if event.ui_element == colour_picker:
                print("Colour picked:", event.colour)

:class:`UIColourChannelEditor <pygame_gui.windows.UIColourChannelEditor>` - UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED
...................................................................................................................

Fired when a colour channel element has had it's value changed. This event is used by the colour picker dialog.

 - **'type'** : pygame_gui.UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED
 - **'value'** : The current value of the channel.
 - **'channel_index'** : The index of this colour channel in the colour (R=0, G=1, B=2 etc).
 - **'ui_element'** : The :class:`UIColourChannelEditor <pygame_gui.windows.UIColourChannelEditor>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the element that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
        if event.type == pygame_gui.UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED:
            if event.ui_element == colour_channel:
                print("Colour channel value:", event.value)

:class:`UIConsoleWindow <pygame_gui.windows.UIConsoleWindow>` - UI_CONSOLE_COMMAND_ENTERED
.........................................................................................................

Fired when a command is entered into a console window. Usually by typing it in and pressing enter.

 - **'type'** : pygame_gui.UI_CONSOLE_COMMAND_ENTERED
 - **'command'** : The entered command.
 - **'ui_element'** : The :class:`UIConsoleWindow <pygame_gui.windows.UIConsoleWindow>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the element that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
        if event.type == pygame_gui.UI_CONSOLE_COMMAND_ENTERED:
            if event.ui_element == debug_console:
                if event.command == 'godmode':
                    print("Entering godmode")
                    player.enable_collision = False

:class:`UITextBox <pygame_gui.elements.UITextBox>` - UI_TEXT_EFFECT_FINISHED
.........................................................................................................

Fired when a command is entered into a console window. Usually by typing it in and pressing enter.

 - **'type'** : pygame_gui.UI_TEXT_EFFECT_FINISHED
 - **'effect'** : The type of the effect that ended.
 - **'ui_element'** : The :class:`UITextBox <pygame_gui.elements.UITextBox>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the element that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
        if event.type == pygame_gui.UI_TEXT_EFFECT_FINISHED:
            if event.ui_element == dialog_box:
                if event.effect == pygame_gui.TEXT_EFFECT_FADE_OUT:
                    print("Dialog faded out")
