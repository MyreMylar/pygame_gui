.. _change-list:

Change List
===========

A record of changes between versions of Pygame GUI.

--------

**Version 0.6.2**
-----------------------------------------------------------------

Another smallish release, with some bug fixes and a new type of element - the UIStatusBar by @ConquerProgramming1.
There should be a new example in the examples project demonstrating the new status bar


Bug Fixes & Other Changes
.........................................................

 - **Fix bug with UITextLine background** - Should now remain the background colour when clicked on.
 - **Fix bug with UISlider changed event** - They weren't generating on a single arrow button click.
 - **Added fallback characters for hidden text int text entry line** - Some fonts don't have the circle character.
 - **Added support for py.typed** - Thanks to @ChrisChou-freeman for mentioning this (there are still lots of mypy typing errors to fix)
 - **Made K_KP_ENTER key behave the same as K_RETURN for UITextEntryLine** - Thanks to @Jamieakuma on the discord.
 - **New theming option for the text cursor in the UITextLine** - No more hardcoded white, now you can match it to your UI theme a lot easier.
 - **Add a 'pixel_size' option to the html subset font tag** - so you can set the font size directly.

Further thanks & Pull Requests
..............................

Several people stepped up to help improve the google translate localization efforts since the 0.6.0 release.

 - **New UIStatusBar element** - Thanks to @ConquerProgramming1, see `(pull #246) <https://github.com/MyreMylar/pygame_gui/pull/246>`_
 - **Fixed typos in Russian localization** - Thanks to @SophieSilver, see `(pull #241) <https://github.com/MyreMylar/pygame_gui/pull/241>`_
 - **Fixes to UIManager docs** - Thanks again to @ConquerProgramming1, see `(pull #240) <https://github.com/MyreMylar/pygame_gui/pull/240>`_
 - **Change UIManager process_events() to return True if it uses the event** - Thanks once more to @ConquerProgramming1, see `(pull #239) <https://github.com/MyreMylar/pygame_gui/pull/239>`_


**Version 0.6.1**
-----------------------------------------------------------------

A quick bug fix release.


Bug Fixes & Other Changes
.........................................................

 - **PyInstaller should work correctly with pygame_gui** - Fixed PyInstaller hook added in 0.6.0 not being picked up.
 - **Added set_text() to UITextBox** - There were several requests for it.
 - **Minor fixes to TextEffect interface** - Added default 'None' in a few places.
 - **Fixed API docs not building on read** -  the docs (thanks to @lionel42)
 - **Made K_KP_ENTER key behave the same as K_RETURN for UITextEntryLine** - Thanks to @Jamieakuma on the discord.

Further thanks & Pull Requests
..............................

Several people stepped up to help improve the google translate localization efforts since the 0.6.0 release.

 - **Improved Japanese localization** - Thanks to @KansaiGaijin, see `(pull #231) <https://github.com/MyreMylar/pygame_gui/pull/231>`_
 - **Improved Indonesian localization** - Thanks to @avaxar, see `(pull #232) <https://github.com/MyreMylar/pygame_gui/pull/232>`_
 - **Improved Russian localization** - Thanks to @SophieSilver, see `(pull #237) <https://github.com/MyreMylar/pygame_gui/pull/237>`_


--------

**Version 0.6.0** - The text update
-----------------------------------------------------------------

The focus of this update was on everything to do with text in the GUI

Dropped compatibility & Breaking changes
..............................................

 - **Dropped support for Pygame 1** - Pygame 2 has been out for some time now and switching fully to Pygame 2 allows the library to adopt its new features and remove some old compatibility hacks.
 - **Dropped support for Python 3.5** - Python 3.5 has been end-of-life for some time. Removing support for it allows the library to use 3.6 onwards features like f strings. This is following pygame 2 also dropping 3.5 (and earlier) support.
 - **Simplified UI events** - New events are generated with 'type' set to the previous 'user_type' values. This makes event processing code simpler. Old events will continue to exist until 0.8.0 but please move to the new style of events as they are the only ones that will get new attributes, new events added in 0.6.0 are only in the new style.


