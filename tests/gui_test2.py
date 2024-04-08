import pygame
import pygame_gui
from pygame_gui.core import UIContainer
from pygame_gui.elements import UIButton, UI2DSlider, UIScrollingContainer, UIAutoScrollingContainer
from pygame_gui.windows import UIColourPickerDialog

pygame.init()

WIDTH, HEIGHT = 900, 600
pygame.display.set_caption('Quick Start')
window_surface = pygame.display.set_mode((WIDTH, HEIGHT))

background = pygame.Surface(window_surface.get_size())
background.fill(pygame.Color('#000000'))

manager = pygame_gui.UIManager((WIDTH, HEIGHT))

buttons = []
# resizing_test = UIAutoScrollingContainer(pygame.Rect(40, 50, WIDTH*0.75, HEIGHT*0.75), manager=manager)
#
# hello_button = UIButton(relative_rect=pygame.Rect((-400, 275), (-1, -1)),
#                         text='Say Hello 1',
#                         manager=manager, container=resizing_test,
#                         object_id="SayHello1",
#                         anchors={"right": "right"}
#                         )
# hello_button.set_hold_range((400, 400))
# buttons.append(hello_button)
# hello_button = UIButton(relative_rect=pygame.Rect((50, 40), (-1, -1)),
#                         text='Say Hello 2',
#                         manager=manager, container=resizing_test,
#                         object_id="SayHello2",
#                         anchors={"left": "left", "left_target": hello_button, "top_target": hello_button})
# hello_button.set_hold_range((400, 400))
# buttons.append(hello_button)

container = UIScrollingContainer(pygame.Rect(100, 100, 200, 200),
                                 manager=manager)
hello_button = UIButton(relative_rect=pygame.Rect((-200, -100), (200, 100)),
                        text='Say Hello 1',
                        manager=manager, container=container,
                        object_id="SayHello1",
                        anchors={"right": "right", "bottom": "bottom"}
                        )
buttons.append(hello_button)
container.set_scrollable_area_dimensions((500, 600))

clock = pygame.time.Clock()
is_running = True
pressed = False
element = None

while is_running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            pressed = False
            element = None

        elif event.type == pygame_gui.UI_2D_SLIDER_MOVED:
            ...  # print(hello_slider.get_current_value())

        elif event.type == pygame_gui.UI_BUTTON_START_PRESS and event.ui_element in buttons:
            pressed = True
            element = event.ui_element

        manager.process_events(event)

    if element and element.in_hold_range(pygame.mouse.get_pos()) and pressed:
        pos = pygame.mouse.get_pos()
        dif = pygame.Vector2(pos) - pygame.Vector2(element.rect.center)
        new_pos = dif + pygame.Vector2(element.relative_rect.topleft)
        element.set_relative_position(new_pos)

    manager.update(time_delta)

    window_surface.blit(background, (0, 0))

    pygame.draw.rect(window_surface, "Yellow", container.scrollable_container.rect, 1)
    pygame.draw.rect(window_surface, "Green", container._view_container.rect, 1)
    pygame.draw.rect(window_surface, "White", container.rect, 1)
    for button in buttons:
        pygame.draw.rect(window_surface, "Orange", button.rect, 1)

    manager.draw_ui(window_surface)

    pygame.display.update()
