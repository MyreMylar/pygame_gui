
Documentation - Home Page
===================================================

Pygame GUI is a module to help you make graphical user interfaces for games written in pygame. The module is firmly
forward looking and is designed to work on Pygame 2 and Python 3. Some features may not work on earlier versions of
pygame, and it's doubtful whether any of it works under Python 2.


Features
--------

 - Theme-able UI elements/widgets - you can use JSON theme files to change the colours, fonts and other appearance
   related details of your UI without touching your code.

 - A subset of HTML is supported for drawing word-wrapped text. Have bold styled words in the middle of a paragraph of text!
   Stick a link in there! Go absolutely hog wild, within the bounds of the defined subset of HTML the module supports.

 - Buttons, text entry, scroll bars and drop down menus all supported, with more on the way.

 - A window stack that will let you keep a bunch of moveable windows of 'stuff' around and correctly sorted.

 - As closely respecting of the pygame way of doing things as possible.


Installation
------------

Install the latest release from PyPi using pip with:

.. code-block:: console

    pip install pygame_gui -U


Or, you can build the latest version `from GitHub here <https://github.com/MyreMylar/pygame_gui>`_ by downloading the
source, navigating to the project's directory (the one with setup.py in it) and then building it with:

.. code-block:: console

    python setup.py install
    pip install . -U


Source code on GitHub
----------------------

The source code is `available from GitHub here <https://github.com/MyreMylar/pygame_gui>`_ .


Getting Started
---------------

Try our :ref:`quick-start` here if you are new to Pygame GUI. Check out the :ref:`theme-guide` if you want to learn how
to style your GUI.

Examples
.........
If you want to see Pygame GUI in action have a rifle through the
`examples project <https://github.com/MyreMylar/pygame_gui_examples>`_ over on GitHub to see some of the stuff the
library can do in action.

Game projects using Pygame GUI
------------------------------

 - `Tower Defence <https://github.com/MyreMylar/tower_defence/tree/new_gui>`_ - A tower defence demo game.
 - `Christmas Adventure <https://github.com/MyreMylar/christmas_adventure/tree/new_gui>`_ - A text adventure demo.


Table of contents
-----------------
.. toctree::
   :maxdepth: 2

   quick_start
   layout_guide
   theme_guide
   events
   text_effects
   change_list
   modules



Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
