from scene.state import SceneState

import displayio
import terminalio
from adafruit_display_text import label
from helper import map_range, animate_pulse

class WinGameFinished(SceneState):
    FADE_OUT_DURATION = 20000

    def enter(self):
        device = self.device
        audio_controller = device.audio_controller
        display = device.display_controller

        # Play ominous sounding music
        audio_controller.eighties_dystopia.play(notes=(43, 44), note_duration=500)

        # Make the switchboard look scary
        device.led_controller.fill_switchboard_color((255, 0, 0))

        # Set up display
        scale = 2
        self._label_group = displayio.Group(scale=scale)
        display.main_group.append(self._label_group)

        scaled_width = int(display.WIDTH / scale)
        scaled_height = int(display.HEIGHT / scale)
        center_x = int(scaled_width / 2)
        center_y = int(scaled_height / 2)

        new_label = label.Label(terminalio.FONT, text = "To be")
        new_label.anchor_point = (0.5, 0.5)
        new_label.anchored_position = (center_x, center_y - 5)
        self._label_group.append(new_label)

        new_label = label.Label(terminalio.FONT, text = "Continued")
        new_label.anchor_point = (0.5, 0.5)
        new_label.anchored_position = (center_x, center_y + 5)
        self._label_group.append(new_label)

        self._fade_out_timer = self.FADE_OUT_DURATION
        self._switchboard_pulse_timer = 0        

    def update(self, dt):
        device = self.device

        self._fade_out_timer = max(self._fade_out_timer - dt, 0)
        volume = map_range(self._fade_out_timer, 0, self.FADE_OUT_DURATION, 0, 1.0)
        device.audio_controller.main_volume = volume


        (self._switchboard_pulse_timer, c) = animate_pulse(self._switchboard_pulse_timer, 
                                                           dt=dt, 
                                                           period=2000, 
                                                           color=(255, 0, 0), 
                                                           min_brightness=91,
                                                           offset=64)  

        device.led_controller.fill_switchboard_color(c)

    def exit(self):
        self.device.display_controller.main_group.remove(self._label_group)