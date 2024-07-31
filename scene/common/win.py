from scene.state import SceneState

import displayio
import terminalio
from adafruit_display_text import label
from helper import animate_pulse, map_range
import scenes

from game_state import GameState

class PuzzleWin(SceneState):
    DELAY_INTERVAL = 2500
    SWITCHBOARD_FILL_INTERVAL = 500

    ANIMATION_STATE_DELAY = 0
    ANIMATION_STATE_FILL_SWITCHBOARD = 1
    ANIMATION_STATE_PULSE_BUTTON = 2

    def enter(self):
        device = self.device
        display = device.display_controller

        # Mark this puzzle as solved.
        puzzle_index = device.game_state.current_puzzle_index

        if puzzle_index is not None:
            device.game_state.set_puzzle_solved(puzzle_index, True)

        device.led_controller.fill_switchboard_color((0, 255, 0))
        device.led_controller.set_button_color((0, 0, 0))

        # Clear seven segment display
        device.seven_seg.fill(0)
        device.seven_seg.show()

        # Turn synth volume back up
        device.audio_controller.synth_volume = device.audio_controller.default_synth_volume

        # Play "success" music
        device.audio_controller.eighties_dystopia.play(notes=(48, 60, 62, 67, 69), note_duration=750)

        # Set up display
        self._label_group = displayio.Group(scale=2)
        display.main_group.append(self._label_group)

        scaled_width = int(display.WIDTH / 2)
        scaled_height = int(display.HEIGHT / 2)
        center_x = int(scaled_width / 2)
        center_y = scaled_height / 2

        new_label = label.Label(terminalio.FONT, text = "DISPATCH")
        new_label.anchor_point = (0.5, 0.5)
        new_label.anchored_position = (center_x, center_y - 5)
        self._label_group.append(new_label)

        new_label = label.Label(terminalio.FONT, text = "SUCCESS")
        new_label.anchor_point = (0.5, 0.5)
        new_label.anchored_position = (center_x, center_y + 5)
        self._label_group.append(new_label)

        # Animation state
        self._animation_state = self.ANIMATION_STATE_DELAY
        self._animation_timer = self.DELAY_INTERVAL
        self._led_animation_steps = GameState.JACK_COUNT/2
        self._button_pulse_timer = 0        

    def update(self, dt):
        device = self.device
        led_controller = device.led_controller  
        switchboard = device.switchboard

        self._animation_timer = max(0, self._animation_timer - dt)

        if self._animation_state == self.ANIMATION_STATE_DELAY:
            if self._animation_timer == 0:
                self._animation_state = self.ANIMATION_STATE_FILL_SWITCHBOARD
                self._animation_timer = self.SWITCHBOARD_FILL_INTERVAL
        elif self._animation_state == self.ANIMATION_STATE_FILL_SWITCHBOARD:

            # Update switchboard LED animation
            current_led = map_range(self._animation_timer, 0, self.SWITCHBOARD_FILL_INTERVAL, self._led_animation_steps - 1, 0)
            current_led = int(current_led)
            led_controller.set_switchboard_color(current_led, (0, 0, 0))
            led_controller.set_switchboard_color(current_led + 5, (0, 0, 0))

            if self._animation_timer == 0:
                self._animation_state = self.ANIMATION_STATE_PULSE_BUTTON
        else:
            if device.arcade_button.value == True:
                # Pulse the button green when not pressed
                (self._button_pulse_timer, c) = animate_pulse(self._button_pulse_timer, dt, 2000, (0, 255, 0))
                led_controller.set_button_color(c)
            else:
                # Set to white when pressed
                led_controller.set_button_color((128, 128, 128))

        if device.arcade_button.rose:
            led_controller.fill_switchboard_color((0, 0, 0))
            led_controller.set_button_color((128, 128, 128))

            if device.game_state.all_puzzles_solved:
                self.application.goto_scene(scenes.WIN_GAME)
            else:
                self.application.goto_scene(scenes.MENU)

    def exit(self):
        self.device.display_controller.main_group.remove(self._label_group)
