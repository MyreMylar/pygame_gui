.. _events:

GUI events
===========

Some of the UI Elements produce a :py:func:`pygame.Event <pygame:pygame.event.Event>` when they are interacted with. These events
all follow a common structure that looks something like this:

 - **'type'** : pygame.USEREVENT
 - **'user_type'** : An id for the specific event that has happened. e.g. 'ui_button_pressed'
 - **'ui_element'** : The UI element that fired this event.
 - **'ui_object_id'** : The most unique ID that applies to the UI element that fired this event. e.g. 'hud_window.#sell_button'

Though some of the events also have additional data relevant to that event.

Event list
----------

A list of all the different events by element.

:class:`UIButton <pygame_gui.elements.UIButton>` - UI_BUTTON_PRESSED
....................................................................

Fired when a user presses a button by left clicking on it with a mouse, and releasing the mouse button while still
hovering over it.

 - **'type'** : pygame.USEREVENT
 - **'user_type'** : pygame_gui.UI_BUTTON_PRESSED
 - **'ui_element'** : The :class:`UIButton <pygame_gui.elements.UIButton>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the button that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == test_button:
                    print('Test button pressed')

:class:`UITextEntryLine <pygame_gui.elements.UITextEntryLine>` - UI_TEXT_ENTRY_FINISHED
.......................................................................................

Fired when a user presses the enter key with a text entry element active for entry.

 - **'type'** : pygame.USEREVENT
 - **'user_type'** : pygame_gui.UI_TEXT_ENTRY_FINISHED,
 - **'text'** : The user entered text in the text entry line.
 - **'ui_element'** : The :class:`UITextEntryLine <pygame_gui.elements.UITextEntryLine>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the text entry line that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                print("Entered text:", event.text)

:class:`UIDropDownMenu <pygame_gui.elements.UIDropDownMenu>` - UI_DROP_DOWN_MENU_CHANGED
........................................................................................

Fired when a user selects an option in a drop down menu.

 - **'type'** : pygame.USEREVENT
 - **'user_type'** : pygame_gui.UI_DROP_DOWN_MENU_CHANGED,
 - **'text'** : The text of the selected option.
 - **'ui_element'** : The :class:`UIDropDownMenu <pygame_gui.elements.UIDropDownMenu>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the drop down menu that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                print("Selected option:", event.text)

:class:`UITextBox <pygame_gui.elements.UITextBox>` - UI_TEXT_BOX_LINK_CLICKED
.............................................................................

Fired when a user clicks on a HTML link in a text box.

 - **'type'** : pygame.USEREVENT,
 - **'user_type'** : pygame_gui.UI_TEXT_BOX_LINK_CLICKED,
 - **'link_target'** : The 'href' parameter of the clicked link.
 - **'ui_element'** : The :class:`UITextBox <pygame_gui.elements.UITextBox>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the text box that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_TEXT_BOX_LINK_CLICKED:
                print(event.link_target)