Major Features
...............................

 - **Localization Support** - There is now some basic support for switching the language of the GUI to one of ten supported languages.
 - **New Console Window** - A new default GUI element that provides support for text shell/console type user  interaction.
 - **Rewritten & unified text backend** - The text displaying and laying out portions of the GUI have all been massively changed and all the GUI elements now all share common code. This makes it easier to add new features to the text, and also have them work everywhere.

Minor features
...............................

 - **UIButtons & UILabels can now scale based off their text** - passing in -1 for a dimension will cause that dimension to be set based on the height or width of the element's text.
 - **More default options to allow only certain characters in UITextLine** - 'alpha_numeric' was added as an option for the latin alphabet. The underlying system was adjusted to allow for localised versions of these character sets, but these do not yet exist.
 - **set_text_hidden() added to UITextLine** - To enable a 'password' style entry line.
 - **text shadow theming options added to UIButton** - Previously these were only on the UILabel.
 - **<img> tag images can now be added to to a UITextBox** - Makes it easier to wrap text around images and have inline images in text (colourful emoji?)
 - **get_relative_mouse_pos() added to UIWindow** - gets a mouse position relative to the UIWindow you call it from.
 - **UISlider now moves in customisable fixed increments when clicking arrow button** - Makes it easier to have precise sliders.
 - **UIButton events can now be produced by any mouse button** - new 'mouse_button' attribute on button events & 'generate_click_events_from' parameter to UIButton.
 - **UIDropDown open/close drop down button width added as theming option** - Called 'open_button_width'.
 - **Text alignment theming options for UITextBox & UILabel** - See their theming pages for details.
 - **Improved text effects** - Effects can now be applied to tagged chunks of text in a text box, some effects can also be applied to UILabels. There are parameters for effects, and an event fired when an effect finishes.


Bug Fixes & Other Changes
.........................................................

 - **PyInstaller should work correctly with pygame_gui** - A 'hook' file has been added to scoop up the default data for pygame_gui, and documentation added on using Pyinstaller & Nuitka with the library. See `(issue #166) <https://github.com/MyreMylar/pygame_gui/issues/166>`_
 - **Fixed issue with window resolution changes** - Thanks to @lonelycorn `(issue #215) <https://github.com/MyreMylar/pygame_gui/issues/215>`_
 - **<br> tag fixed to produce blank lines** - See `(issue #217) <https://github.com/MyreMylar/pygame_gui/issues/217>`_
 - **Fixed missing type cast in UIFileDialog** - Thanks to @GUI-GUY `(issue #207) <https://github.com/MyreMylar/pygame_gui/issues/207>`_
 - **Fixed issues with adding lines to bottom of UITextBox** - Demonstrated in new UIConsoleWindow window. See issues `(issue #69) <https://github.com/MyreMylar/pygame_gui/issues/69>`_ and `(issue #78) <https://github.com/MyreMylar/pygame_gui/issues/78>`_
 - **Fixed issues with positioning UIDropDown inside container** -  See issues `(issue #179) <https://github.com/MyreMylar/pygame_gui/issues/179>`_ and `(issue #153) <https://github.com/MyreMylar/pygame_gui/issues/153>`_
 - **Improved scaling support** - I still don't have the hardware to test this properly, but thanks to @jlaumonier, see `(issue #210) <https://github.com/MyreMylar/pygame_gui/issues/210>`_ it should work a bit better.
 - **Fixed html link click events firing multiple times in some circumstances** - Thanks to @RedFlames for finding and fixing this. See `(issue #206) <https://github.com/MyreMylar/pygame_gui/issues/206>`_
 - **Various documentation improvements and updates** - Thanks to everyone who pointed out things they didn't understand on GitHub, in Discord or in person. I've tried to make things clearer wherever I can. Keep letting me know when you get stuck!

Further thanks & Pull Requests
..............................

While I was very slowly rebuilding the text back end for 0.6.0 the library also received several pull requests that
will now make their way into the released version. After 1.0.0, when I (@MyreMylar) finish my main work on it, pull
requests like this will be the main way the library changes from version to version.

