Contributing to Pygame GUI
--------------------------

Basic guidlines for contributing
================================

1. *Pygame GUI uses PEP8 as a style guide*, mainly because it is enforced by PyCharm. Contributions should be in the same general style.
2. *Pygame GUI tries to use type hinting as much as possible*. This is mainly to help with code auto completion and refactoring operations, [See here](https://docs.python.org/3/library/typing.html) for the typing documentaion if you are unfamiliar with it's use.
3. *Pygame GUI uses docstrings*. At least most of the time; this is to help encourage better documentation.
4. *Pygame GUI tries to use pygame-like approaches wherever possible*. This is to make using the library as familiar to users of pygame as possible. This is why we use the pygame event system for communicating GUI events and pygame sprites for drawing GUI elements.
5. *Pygame GUI has a game focus* - but we also don't want to get too-specific to an individual project. New elements should have applicability to a reasonably wide range of game projects.
6. *Pygame GUI aims to be easy to use* - so it is approachable for relative novices, while still being practical for proper released projects. It's a tricky balance, but in general we want to minimise the amount of code to get _something_ up and running, and keep extra depth a little more tucked away.
7. *Pygame GUI has good documentation & tutorials*. In keeping with our newbie friendly approach, the Pygame GUI documentation aims to be up-to-date and friendly.
8. *Be nice* - try to remember to be nice & helpful to another when contributing!
9. *These are guidelines rather than hard rules*. Submitted issues are pretty much always welcome in whatever form as it lets us know someone is making use of the library! The creators of Pygame GUI are fallible humans and just as likely to not be doing something right as the next person, if you think we are doing something wrong and it doesn't fit these guidelines, just let us know.

Building the library
====================

Building Pygame GUI as a developer has a few additional dependecies.

For building the library you will need:

  - stringify

For building the documentation you will need:

  - sphinx
  - sphinx_rtd_theme
  
For running the tests you will need:

 - pytest
 
 
 All should be pip installable.

 
 Helpful checklist to go through before submitting a big pull request
 ====================================================================
 
 1. Do the tests run?
 2. Do the relevent examples at https://github.com/MyreMylar/pygame_gui_examples run & look OK?
 3. Have I documented any new features/code in a helpful fashion. If so, does the documentation build and look OK?
 
 
 Thank you for reading and considering contributing.
 
