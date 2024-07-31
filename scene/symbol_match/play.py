from scene.state import SceneState
from scene.common.win import PuzzleWin
from scene.common.lose import PuzzleLose

import displayio
import vectorio
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

from game_state import GameState

class SymbolMatchPlay(SceneState):

    def enter(self):
        device = self.device
        display = device.display_controller

        # print("next connection:", self.scene.current_connection)        

        wingdings_font = bitmap_font.load_font("fonts/Wingdings-Regular-32.bdf")

        self._connection_group = displayio.Group()

        self._label_a = label.Label(wingdings_font, text=self._current_jack_name_a())
        self._label_a.anchor_point = (0.0, 0.5)
        self._label_a.anchored_position = (8, 32)
        self._connection_group.append(self._label_a)

        self._label_b = label.Label(wingdings_font, text=self._current_jack_name_b())
        self._label_b.anchor_point = (1.0, 0.5)
        self._label_b.anchored_position = (120, 32)
        self._connection_group.append(self._label_b)

        palette = displayio.Palette(1)
        palette[0] = 0xFFFFFF

        self._connector_line = vectorio.Rectangle(pixel_shader=palette, width=20, height=4, x=54, y=32)
        self._connection_group.append(self._connector_line)

        display.main_group.append(self._connection_group)

    def update(self, dt):
        device = self.device
        led_controller = device.led_controller

        switchboard = device.switchboard
        switchboard.scan(dt)

        if switchboard.did_change:
            device.audio_controller.eighties_dystopia.skip_to_next_note()

            if switchboard.has_connections:
                connections = switchboard.get_connections()
                first_connection = connections[0]

                if first_connection == self.scene.current_connection:
                    if self.scene.current_sequence_index < self.scene.connection_count - 1:
                        led_controller.set_switchboard_color(first_connection[0], (0, 255, 0))
                        led_controller.set_switchboard_color(first_connection[1], (0, 255, 0))

                        # Prevent circular dependency with local import
                        from scene.symbol_match.correct import SymbolMatchCorrect
                        next_state = SymbolMatchCorrect(self.scene)
                        self.goto_next_state(next_state)
                    else:
                        next_state = PuzzleWin(self.scene)
                        self.goto_next_state(next_state)
                else:
                    device.audio_controller.play_connection_sfx()
                    next_state = PuzzleLose(self.scene)
                    self.goto_next_state(next_state)

    def exit(self):
        self.device.display_controller.main_group.remove(self._connection_group)

    def _current_jack_name_a(self):
        return self.scene.get_symbol(self.scene.current_connection[0])

    def _current_jack_name_b(self):
        return self.scene.get_symbol(self.scene.current_connection[1])