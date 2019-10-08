.. _quick-start:

Quick start guide
=================

To start making use of Pygame GUI, you first need to have at least the bare bones of a pygame project
if you don't know much about pygame then there is some `documentation here <https://www.pygame.org/docs/>`_
and many tutorials across the internet.

Assuming you have some idea what you are doing with pygame, I've created a basic, empty pygame project with
the code below:

```
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

```

That should open an empty window upon being run.