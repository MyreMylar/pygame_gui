.. _text-effects:

Text Effects
============

When using either :class:`UITextBox <pygame_gui.elements.UITextBox>` or :class:`UILabel <pygame_gui.elements.UILabel>`
there is an option to add some of the below text effects that will control some aspect of how the text in the
element is displayed.

These effects are:

Apply to all text in the Element, or an individual chunk of tagged text in a UITextBox:

 - **Fade In** (ID: pygame_gui.TEXT_EFFECT_FADE_IN)
 - **Fade Out** (ID: pygame_gui.TEXT_EFFECT_FADE_OUT)
 - **Typing Appear** (ID: pygame_gui.TEXT_EFFECT_TYPING_APPEAR)

Apply ONLY to tagged chunks in a UITextBox:

 - **Bounce** (ID: pygame_gui.TEXT_EFFECT_BOUNCE)
 - **Tilt** (ID: pygame_gui.TEXT_EFFECT_TILT)
 - **Expand & Contract** (ID: pygame_gui.TEXT_EFFECT_EXPAND_CONTRACT)


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

Applying an effect to a tagged chunk in a text box
--------------------------------------------------

First tag up the chunk of text you want to apply an effect to with the 'effect' tag. The text should have the same style
throughout, otherwise you will get two chunks each running an effect. The 'id' parameter supplied to the effect tag is
used to pick it out for an effect.

.. code-block:: python
   :linenos:

    text_box = UITextBox(
        html_text="This is an <effect id=test>EARTHQUAKE</effect>",
        relative_rect=pygame.Rect(100, 100, 200, 50),
        manager=ui_manager)

Then when you want to apply an effect, supply the tag to set_active_effect like so:

.. code-block:: python
   :linenos:

    text_box.set_active_effect(pygame_gui.TEXT_EFFECT_BOUNCE, effect_tag='test')

Event when an effect is finished
--------------------------------

For effects that start, and then end after they have finished doing their thing - rather than looping forever, A GUI
event is fired that you can check for in your event loop. It is called - UI_TEXT_EFFECT_FINISHED. You can read more
about it in the :ref:`events` documentation.

Effect parameters
-----------------

Most of the effects have a parameter or two to give you some control over the effect. The parameters are listed below
for each effect

Fade In
--------

 A simple alpha fade from translucent to opaque.

Params
......

 - **'time_per_alpha_change'** - A float that controls the time in seconds to change alpha by 1 (to a maximum of 255)

Fade Out
---------

 The reverse of fade in, an alpha fade from opaque to translucent.

Params
......

 - **'time_per_alpha_change'** - A float that controls the time in seconds to change alpha by 1 (to a maximum of 255)

Typing Appear
--------------

 This effect makes the text in the box appear letter-by-letter as if someone was typing it in by hand.

Params
......

 - **'time_per_letter'** - A float that controls the time in seconds to add a single letter.
 - **'time_per_letter_deviation'** - A float that controls the deviation in time from the average that it takes to add a letter. Defaults to 0.0

Bounce
--------------

 This effect makes the text in a chunk bounce up and down.

Params
......

 - **'loop'** - A bool that sets whether this effect loops indefinitely (have to manually stop it). Defaults to true
 - **'bounce_max_height'** - An int that controls how high the text bounces up from the baseline in pixels. Defaults to 5.
 - **'time_to_complete_bounce'** - A float that controls the time in seconds to do a complete bounce. Defaults to 0.5.

Tilt
--------------

 This effect makes the text in a chunk rotate to a maximum rotation angle and then return back to 0.

Params
......

 - **'loop'** - A bool that sets whether this effect loops indefinitely (have to manually stop it). Defaults to true
 - **'max_rotation'** - An int that controls how far the text rotates before returning to 0. Defaults to 1080.
 - **'time_to_complete_rotation'** - A float that controls the time in seconds to do a complete tilt. Defaults to 5.0.

Expand & Contract
-----------------

This effect makes the text in a chunk expand to a maximum scale and then return back to 1.0 (default size).

Params
......

 - **'loop'** - A bool that sets whether this effect loops indefinitely (have to manually stop it). Defaults to true
 - **'max_scale'** - An float that controls how much the text expands before returning to 1.0. Defaults to 1.5.
 - **'time_to_complete_expand_contract'** - A float that controls the time in seconds to do a complete expansion and contraction. Defaults to 2.0.