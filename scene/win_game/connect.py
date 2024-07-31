from scene.state import SceneState
from scene.win_game.connected import WinGameConnected

import displayio
import terminalio
from adafruit_display_text import label
from rainbowio import colorwheel
from game_state import GameState

class WinGameConnect(SceneState):
    LED_ANIMATION_INTERVAL = 125
    LED_COLOR_CYCLE_INTERVAL = 5000

    def enter(self):
        device = self.device
        audio_controller = device.audio_controller
        led_controller = device.led_controller
        display = device.display_controller

        # Edited version of: https://pixabay.com/sound-effects/the-sound-of-dial-up-internet-6240/
        audio_controller.play_wave_file("audio/dialup.wav")

        # Set up display
        scale = 2
        self._label_group = displayio.Group(scale=scale)
        display.main_group.append(self._label_group)

        scaled_width = int(display.WIDTH / scale)
        scaled_height = int(display.HEIGHT / scale)
        center_x = int(scaled_width / 2)
        center_y = int(scaled_height / 2)

        new_label = label.Label(terminalio.FONT, text = "Connecting")
        new_label.anchor_point = (0.5, 0.5)
        new_label.anchored_position = (center_x, center_y)
        self._label_group.append(new_label)

        # Switchboard LED animation
        self._led_animation_timer = self.LED_ANIMATION_INTERVAL
        self._led_animation_index = 0
        self._led_animation_frames = [0, 1, 2, 3, 4, 3, 2, 1]
        self._led_color_timer = 0

        c = self._get_led_color()
        led_controller.set_switchboard_color(0, c)
        led_controller.set_switchboard_color(5, c)

    def update(self, dt):
        device = self.device
        led_controller = device.led_controller

        # Color cycle
        self._led_color_timer += dt

        if self._led_color_timer >= self.LED_COLOR_CYCLE_INTERVAL:
            self._led_color_timer = 0

        # Update LED animation position
        self._led_animation_timer -= dt

        if self._led_animation_timer <= 0:
            self._led_animation_timer = self.LED_ANIMATION_INTERVAL

            self._led_animation_index += 1

            if self._led_animation_index >= len(self._led_animation_frames):
                self._led_animation_index = 0

            led_controller.fill_switchboard_color((0, 0, 0))

            c = self._get_led_color()
            f = self._led_animation_frames[self._led_animation_index]
            led_controller.set_switchboard_color(f, c)
            led_controller.set_switchboard_color(f + 5, c)

        if not device.audio_controller.is_playing_wave_file:
            next_state = WinGameConnected(self.scene)
            self.goto_next_state(next_state)
            return

    def exit(self):
        self.device.display_controller.main_group.remove(self._label_group)

    def _get_led_color(self):
        hue = (self._led_color_timer / self.LED_COLOR_CYCLE_INTERVAL) * 255
        return colorwheel(hue)
