from scene.state import SceneState

import displayio
import terminalio
from adafruit_display_text import label
from helper import color_by_index
from game_state import GameState

class FindSumCorrect(SceneState):

    def enter(self):
        device = self.device
        display = device.display_controller
        switchboard = device.switchboard
        led_controller = device.led_controller

        device.audio_controller.play_wave_file("audio/confirmation_001.wav")

        # Title text group
        self._prompt_group = displayio.Group()

        new_label = label.Label(terminalio.FONT, text = "Disconnect to resume")
        new_label.anchor_point = (0.5, 1.0)
        new_label.anchored_position = (64, 60)
        self._prompt_group.append(new_label)        

        display.main_group.append(self._prompt_group)

        self._title_group = displayio.Group(scale=2)

        new_label = label.Label(terminalio.FONT, text = "CONNECTED")
        new_label.anchor_point = (0.5, 0.0)
        new_label.anchored_position = (32, 0)
        self._title_group.append(new_label)        

        display.main_group.append(self._title_group)

    def update(self, dt):
        device = self.device
        led_controller = device.led_controller
        audio_controller = device.audio_controller
        switchboard = device.switchboard      

        switchboard.scan()

        if switchboard.did_change:
            audio_controller.eighties_dystopia.skip_to_next_note()

            seven_seg = device.seven_seg
            seven_seg.fill(0)
            seven_seg.show()

            led_controller.fill_switchboard_color((0, 0, 0))

            connections = switchboard.get_connections()
            connection_count = len(connections)

            last_connections = switchboard.get_last_connections()
            last_connection_count = len(last_connections)

            if switchboard.has_connections:
                if connection_count > last_connection_count:
                    audio_controller.play_connection_sfx()
                else:
                    audio_controller.play_disconnection_sfx()

                # 0 and 1 of color_by_index() are black and white; let's skip those.
                skip_indices = 2
                max_color_index = GameState.JACK_COUNT + skip_indices

                for connection in connections:
                    c = color_by_index(connection[0] + skip_indices, max_color_index)
                    led_controller.set_switchboard_color(connection[0], c)
                    c = color_by_index(connection[1] + skip_indices, max_color_index)
                    led_controller.set_switchboard_color(connection[1], c)
            else:
                audio_controller.play_disconnection_sfx()
                led_controller.fill_switchboard_color((0, 0, 0))

                # Prevent circular dependency with local import
                from scene.find_sum.play import FindSumPlay
                next_state = FindSumPlay(self.scene)
                self.goto_next_state(next_state)

    def exit(self):
        display = self.device.display_controller
        display.main_group.remove(self._prompt_group)
        display.main_group.remove(self._title_group)