For now I'm putting them in their own section of this changes document to highlight them (unless there is a pull request
that adds a big feature that is going up top as well)

 - **Fixed redundant redrawing of UITextEntryLine()** - Thanks to @glipR, see `(pull #178) <https://github.com/MyreMylar/pygame_gui/pull/178>`_
 - **Fixed double clicking folder in UIFileDialog** - Thanks to @glipR, see `(pull #197) <https://github.com/MyreMylar/pygame_gui/pull/197>`_
 - **Fixed hiding & showing disabled buttons** - Thanks to @xirsoi, see `(pull #185) <https://github.com/MyreMylar/pygame_gui/pull/185>`_
 - **Fixed grammatical errors in index.rst** - Thanks to @nonoesimposible, see `(pull #208) <https://github.com/MyreMylar/pygame_gui/pull/208>`_
 - **Added ability to set default values for UISelectionList** - Thanks to @teaguejt, see `(pull #213) <https://github.com/MyreMylar/pygame_gui/pull/213>`_
 - **Fix invalid URL for game project examples** - Thanks to @Grimmys, see `(pull #216) <https://github.com/MyreMylar/pygame_gui/pull/216>`_

--------

**Version 0.5.7** - Hiding and better pygame 2 support
-----------------------------------------------------------------


Major Features
...............................

 - **show() & hide() feature added to all elements**. Allows you to temporarily hide and show a UIElement or UIWindow rather than having to kill() and recreate it each time when you want it out of sight for a bit. This feature was contributed by @ylenard so all thanks goes to them.

 - **switch to using premultiplied alpha blending for pygame 2** - For a long while now features like rounded corners have not worked correctly with pygame 2. Thanks to some recent improvements in the latest version of pygame 2.0.0.dev10 pygame_gui has been able to switch to using pre-multiplied alpha blending when dev10 is also installed. This resolves all the visual issues with rounded corners and I think runs a teeny bit faster too.


Minor features
...............................

 - **enable() & disable() have been added to many more elements and windows** - Maybe all of them now, even where it doesn't really make sense. Disable things to your heart's content.
 - **focus sets** - This is a new concept I'm trialling in the UI to indicate a group of elements that together constitute a thing that should all have interaction focus at the same time. So far it's working fairly well and has made it easy to extend pygame 2's scrollwheel functionality so that you should now scroll the content of what you are hovering with the wheel (at least in most cases). In the future this idea may make it easier to handle keyboard only input and input via controllers.
 - **class IDs for UIElement objects** - UIelement objects could always have an Object ID, but those were designed to be unique specifiers for events as well as theming and sometimes you want to pick out a specific group of elements for theming that all already have unique object IDs. Enter class IDs, there is a new datatype 'ObjectID' that you can pass when you create an element and it lets you set two string IDs, the old unique `object_id` and the new `class_id`. Once you have some objects sharing a `class_id` you can theme theme in a theme file theming block the same way you would with an object ID.  It's also worth noting here that you can load multiple theme files into a single UIManager if you want to organise your theme data some more.

Dropped compatibility
..............................................

 - **No longer supporting pygame 1.9.3 & pygame 1.9.4** - Keeping up with the bugs in these old versions of pygame was holding back the GUI so I made the decision to drop support in this version. If you are still using pygame 1.9.3 or 1.9.4, my apologies.

Bug Fixes & Other Changes
.........................................................

 - **Switched to using a custom Sprite and SpriteGroup class as base for UI elements*** - previously I was using the pygame classes but after getting up close and personal with them recently I realised that the existing sprite base was doing things that we weren't using and that a slimmed down sprite could speed things up. In my tests on windows this has made the draw loop about 10% faster.
 - **A series of fixes to the drop down menus** - they should now not break when they would have overlapped previously and correctly set the height of the background when the height of a list item is set to a custom value. Thanks to all the people who submitted bugs with these.
 - **fixed a bunch of LGTM alerts** - gotta have that A+ rating.


Further thanks
.............................

 - Thanks once again to @ylenard for all their hard work put into this release.
 - Thank you to everyone who reported issues in the GUI this time around. If you don't report 'em, we can't fix 'em.

--------

**Version 0.5.6** - Loading changes & minor optimisations
-----------------------------------------------------------------


Major Feature
............................

