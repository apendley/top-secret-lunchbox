from scene.state import SceneState
from scene.boot.wait import BootWait
from scene.boot.finish import BootFinish

import random
from helper import color_by_index, map_range
from game_state import GameState

class BootStart(SceneState):
    LED_EVENT_INTERVAL = 100
    OLED_ANIMATION_INTERVAL = 7500

    def enter(self):
        device = self.device

        # Start playing computer boot sound
        device.audio_controller.eighties_dystopia.play(notes=(35, 47, 48, 52, 53, 55, 63, 65, 67),
                                                       note_duration=150)

        # Every time this timer expires, we set a random LED to a random color
        self._next_led_event_timer = self.LED_EVENT_INTERVAL
        self._led_event_counter = int(self.OLED_ANIMATION_INTERVAL / self.LED_EVENT_INTERVAL)

        # Switchboard display animation control
        self._switchboard_max_center_space = 128.0
        self._switchboard_animation_interval = self.OLED_ANIMATION_INTERVAL
        self._switchboard_animation_timer = 0

        # Switchboard renderer
        sb_renderer = device.display_controller.switchboard_renderer
        sb_renderer.set_center_space(int(self._switchboard_max_center_space))
        sb_renderer.hide_labels = True
        sb_renderer.set_center_x(0)
        sb_renderer.blit()
        device.display_controller.set_switchboard_renderer_active(True)

    def update(self, dt):
        device = self.device
        switchboard = device.switchboard

        self._switchboard_animation_timer += dt
        self._switchboard_animation_timer = min(self._switchboard_animation_timer, self._switchboard_animation_interval)

        center_x = map_range(self._switchboard_animation_timer, 0, self._switchboard_animation_interval, self._switchboard_max_center_space, 0)
        center_x = int(center_x)

        # Update switchboard animation
        device.display_controller.switchboard_renderer.set_center_space(center_x)

        # Update LED animation
        self._next_led_event_timer -= dt

        if self._next_led_event_timer <= 0:
            self._next_led_event_timer += self.LED_EVENT_INTERVAL

            led_index = random.randrange(0, switchboard.pin_count)
            steps = 16

            # add 1 to skip black
            led_color = color_by_index(random.randrange(0, steps - 1) + 1, steps)
            device.led_controller.set_switchboard_color(led_index, led_color)

            self._led_event_counter = max(0, self._led_event_counter - 1)

            if self._led_event_counter == 0:
                device.audio_controller.eighties_dystopia.play(notes=GameState.MAIN_THEME_NOTES)

                next_state = BootWait(self.scene)
                self.goto_next_state(next_state)
                return

    def exit(self):
        pass