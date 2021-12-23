.. _text-effects:

Text Effects
============

When using the :class:`UITextBox <pygame_gui.elements.UITextBox>` element there is an option to add one of three preset
effects that will control how all of the text in the element is displayed.

These effects are:

 - **Fade In.** (ID: pygame_gui.TEXT_EFFECT_FADE_IN)
 - **Fade Out.** (ID: pygame_gui.TEXT_EFFECT_FADE_OUT)
 - **Typing Appear.** (ID: pygame_gui.TEXT_EFFECT_TYPING_APPEAR)


Applying an effect
------------------

To apply an effect to a :class:`UITextBox <pygame_gui.elements.UITextBox>` element call the set_active_effect method,
with the id of the effect to apply:

.. code-block:: python
   :linenos:

    text_box.set_active_effect(pygame_gui.TEXT_EFFECT_FADE_IN)

The effect will start running immediately after calling this method. You can deactivate an active effect by calling:

.. code-block:: python
   :linenos:

   text_box.set_active_effect(None)

Event when an effect is finished
--------------------------------

For effects that start, and then end after they have finished doing their thing - rather than looping forever, A GUI
event is fired that you can check for in your event loop. It is called - UI_TEXT_EFFECT_FINISHED. You can read more
about it in the :ref:`events` documentation.

Fade In
--------

 A simple alpha fade from translucent to opaque. This effect is currently only supported on Pygame 2.

Fade Out
---------

 The reverse of fade in, an alpha fade from opaque to translucent. This effect is currently only supported on Pygame 2.

Typing Appear
--------------

 This effect makes the text in the box appear letter-by-letter as if someone was typing it in by hand (very smoothly).



