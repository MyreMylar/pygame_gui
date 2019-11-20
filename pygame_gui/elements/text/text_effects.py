class TextBoxEffect:
    def __init__(self, all_characters):
        self.all_characters = all_characters

    def should_full_redraw(self):
        return False

    def should_redraw_from_chunks(self):
        return False

    def update(self, time_delta):
        pass

    def get_end_text_pos(self):
        return len(self.all_characters)

    def get_final_alpha(self):
        return 255


class TypingAppearEffect(TextBoxEffect):
    def __init__(self, all_characters):
        super().__init__(all_characters)
        self.text_progress = 0
        self.time_per_letter = 0.05
        self.time_per_letter_acc = 0.0
        self.time_to_redraw = False

    def update(self, time_delta):
        if self.text_progress < len(self.all_characters):
            if self.time_per_letter_acc < self.time_per_letter:
                self.time_per_letter_acc += time_delta
            else:
                self.time_per_letter_acc = 0.0
                self.text_progress += 1
                self.time_to_redraw = True

    def should_full_redraw(self):
        if self.time_to_redraw:
            self.time_to_redraw = False
            return True
        else:
            return False

    def get_end_text_pos(self):
        return self.text_progress


class FadeInEffect(TextBoxEffect):
    def __init__(self, all_characters):
        super().__init__(all_characters)
        self.alpha_value = 0
        self.time_per_alpha_change = 0.01
        self.time_per_alpha_change_acc = 0.0
        self.time_to_redraw = False

    def update(self, time_delta):
        if self.alpha_value < 255:
            self.time_per_alpha_change_acc += time_delta

            alpha_progress = int(self.time_per_alpha_change_acc / self.time_per_alpha_change)

            if alpha_progress != self.alpha_value:
                self.alpha_value = alpha_progress
                if self.alpha_value > 255:
                    self.alpha_value = 255
                self.time_to_redraw = True

    def should_redraw_from_chunks(self):
        if self.time_to_redraw:
            self.time_to_redraw = False
            return True
        else:
            return False

    def get_final_alpha(self):
        return self.alpha_value


class FadeOutEffect(TextBoxEffect):
    def __init__(self, all_characters):
        super().__init__(all_characters)
        self.alpha_value = 255
        self.time_per_alpha_change = 0.01
        self.time_per_alpha_change_acc = 0.0
        self.time_to_redraw = False

    def update(self, time_delta):
        if self.alpha_value > 0:
            self.time_per_alpha_change_acc += time_delta

            alpha_progress = 255 - int(self.time_per_alpha_change_acc / self.time_per_alpha_change)

            if alpha_progress != self.alpha_value:
                self.alpha_value = alpha_progress
                if self.alpha_value < 0:
                    self.alpha_value = 0
                self.time_to_redraw = True

    def should_redraw_from_chunks(self):
        if self.time_to_redraw:
            self.time_to_redraw = False
            return True
        else:
            return False

    def get_final_alpha(self):
        return self.alpha_value
