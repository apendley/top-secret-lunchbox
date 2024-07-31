from scene.state import SceneState
from scene.reaction_match.play import ReactionMatchPlay

import random
import displayio
import terminalio
from adafruit_display_text import label

class ReactionMatchStart(SceneState):

    def enter(self):
        device = self.device
        display = device.display_controller

        device.led_controller.set_button_color((0, 0, 0))
        device.led_controller.fill_switchboard_color((0, 0, 0))

        # Title label
        self._title_group = displayio.Group(scale=2)

        scaled_width = int(display.WIDTH / 2)
        scaled_height = int(display.HEIGHT / 2)
        center_x = int(scaled_width / 2)
        center_y = scaled_height / 2

        new_label = label.Label(terminalio.FONT, text = "GET READY")
        new_label.anchor_point = (0.5, 0.5)
        new_label.anchored_position = (center_x, center_y)
        self._title_group.append(new_label)
        device.display_controller.main_group.append(self._title_group)        

        self.scene.show_countdown(self.scene.round_interval)

        self._timer = random.randrange(3000, 7000)

    def update(self, dt):
        self._timer -= dt

        if self._timer <= 0:
            self.device.audio_controller.play_wave_file("audio/glitch_001.wav")

            next_state = ReactionMatchPlay(self.scene)
            self.goto_next_state(next_state)

    def exit(self):
        self.device.display_controller.main_group.remove(self._title_group)