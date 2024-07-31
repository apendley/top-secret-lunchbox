from scene.state import SceneState

from helper import map_range
from game_state import GameState
import scenes

class BootFinish(SceneState):

    def enter(self):
        device = self.device

        # Animation control
        self._animation_interval = 750
        self._animation_timer = 0

        self._led_animation_steps = GameState.JACK_COUNT/2
        self._switchboard_target_x = 36.0

        device.audio_controller.eighties_dystopia.skip_to_next_note()

    def update(self, dt):
        device = self.device

        self._animation_timer += dt
        self._animation_timer = min(self._animation_timer, self._animation_interval)

        # Update switchboard LED animation
        current_led = map_range(self._animation_timer, 0, self._animation_interval, 0, self._led_animation_steps - 1)
        current_led = int(current_led)

        device.led_controller.set_switchboard_color(current_led, (0, 0, 255))
        device.led_controller.set_switchboard_color(current_led + 5, (0, 0, 255))

        # Update switchboard OLED animation
        current_x = map_range(self._animation_timer, 0, self._animation_interval, 0, self._switchboard_target_x)
        current_x = int(current_x)
        device.display_controller.switchboard_renderer.set_center_x(current_x)

        # When anim is done, go to next state
        if self._animation_timer >= self._animation_interval:
            self.application.goto_scene(scenes.MENU)

    def exit(self):
        pass