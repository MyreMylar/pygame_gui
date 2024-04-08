# import pygame
# import pygame_gui
# from pygame_gui.core import UIContainer
# from pygame_gui.elements import UIButton, UIAutoResizingContainer, UIAutoScrollingContainer, UIDropDownMenu


# pygame.init()
#
# pygame.display.set_caption('Quick Start')
# window_surface = pygame.display.set_mode((800, 600))
#
# background = pygame.Surface(window_surface.get_size())
# background.fill(pygame.Color('#000000'))
#
# manager = pygame_gui.UIManager((900, 700))
#
# buttons = []
# resizing_test = UIAutoResizingContainer(pygame.Rect(20, 50, 700, 500), manager=manager)
# # resizing_test = UIContainer(pygame.Rect(40, 50, 700, 500), manager=manager)
# resizing_test = UIAutoScrollingContainer(pygame.Rect(40, 50, 700, 500), manager, False, True)
#
# hello_button = UIButton(relative_rect=pygame.Rect((250, 175), (100, 50)),
#                         text='Say Hello 1',
#                         manager=manager,
#                         container=resizing_test,
#                         object_id="SayHello1"
#                         )
#
# hello_button.set_hold_range((400, 400))
# buttons.append(hello_button)
# hello_button = UIButton(relative_rect=pygame.Rect((-450, 225), (100, 50)),
#                         text='Say Hello' + str(int(hello_button.text[-1]) + 1),
#                         manager=manager, container=resizing_test,
#                         object_id="SayHello" + str(int(hello_button.text[-1]) + 1),
#                         anchors={"right": "right", "left": "right"}
#                         #anchors={"left_target": hello_button, "top_target": hello_button}
#                         )
#
# hello_button.set_hold_range((400, 400))
# buttons.append(hello_button)
# hello_button = UIButton(relative_rect=pygame.Rect((-400, 275), (-1, -1)),
#                         text='Say Hello' + str(int(hello_button.text[-1]) + 1),
#                         manager=manager, container=resizing_test,
#                         object_id="SayHello" + str(int(hello_button.text[-1]) + 1),
#                         anchors={"right": "right"}
#                         #anchors={"left_target": hello_button, "top_target": hello_button}
#                         )
# hello_button.set_hold_range((400, 400))
# buttons.append(hello_button)
# hello_button = UIButton(relative_rect=pygame.Rect((50, 40), (-1, -1)),
#                         text='Say Hello' + str(int(hello_button.text[-1]) + 1),
#                         manager=manager, container=resizing_test,
#                         object_id="SayHello" + str(int(hello_button.text[-1]) + 1),
#                         anchors={"left_target": hello_button, "top_target": hello_button})
# # print("After all ", hello_button._image)
# hello_button.set_hold_range((400, 400))
# buttons.append(hello_button)
# # hello_button = UIDropDownMenu(relative_rect=pygame.Rect((60, 40), (150, 50)),
# #                               options_list=['Say Hello' + str(int(hello_button.text[-1]) + 1)],
# #                               starting_option='Say Hello' + str(int(hello_button.text[-1]) + 1),
# #                               manager=manager, container=resizing_test,
# #                               anchors={"left_target": hello_button, "top_target": hello_button})
# # buttons.append(hello_button)
# hello_button.set_hold_range((400, 400))
#
# clock = pygame.time.Clock()
# is_running = True
# pressed = False
# element = None
#
# while is_running:
#     time_delta = clock.tick(60) / 1000.0
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             is_running = False
#
#         elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == hello_button:
#             pressed = False
#             element = None
#
#             hello_button = UIButton(relative_rect=pygame.Rect((-15, -40), (-1, -1)),
#                                     text='Say Hello' + str(int(hello_button.text[-1]) + 1),
#                                     manager=manager, container=resizing_test,
#                                     object_id="SayHello" + str(int(hello_button.text[-1]) + 1),
#                                     anchors={"right": "right", "bottom": "bottom", "right_target": hello_button, "bottom_target": hello_button})
#             # print(hello_button.rect, hello_button.relative_rect)
#             buttons.append(hello_button)
#             hello_button.set_hold_range((400, 400))
#             # size = pygame.Vector2(resizing_test.get_size()) + pygame.Vector2(hello_button.get_abs_rect().size)
#             # resizing_test.set_dimensions(size)
#             # print(size)
#             # print(resizing_test.get_image_clipping_rect(), resizing_test.get_image_clipping_rect())
#             # hello_button._set_image_clip(None)
#             # resizing_test._set_image_clip(None)
#             # resizing_test.ui_container._set_image_clip(None)
#             # print(resizing_test.get_image_clipping_rect())
#
#         elif event.type == pygame_gui.UI_BUTTON_PRESSED:
#             pressed = False
#             element = None
#
#         elif event.type == pygame_gui.UI_BUTTON_START_PRESS:
#             pressed = True
#             element = event.ui_element
#
#         manager.process_events(event)
#
#     if element and element.in_hold_range(pygame.mouse.get_pos()) and pressed:
#         pos = pygame.mouse.get_pos()
#         dif = pygame.Vector2(pos) - pygame.Vector2(element.rect.center)
#         new_pos = dif + pygame.Vector2(element.relative_rect.topleft)
#         element.set_relative_position(new_pos)
#
#     manager.update(time_delta)
#
#     window_surface.blit(background, (0, 0))
#
#     # pygame.draw.rect(window_surface, "Yellow", resizing_test.scrollable_container.rect, 1)
#     pygame.draw.rect(window_surface, "White", resizing_test.rect, 1)
#     for button in buttons:
#         pygame.draw.rect(window_surface, "Orange", button.rect, 1)
#
#     manager.draw_ui(window_surface)
#
#     pygame.display.update()

