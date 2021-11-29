.. _quick-start:

Quick Start Guide
=================

To start making use of Pygame GUI, you first need to have at least the bare bones of a pygame project
if you don't know much about pygame then there is some `documentation here <https://www.pygame.org/docs/>`_
and many tutorials across the internet.

Assuming you have some idea what you are doing with pygame, I've created a basic, empty pygame project with
the code below. You can just copy and paste it into an empty python script file.:

.. code-block:: python
   :linenos:

    import pygame


    pygame.init()

    pygame.display.set_caption('Quick Start')
    window_surface = pygame.display.set_mode((800, 600))

    background = pygame.Surface((800, 600))
    background.fill(pygame.Color('#000000'))

    is_running = True

    while is_running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        window_surface.blit(background, (0, 0))

        pygame.display.update()


That should open an empty window upon being run. If it doesn't you may need to install pygame.

Next, we need to make sure that we've installed the pygame_gui module. If you haven't, then the quickest way is to open
a terminal or Command Prompt and type:

.. code-block:: console

    pip install pygame_gui

Assuming that all installed correctly, then the next step is to head back to our code, import the Pygame GUI module
and create a UIManager:

.. code-block:: python
   :linenos:
   :emphasize-lines: 2,13

    import pygame
    import pygame_gui


    pygame.init()

    pygame.display.set_caption('Quick Start')
    window_surface = pygame.display.set_mode((800, 600))

    background = pygame.Surface((800, 600))
    background.fill(pygame.Color('#000000'))

    manager = pygame_gui.UIManager((800, 600))

    is_running = True

    while is_running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        window_surface.blit(background, (0, 0))

        pygame.display.update()

As you can see the UIManager class, like pygame's display.set_mode() function also needs to know the current
size of the screen.

The UI manager handles calling the update, draw and event handling functions of all the UI elements we create and
assign to it. To make it do this we need to call these functions on the UIManager object we just created.

.. code-block:: python
   :linenos:
   :emphasize-lines: 15, 19, 24, 26, 29

    import pygame
    import pygame_gui


    pygame.init()

    pygame.display.set_caption('Quick Start')
    window_surface = pygame.display.set_mode((800, 600))

    background = pygame.Surface((800, 600))
    background.fill(pygame.Color('#000000'))

    manager = pygame_gui.UIManager((800, 600))

    clock = pygame.time.Clock()
    is_running = True

    while is_running:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            manager.process_events(event)

        manager.update(time_delta)

        window_surface.blit(background, (0, 0))
        manager.draw_ui(window_surface)

        pygame.display.update()

As you may have noticed we also had to create a pygame Clock to track the amount of time in seconds that
passes between each loop of the program. We need this 'time_delta' value because several of the UI elements make
use of timers and this is a convenient place to get it.

Using .tick() to fix the frame rate of your pygame program is a good idea anyway, otherwise your code will just
run as fast as it can go unnecessarily, probably straining the circuits of any computer it runs on.

So, now the UI manager is all setup it's time to create a UI element so we can actually see something on the screen.
Let's try and stick a UIButton in the middle of the screen that prints 'Hello World' to the console when we press it.

To start lets make the button.

.. code-block:: python
   :linenos:
   :emphasize-lines: 15, 16, 17

    import pygame
    import pygame_gui


    pygame.init()

    pygame.display.set_caption('Quick Start')
    window_surface = pygame.display.set_mode((800, 600))

    background = pygame.Surface((800, 600))
    background.fill(pygame.Color('#000000'))

    manager = pygame_gui.UIManager((800, 600))

    hello_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
                                                text='Say Hello',
                                                manager=manager)

    clock = pygame.time.Clock()
    is_running = True

    while is_running:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            manager.process_events(event)

        manager.update(time_delta)

        window_surface.blit(background, (0, 0))
        manager.draw_ui(window_surface)

        pygame.display.update()

Now if you try running the program again you should see a grey rectangle in the middle of the window with the text
'Say Hello' on it, and if you move the mouse over it or click on it the rectangle changes colour. That's what a
basic UIButton looks like. If you load a theme file into the UIManager we can change these colours, the font of the
text on the button and several other things about it's appearance.

For now though, we won't worry about theming our button - we still need to make it print 'Hello World!' to the console
When we click on it. To do that we need to check the pygame event queue:

.. code-block:: python
   :linenos:
   :emphasize-lines: 28, 29, 30, 31

    import pygame
    import pygame_gui


    pygame.init()

    pygame.display.set_caption('Quick Start')
    window_surface = pygame.display.set_mode((800, 600))

    background = pygame.Surface((800, 600))
    background.fill(pygame.Color('#000000'))

    manager = pygame_gui.UIManager((800, 600))

    hello_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
                                                text='Say Hello',
                                                manager=manager)

    clock = pygame.time.Clock()
    is_running = True

    while is_running:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

             if event.type == pygame_gui.UI_BUTTON_PRESSED:
                 if event.ui_element == hello_button:
                     print('Hello World!')

            manager.process_events(event)

        manager.update(time_delta)

        window_surface.blit(background, (0, 0))
        manager.draw_ui(window_surface)

        pygame.display.update()

Pygame GUI creates events of various types, in this case we are after UI_BUTTON_PRESSED. You can find more documentation
on the different event types under :ref:`events`. Finally, we do a check to see which specific button has been pressed,
since we have a variable for our hello_button and the event also includes a reference to the ui_element that created it,
we can just compare the event's ui_element attribute with our hello_button variable to confirm they are one and the same.

Try running the code again and clicking on the button. If it's all worked you should see 'Hello World!' printed to the
python console each time you click the button.

Congratulations, you've learned the basics of using Pygame GUI! If you want to explore more, check out the API Reference
and try creating some of the other UI Elements, have a look at how layout works with the :ref:`layout-guide` or head
over to the :ref:`theme-guide` to learn how to style your elements.
