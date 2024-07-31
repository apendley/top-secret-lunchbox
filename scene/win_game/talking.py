from scene.state import SceneState
from scene.win_game.finished import WinGameFinished

import random
import displayio
import terminalio
from adafruit_display_text import label
from helper import map_range

class WinGameTalking(SceneState):
    LED_MAX_LEVEL = 1000
    LED_DECAY_RATE = 3.5

    def enter(self):
        device = self.device
        display = device.display_controller
        audio_controller = device.audio_controller

        # (delay in ms, text to display)
        self._events = [
            (1500, "Hello?"),
            (1000, ""),
            (140, "Who"),
            (140, "is"),
            (1200, "this?"),
            (1100, "Wait..."),
            (140, "How"),
            (150, "did"),
            (150, "you"),
            (150, "get"),
            (150, "this"),
            (2000, "number?"),
        ]

        self._event_index = 0
        self._event_timer = self._events[0][0]
        self._led_level = self.LED_MAX_LEVEL

        # Set up display
        scale = 2
        self._label_group = displayio.Group(scale=scale)
        display.main_group.append(self._label_group)

        scaled_width = int(display.WIDTH / scale)
        scaled_height = int(display.HEIGHT / scale)
        center_x = int(scaled_width  / 2)
        center_y = int(scaled_height / 2)

        new_label = label.Label(terminalio.FONT, text = self._events[self._event_index][1])
        new_label.anchor_point = (0.5, 0.5)
        new_label.anchored_position = (center_x, center_y)

        self._label = new_label
        self._label_group.append(new_label)

        # Play audio clip.
        # Generated from the 'say' command on the terminal of my MacBook.
        audio_controller.play_wave_file("audio/who_is_this.wav")   
        self._draw_leds()     

    def update(self, dt):
        # Update events
        self._event_timer -= dt

        if self._event_timer <= 0:
            self._event_index += 1

            if self._event_index < len(self._events):
                event = self._events[self._event_index]
                self._event_timer = event[0]
                self._label.text = event[1]

                if event[1] == "":
                    self._led_level = 0
                else:
                    self._led_level = self.LED_MAX_LEVEL
            else:
                next_state = WinGameFinished(self.scene)
                self.goto_next_state(next_state)
                return

        # Update LEDs
        self._draw_leds()

        decay = dt * self.LED_DECAY_RATE
        self._led_level = max(self._led_level - decay, 0)

    def exit(self):
        self.device.display_controller.main_group.remove(self._label_group)

    def _draw_leds(self):
        led_controller = self.device.led_controller

        top_led = map_range(self._led_level, 0, self.LED_MAX_LEVEL, 0, 5)

        led_controller.fill_switchboard_color((0, 0, 0))

        for i in range(0, top_led):
            led_controller.set_switchboard_color(4 - i, (255, 0, 0))
            led_controller.set_switchboard_color(4 - i + 5, (255, 0, 0))        
