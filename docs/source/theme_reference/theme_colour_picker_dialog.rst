.. _theme-colour-picker:

UIColourPickerDialog Theming Parameters
=======================================

:class:`UIColourPickerDialog <pygame_gui.windows.UIColourPickerDialog>` is a UIWindow with the object id of '#colour_picker_dialog'.

.. figure:: ../_static/colour_picker_static_image.png

   An image of the Colour Picker Dialog.

Inherited Parameters
--------------------

As a UIWindow the Colour Picker Dialog has all the theming parameters of the UIWindow, which you can read more about here
:ref:`theme-window`.

Sub-elements
------------

As well as the sub-elements of the UIWindow (title bar and close button) which you can read about here
:ref:`theme-window`, the Colour Picker Dialog has the following sub element IDs -

UIButtons:

 - '#colour_picker_dialog.#ok_button'
 - '#colour_picker_dialog.#cancel_button'

UIColourChannelEditor:

 - '#colour_picker_dialog.colour_channel_editor'

You can find out more about theming buttons here: :ref:`theme-button`.

UIColourChannelEditor Theming Parameters
----------------------------------------

:class:`UIColourChannelEditor <pygame_gui.windows.ui_colour_picker_dialog.UIColourChannelEditor>` has no theming
parameters of its own.

Sub-elements
------------

The Colour channel editor is only used in the colour picker dialog, and is composed of three sub-elements. You can
access them for theming with the following IDs:

 - '#colour_picker_dialog.colour_channel_editor.text_entry_line'
 - '#colour_picker_dialog.colour_channel_editor.label'
 - '#colour_picker_dialog.colour_channel_editor.horizontal_slider'

You can find out more about theming text entry lines here: :ref:`theme-text-entry-line`, labels here: :ref:`theme-label`
and horizontal sliders here: :ref:`theme-horizontal-slider`.
