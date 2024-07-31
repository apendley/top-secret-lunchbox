from scene.state import SceneState
from scene.gremlin.connection_gremlin import GremlinConnectionGremlin
from scene.gremlin.connection_no_gremlin import GremlinConnectionNoGremlin

import displayio
import terminalio
from adafruit_display_text import label

class GremlinStart(SceneState):

    def enter(self):
        device = self.device
        display = device.display_controller
        led_controller = device.led_controller
        seven_seg = device.seven_seg

        self.scene.current_connection_index = None

        # Clear seven seg
        seven_seg.fill(0)
        seven_seg.show()

        # Clear LEDs
        led_controller.fill_switchboard_color((0, 0, 0))
        led_controller.set_button_color((0, 0, 0))

        # Title group
        words = ["MAKE A", "CONNECTION"]
        word_count = len(words)

        self._title_group = displayio.Group(scale=2)

        for i in range(0, word_count):
            new_label = label.Label(terminalio.FONT, text = words[i])
            new_label.anchor_point = (0.5, 0.0)
            new_label.anchored_position = (32, 0 + i * 10)
            self._title_group.append(new_label)

        display.main_group.append(self._title_group)

        # Prompt group
        self._tally_group = displayio.Group()

        new_label = label.Label(terminalio.FONT, text = f"{self.scene.gremlins_remaining}/5 gremlins remain")
        new_label.anchor_point = (0.5, 1.0)
        new_label.anchored_position = (64, 60)
        self._tally_group.append(new_label) 

        display.main_group.append(self._tally_group)
    
    def update(self, dt):
        device = self.device
        switchboard = device.switchboard

        switchboard.scan()

        if switchboard.did_change:
            connections = switchboard.get_connections()
            connections_count = len(connections)
            has_connections = connections_count > 0

            if has_connections:
                c = connections[0]

                connection_index = self.scene.get_connection_index(c)
                self.scene.current_connection_index = connection_index

                # Should not be possible, but still...
                if connection_index is not None:
                    device.audio_controller.play_connection_sfx()
                    device.audio_controller.eighties_dystopia.skip_to_next_note()
                    
                    if self.scene.contains_gremlin(connection_index):
                        next_state = GremlinConnectionGremlin(self.scene)
                        self.goto_next_state(next_state)
                    else:
                        next_state = GremlinConnectionNoGremlin(self.scene)
                        self.goto_next_state(next_state)                        

    def exit(self):
        device = self.device
        display = device.display_controller
        display.main_group.remove(self._title_group)
        display.main_group.remove(self._tally_group)