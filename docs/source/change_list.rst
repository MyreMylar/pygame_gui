.. _change-list:

Change List
===========

A record of changes between versions of Pygame GUI.

**Version 0.5.0** - The Windows Update
--------------------------------------

Major system features
.....................

 - **Big UIWindow class refactoring**. UIWindow features like dragging windows, title bars and close buttons added as core
   features of the class. The class has moved from 'core' submodule to the 'elements' submodule. You can now create
   usable UIWindows without inheriting from the class first.
 - **Windows now support dynamic user resizing**. You can grab corners and sides of windows and stretch them around.
 - **Layout 'anchoring' system**. For laying out UI elements inside Containers (including Windows & Panels). This lets users place
   elements relative to other sides of their containers not just the default 'top left' every time.
 - **Button state transition 'cross-fade' effect.** A bit of flash.
 - **Theming files now support 'prototype' blocks.** To help reduce repetitive styling data. Theming parameter
   inheritance has also been changed to be more generous - e.g. now if you theme the 'button' block it will also affect
   buttons inside windows unless they have a more specific theming block.

New Elements
............

 - **UISelectionList** - a list of elements that let users select either one, or multiple items on it depending on how
   it is configured.
 - **UIPanel** - A new type of Container like element that you can place other elements inside of and set to start
   drawing at a specific layer in the UI. Designed for HUDs and the like.

New Windows
...........

 - **UIConfirmationDialog** - A Dialog Window which presents a choice to users to perform an action or cancel it.
 - **UIFileDialog** - A Dialog that helps users navigate a file system and pick a file from it.
 - **UIColourPickerDialog** - A Dialog window that lets you pick a colour.

Minor Features
..............

 - Drop down menu now supports larger lists of items in smaller space using a scroll bar and a parameter at creation to
   limit the vertical size. By default it will limit it's expansion to the boundaries of the container it is insider of.
 - Drop downs can now be expanded by clicking on the selected item button as well as the little arrow.
 - New theming options to remove the arrow buttons from horizontal sliders and vertical scroll bars.
 - Layer debug function on the UI Manager that lets you inspect what's going on with the UI Layers.
 - You can now set UIPanels and UIWindows as the 'container' parameter for all UIElements directly on creation.
 - Lots of new UI events to support the new elements and a new one for when the horizontal slider has moved.

API Breaking changes
....................

 - Lots of stuff with UIWindow. It's moved submodules, it has lots of new features that previously had to be provided in
   sub classes or didn't exist anywhere. The container for elements now excludes the title bar, shadow and borders of
   the window. Adapting is largely a case of deleting code, but it's a job of work.
 - UIMessageWindow has also changed a lot, it's now themed by it's object ID '#message_window' rather than an element
   ID like before, and it has lost lots of code to the underlying UIWindow class.
 - Object IDs for UI Events have changed to be the most specific ID that can be found or the element that generates
   them. This means code that was checking previously for '#my_window_ok_button' will probably need to be changed to
   check for '#my_window.#my_window_ok_button' or, you could change the button object ID to make it something like:
   '#my_window.#ok_button' because that identifier will now be more unique which was the general goal of the change.
 - Theming files may not perform exactly the same way they did before. Again, you can probably do lots of deleting if
   you make use of the prototype block system and I've tried to keep it mostly the same.
 - Default parameters have changed for 'text_box' and 'button'.

I try to minimise API breaking changes, but before we hit 1.0.0 I'd rather make changes that improve the overall module
than skip them and preserve an API that isn't working anymore.

Bug Fixes & Other Changes
.........................

 - Images loaded by the theming system should now work in pyinstaller -onefile .exe builds.
 - Drop down element should update the selected_option variable upon picking an option.
 - set_position, set_relative_position and set_dimensions methods should now work much more consistently across all
   elements.
 - Text boxes should expand correctly when the appropriate dimension is set to -1 or when the 'wrap_to_height' parameter
   is set to True on startup.
 - Text entry line text selection is smoother now.
 - UIContainer class now used all over the place - replacing the old 'root window' as 'root container', inside sliders &
   scroll bars.
 - Lots of refactoring to please Python Linting tools flake8 and pylint. Always more work to do here, but the code
   should be a few percent cleaner now.
 - Made use of interface/ABC meta classes to remove bothersome circular dependency problems.
 - More tests. Always more tests.
 - Text line documentation bug fixed by contributor **St3veR0nin**
