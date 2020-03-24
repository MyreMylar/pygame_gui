.. _layout-guide:

Layout Guide
============

Pygame GUI elements are positioned in three different axes - x (horizontal), y (vertical) and a layer.


Horizontal & Vertical positioning
---------------------------------

Just as in regular pygame, the x and y axis used by pygame GUI run from 0 in the top left corner down to the pixel
size of whatever surface/window you are positioning your elements on.

The standard way of positioning elements is through using a 'relative rectangle'; this rectangle's position is always
relative to the container it is inside of. If you do not supply a container when creating your element, they will be
assigned the default 'root container' which  is created when you make the GUI's UI Manager and is the same size as the
supplied window_resolution parameter.

If you do supply a container when creating an element, by default it will normally be positioned relative to the top
left corner of the container. For example, if we were to position a 'hello' UIButton element inside of a UIWindow
container, and set it's relative_rect parameter like so:

.. code-block:: python
   :linenos:

    button_layout_rect = pygame.Rect(30, 20, 100, 20)

    UIButton(relative_rect=button_layout_rect,
             text='Hello',
             manager=manager,
             container=ui_window)

You would get a result something like this:

.. figure:: _static/layout_default_anchors.png

The button would maintain it's relative x and y position to the top left corner of the window it's contained inside
of, no matter where the window is moved to.

Layout Anchors
--------------

What if you don't want to position your element relative to the top left hand corner of a container? That's where
layout anchors come in, by changing the anchors for an element you change what the relative layout rectangle is
relative _to_.

The most straight forward use is to switch both layout axes to track different sides of the container. So instead of
being relative to the top left we anchor to, say the bottom right. That would look something like this:

.. code-block:: python
   :linenos:

    button_layout_rect = pygame.Rect(0, 0, 100, 20)
    button_layout_rect.bottomright = (-30, -20)

    UIButton(relative_rect=button_layout_rect,
             text='Hello', manager=manager,
             container=ui_window,
             anchors={'left': 'right',
                      'right': 'right',
                      'top': 'bottom',
                      'bottom': 'bottom'})

Note that both the left and right sides of the button are anchored to the right of our container, and both the top and
bottom are anchored to its bottom. This will keep the button the same size whatever size the container
is and will produce a layout looking a bit like this:

.. figure:: _static/layout_bottom_right_anchors.png

Sometimes though you want a layout to change size with it's container so we make maximum use of the available space.