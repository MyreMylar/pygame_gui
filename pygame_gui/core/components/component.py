'from pygame_gui.core import UIElement'
    
class Component():
    def __init__(self, element: 'UIElement'):
        self.element = element
        
    def on_set_relative_position(self, *args, **kwargs):
        pass
    
    def on_set_position(self, *args, **kwargs):
        pass
    
    def on_set_minimum_dimensions(self, *args, **kwargs):
        pass
    
    def on_set_dimensions(self, *args, **kwargs):
        pass