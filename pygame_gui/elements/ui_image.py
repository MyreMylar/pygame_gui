from ..core.ui_element import UIElement


class UIImage(UIElement):
    def __init__(self, relative_rect, image_surface, manager,
                 container=None, element_ids=None, object_id=None):
        if element_ids is None:
            new_element_ids = ['image']
        else:
            new_element_ids = element_ids.copy()
            new_element_ids.append('image')
        super().__init__(relative_rect, manager, container,
                         starting_height=1,
                         layer_thickness=1,
                         object_id=object_id,
                         element_ids=new_element_ids)
        self.image = image_surface
