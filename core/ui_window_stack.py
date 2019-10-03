

class UIWindowStack:
    def __init__(self, window_resolution):
        self.window_resolution = window_resolution
        self.stack = []

    def clear(self):
        while len(self.stack) != 0:
            self.stack.pop().kill()
        self.stack.clear()

    def add_new_window(self, window):
        if len(self.stack) > 0:
            new_layer = self.stack[-1].get_top_layer() + 1
        else:
            new_layer = 0
        window.change_window_layer(new_layer)
        self.stack.append(window)

    def remove_window(self, window_to_remove):
        if window_to_remove in self.stack:
            popped_windows_to_readd = []
            window = self.stack.pop()
            while window != window_to_remove:
                popped_windows_to_readd.append(window)
                window = self.stack.pop()

            popped_windows_to_readd.reverse()
            for old_window in popped_windows_to_readd:
                self.add_new_window(old_window)

    def move_window_to_front(self, window_to_front):
        if window_to_front in self.stack:
            popped_windows_to_readd = []
            window = self.stack.pop()
            while window != window_to_front:
                popped_windows_to_readd.append(window)
                window = self.stack.pop()

            popped_windows_to_readd.reverse()
            for old_window in popped_windows_to_readd:
                self.add_new_window(old_window)

            self.add_new_window(window_to_front)

    def get_root_window(self):
        if len(self.stack) > 0:
            return self.stack[0]
        else:
            return None

    def is_window_at_top(self, window):
        if window is self.stack[-1]:
            return True
        else:
            return False
