from scene.state import SceneState
from scene.win_game.talking import WinGameTalking

import displayio
import terminalio
from adafruit_display_text import label

class WinGameConnected(SceneState):

    def enter(self):
        self.device.led_controller.fill_switchboard_color((0, 0, 0))

        self._wait_timer = 2000

    def update(self, dt):
        self._wait_timer = max(self._wait_timer - dt, 0)

        if self._wait_timer == 0:
            next_state = WinGameTalking(self.scene)
            self.goto_next_state(next_state)

    def exit(self):
        pass