import pygame
import pygame_gui
from pygame_gui import UI_FORM_SUBMITTED
from pygame_gui.elements import UIButton, UIAutoResizingContainer, UIAutoScrollingContainer, UIForm, UIDropDownMenu

pygame.init()

pygame.display.set_caption('Quick Start')
window_surface = pygame.display.set_mode((800, 600))

background = pygame.Surface((800, 600))
background.fill(pygame.Color('#000000'))

manager = pygame_gui.UIManager((800, 600))

test_rect = pygame.Rect(40, 50, 700, 500)

# buttons = []
# resizing_test = UIAutoScrollingContainer(pygame.Rect(40, 50, 700, 500), manager, True, False)
# hello_button = UIButton(relative_rect=pygame.Rect((650, 275), (100, 50)),
#                         text='Say Hello 1',
#                         manager=manager, container=resizing_test)
# buttons.append(hello_button)
#
# hello_button = UIButton(relative_rect=pygame.Rect((25, 75), (150, 25)),
#                         text='Say Hello' + str(int(hello_button.text[-1]) + 1),
#                         manager=manager, container=resizing_test,
#                         anchors={"left_target": hello_button, "top_target": hello_button})
# buttons.append(hello_button)

questionnaire = {
    "Just enter one character:": "character",
    "Perhaps some more:": "short_text",
    "Or go wild!": "long_text",
    "how about a section?": {"do you like it?": "boolean", "well, here, section-ception": {"do you like it?": "boolean", "well, here, section-ception": {"finally...": "integer"}}},
    "Enter a float:": "decimal(default=0.01)",
    "You must enter something here:": "short_text('here', True)",
    "Persome more:": "long_text",
    "let's try a button": UIButton(pygame.Rect(100, 100, 100, 100), "button"),
    "Peaps some more:": "short_text",
    "OO dropdown!": UIDropDownMenu(["foo", "foo", "foo", "foo", "foo", "foo", "foo", "foo", "foo", "foo"], "foo",
                                   pygame.Rect(100, 100, 100, 100), ),
    "rhaps some more:": "password"}
form_test = UIForm(test_rect, questionnaire, manager)

print(form_test.combined_element_ids)
print(form_test.get_container().combined_element_ids)
print(form_test.parsed_questionnaire["how about a section?"].combined_element_ids)
print(form_test.parsed_questionnaire["how about a section?"].parsed_questionnaire["well, here, section-ception"].combined_element_ids)


clock = pygame.time.Clock()
is_running = True
pressed = False
element = None

while is_running:
    time_delta = clock.tick(30) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            print(event.ui_element.most_specific_combined_id)
            pressed = False
            element = None

        elif event.type == UI_FORM_SUBMITTED:
            print(event.form_values)

        # elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == hello_button:
        #
        #     hello_button = UIButton(relative_rect=pygame.Rect((50, 75), (150, 25)),
        #                             text='Say Hello' + str(int(hello_button.text[-1]) + 1),
        #                             manager=manager, container=resizing_test,
        #                             anchors={"left_target": hello_button, "top_target": hello_button})
        #     print(hello_button.rect, hello_button.relative_rect)
        #     buttons.append(hello_button)

        # elif event.type == pygame_gui.UI_BUTTON_START_PRESS and event.ui_element in buttons:
        #     pressed = True
        #     element = event.ui_element

        manager.process_events(event)

    # if element and element.in_hold_range(pygame.mouse.get_pos()) and pressed:
    #     pos = pygame.mouse.get_pos()
    #     dif = pygame.Vector2(pos) - pygame.Vector2(element.rect.center)
    #     new_pos = dif + pygame.Vector2(element.relative_rect.topleft)
    #     element.set_relative_position(new_pos)

    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    pygame.draw.rect(window_surface, "Yellow", form_test.scrollable_container.rect, 1)
    pygame.draw.rect(window_surface, "Green", form_test._view_container.rect, 1)
    pygame.draw.rect(window_surface, "White", form_test.rect, 1)
    s_cont = form_test.parsed_questionnaire["how about a section?"]
    pygame.draw.rect(window_surface, "Blue", s_cont.rect, 1)
    pygame.draw.rect(window_surface, "Blue", s_cont.section_container.rect, 1)
    # for button in buttons:
    #     pygame.draw.rect(window_surface, "Orange", button.rect, 1)
    # print(form_test.submit_button.combined_element_ids)
    # print(form_test.parsed_questionnaire)

    pygame.draw.rect(window_surface, "Orange", form_test.submit_button.rect, 1)
    for label in form_test.parsed_questionnaire.values():
        if isinstance(label, pygame_gui.elements.ui_form.InputField):
            # print(label[1].combined_element_ids)
            pygame.draw.rect(window_surface, "Orange", label[1].rect, 1)
            pygame.draw.rect(window_surface, "Orange", label[2].rect, 1)
            # print(label[0].rect, label[0].most_specific_combined_id)
    manager.draw_ui(window_surface)

    pygame.display.update()