- **Improved loading system** - Pygame GUI now supports:
    - **Incremental loading** - By passing in a loader you create yourself to the UIManager, you can get progress updates on how your GUI resources are loading. See `IncrementalThreadedResourceLoader` in `pygame_gui.core`, or the new loading examples in the [examples repository](https://github.com/MyreMylar/pygame_gui_examples).
    - **Loading resources from python packages** - This is, probably, the wave of the future for python projects. Instead of putting your resources in plain old directories and using boring file paths you can now add an exciting empty dunder `__init__.py` file to your resource directories, transforming them into packages which can then be loaded with a similar style to how we import code. There is a new `PackageResource` class at module scope to support this and some new ways to specify resources in theme files. See the [examples](https://github.com/MyreMylar/pygame_gui_examples) for a few usages and the [documentation](https://pygame-gui.readthedocs.io/en/latest/theme_reference/theme_button.html).
    - **Loading with threads** - As always with anything parallel, this comes with an extra frisson of danger. But in theory you should be able to see some improvement in how fast your resources are loaded. On my hard drive I've seen something like a 10% loading speed increase in my tests, but that can increase to almost 2x faster if your drive access speed is slow - as I discovered loading from a network drive. Care should probably be taken not to try and use any of the resources *while* they are being loaded as heck know what pygame will make of that. Threaded loading is enabled by default, so let us know if any problems crop up and I'll implement a fall-back, sequential-loading-only loader.

Breaking interface change
.....................................................

If you have any code that looks like this:

    background.fill(manager.ui_theme.get_colour(None, None, 'dark_bg'))

Or

    background.fill(manager.ui_theme.get_colour([], [], 'dark_bg'))

Then you will now have to change it to:

    background.fill(manager.ui_theme.get_colour('dark_bg'))

This actually resulted from general optimisation changes but I think it is a solid improvement to the interface for getting default colours from a theme so I am enforcing it.

- **Custom UI elements** - If you've made any custom UI element classes (inheriting from UIElement) with their own theming then the procedure for getting theming IDs and theming parameters has changed slightly. You can see an example of adapting to these changes in the [pygame_paint repository here](https://github.com/MyreMylar/pygame_paint/commit/c5e7023bd0998b461b574f816b033dcf193399d3)

Bug Fixes & Other Changes
.........................................................

 - The speed of creating 100+ buttons in a single frame should now be slightly faster than the 0.4.0 era of Pygame GUI rather than 3x *slower* (fix for #91)
 - Mildly improved exception handling internally - This is an ongoing project.
 - Abstract interface classes now properly enforce their interface on inheriting classes. Oops.

--------

**Version 0.5.5** - The Windows Update, Update
-----------------------------------------------------

No major features, just a smattering of bug fixes, a few new elements and probably some new bugs.

New Elements
............

 - **UIHorizontalScrollBar** - Just like the vertical scroll bar, but in the x axis.
 - **UIScrollingContainer** - Another type of ContainerLike element. this one is largely invisible except for scroll bars that appear on the right hand side and at the bottom when the content inside the container is larger than the container itself.

Minor Features
..............

 - UIFileDialog has a couple of new options on creation mainly to support make file dialogs for loading and saving files. Probably still more bugs to find in this bad boy.
 - New simple method to set the title of a window.
 - New events for when text is changed in a text entry event, when a button is 'clicked once' (pushed down, but not yet released) to match the double click event and when buttons are hovered and unhovered.

Bug Fixes & Other Changes
.........................

 - Added more interfaces to the code base which should make autocomplete more reliable when using the methods of the library.
 - Fixed a bug with containers not using 'hover_point()' method for testing hovering collisions with the mouse thus messing up various interactions slightly.
 - Fixed a bug with removing the close button on a window theme not correctly resizing the title bar.
 - Changed UIElement to take a copy of passed in rectangles in case they are re-used elsewhere.
 - Fixed  bugs in UIPanel and UISelection list where anchors and containers of the element were not being copied to their root container leading to shenanigans.
 - Resizing the elemnet container for the UIWindow element was missing off the border leading to overlaps. This is now fixed.
 - Fix for elements owning root containers anchored to the top and bottom of containers having their root containers incorrectly resized before they were positioned, thereby causing a mess of appearance bugs. It was a bad scene. Should now be fixed.

--------

**Version 0.5.1**
--------------------

Bug Fixes
----------

 - Getting the library working with pygame 1.9.3
 - Removing window's title bar now works correctly.

--------

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
