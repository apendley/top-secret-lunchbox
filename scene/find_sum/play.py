from scene.state import SceneState
from scene.find_sum.correct import FindSumCorrect
from scene.common.win import PuzzleWin

import random
import displayio
import terminalio
from adafruit_display_text import label
from helper import color_by_index

from game_state import GameState

class FindSumPlay(SceneState):
    def enter(self):
        device = self.device
        display = device.display_controller
        switchboard = device.switchboard

        text_scale = 5
        scaled_width = int(display.WIDTH / text_scale)
        scaled_height = int(display.HEIGHT / text_scale)
        center_x = int(scaled_width / 2) + (text_scale / 2.5)
        center_y = int(scaled_height / 2)

        self._magic_number_group = displayio.Group(scale=text_scale)
        display.main_group.append(self._magic_number_group)

        if not self.scene.is_puzzle_solved:
            self._magic_number_label = label.Label(terminalio.FONT, text=str(self.scene.current_magic_number))
            self._magic_number_label.anchor_point = (0.5, 0.5)
            self._magic_number_label.anchored_position = (center_x, center_y)
            self._magic_number_group.append(self._magic_number_label)

        self._switchboard_sum = self._sum_connections(switchboard.get_connections())
        self._draw_switchboard_sum()

    def update(self, dt):
        device = self.device
        led_controller = device.led_controller

        switchboard = device.switchboard
        switchboard.scan(dt)

        if switchboard.did_change:
            device.audio_controller.eighties_dystopia.skip_to_next_note()

            connections = switchboard.get_connections()

            # 0 and 1 of color_by_index() are black and white; let's skip those.
            skip_indices = 2
            max_color_index = GameState.JACK_COUNT + skip_indices

            # Clear all LEDs and just redraw relevant ones
            led_controller.fill_switchboard_color((0, 0, 0))

            for connection in connections:
                c = color_by_index(connection[0] + skip_indices, max_color_index)
                led_controller.set_switchboard_color(connection[0], c)
                c = color_by_index(connection[1] + skip_indices, max_color_index)
                led_controller.set_switchboard_color(connection[1], c)

            self._switchboard_sum = self._sum_connections(connections)
            self._draw_switchboard_sum()

            if self._switchboard_sum == self.scene.current_magic_number:
                self.scene.next_magic_number()

                if self.scene.is_puzzle_solved:
                    next_state = PuzzleWin(self.scene)
                    self.goto_next_state(next_state)
                    return
                else:
                    # Prevent circular dependency with local import
                    # from scene.find_sum.correct import FindSumCorrect
                    next_state = FindSumCorrect(self.scene)
                    self.goto_next_state(next_state)
                    return                    
            else:
                connections_count = len(connections)
                has_connections = connections_count > 0

                last_connections = switchboard.get_last_connections()
                last_connections_count = len(last_connections)

                if last_connections_count < connections_count:
                    device.audio_controller.play_connection_sfx()
                elif last_connections_count > connections_count:
                    device.audio_controller.play_disconnection_sfx()


    def exit(self):
        self.device.display_controller.main_group.remove(self._magic_number_group)

    def _sum_connections(self, connections):
        cable_sum = 0

        for i in range(0, len(connections)):
            c = connections[i]
            cable_sum += c[0]
            cable_sum += c[1]

        return cable_sum

    def _draw_switchboard_sum(self):
        if self._switchboard_sum == 0:
            self.device.seven_seg.fill(0)
        else:
            text = " {:2} ".format(self._switchboard_sum)
            self.device.seven_seg.print(text)

        self.device.seven_seg.show()
