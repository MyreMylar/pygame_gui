.. _events:

GUI events
===========

Some of the UI Elements produce a :py:class:`pygame.event.Event` when they are interacted with. These events all follow a common structure
that looks something like this:

 - **'type'** : pygame.USEREVENT
 - **'user_type'** : An id for the specific event that has happened. e.g. 'ui_button_pressed'
 - **'ui_element'** : The UI element that fired this event.
 - **'ui_object_id'** : The most unique ID that applies to the UI element that fired this event. e.g. 'hud_window.#sell_button'

Though some of the events also have additional data relevant to that event.

Event list
----------

A list of all the different events by element.

UIButton
........

ui_button_pressed
^^^^^^^^^^^^^^^^^^
Fired when a user presses a button by left clicking on it with a mouse, and releasing the mouse button while still
hovering over it.

 - **'type'** : pygame.USEREVENT
 - **'user_type'** : 'ui_button_pressed'
 - **'ui_element'** : The UIButton that fired this event.
 - **'ui_object_id'** : The most unique ID for the button that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
        if event.user_type == 'ui_button_pressed':
            if event.ui_element == test_button:
                print('Test button pressed')


UITextEntryLine
...............

ui_text_entry_finished
^^^^^^^^^^^^^^^^^^^^^^
Fired when a user presses the enter key with a text entry element active for entry.

 - **'type'** : pygame.USEREVENT
 - **'user_type'** : 'ui_text_entry_finished',
 - **'text'** : The user entered text in the text entry line.
 - **'ui_element'** : The UITextEntryLine that fired this event.
 - **'ui_object_id'** : The most unique ID for the text entry line that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
        if event.user_type == 'ui_text_entry_finished':
            print("Entered text:", event.text)

UIDropDownMenu
...............

ui_drop_down_menu_changed
^^^^^^^^^^^^^^^^^^^^^^^^^
Fired when a user selects an option in a drop down menu.

 - **'type'** : pygame.USEREVENT
 - **'user_type'** : 'ui_drop_down_menu_changed',
 - **'text'** : The text of the selected option.
 - **'ui_element'** : The UIDropDownMenu that fired this event.
 - **'ui_object_id'** : The most unique ID for the drop down menu that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
        if event.user_type == 'ui_drop_down_menu_changed':
            print("Selected option:", event.text)


UITextBox
..........

ui_text_box_link_clicked
^^^^^^^^^^^^^^^^^^^^^^^^
Fired when a user clicks on a HTML link in a text box.

 - **'type'** : pygame.USEREVENT,
 - **'user_type'** : 'ui_text_box_link_clicked',
 - **'link_target'** : The 'href' parameter of the clicked link.
 - **'ui_element'** : The UITextBox that fired this event.
 - **'ui_object_id'** : The most unique ID for the text box that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
        if event.user_type == 'ui_text_box_link_clicked':
            print(event.link_target)
