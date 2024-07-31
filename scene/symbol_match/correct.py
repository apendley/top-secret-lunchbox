from scene.state import SceneState
from scene.symbol_match.play import SymbolMatchPlay

import displayio
import terminalio
from adafruit_display_text import label

class SymbolMatchCorrect(SceneState):

    def enter(self):
        # Next connection in the sequence
        self.scene.current_sequence_index = min(self.scene.current_sequence_index + 1, self.scene.connection_count - 1)

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

            led_controller.fill_switchboard_color((0, 0, 0))

            connections = switchboard.get_connections()
            connection_count = len(connections)

            last_connections = switchboard.get_last_connections()
            last_connection_count = len(last_connections)

            if connection_count > last_connection_count:
                audio_controller.play_connection_sfx()
            else:
                audio_controller.play_disconnection_sfx()

            if switchboard.has_connections:
                for connection in connections:
                    led_controller.set_switchboard_color(connection[0], (255, 0, 0))
                    led_controller.set_switchboard_color(connection[1], (255, 0, 0))                
            else:
                next_state = SymbolMatchPlay(self.scene)
                self.goto_next_state(next_state)

    def exit(self):
        display = self.device.display_controller
        display.main_group.remove(self._prompt_group)
        display.main_group.remove(self._title_group)
