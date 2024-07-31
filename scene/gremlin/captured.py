from scene.state import SceneState

import displayio
import terminalio
from adafruit_display_text import label

class GremlinCaptured(SceneState):

    def enter(self):
        device = self.device
        display = device.display_controller
        seven_seg = device.seven_seg
        led_controller = device.led_controller
        switchboard = device.switchboard

        device.audio_controller.play_wave_file("audio/confirmation_001.wav")

        # Clear seven seg
        seven_seg.fill(0)
        seven_seg.show()        

        # Clear LEDs
        self._draw_connections(switchboard.get_connections())
        led_controller.set_button_color((0, 0, 0))

        # Title group
        words = ["GREMLIN", "CAPTURED!"]
        word_count = len(words)

        self._title_group = displayio.Group(scale=2)

        for i in range(0, word_count):
            new_label = label.Label(terminalio.FONT, text = words[i])
            new_label.anchor_point = (0.5, 0.0)
            new_label.anchored_position = (32, 0 + i * 10)
            self._title_group.append(new_label)

        display.main_group.append(self._title_group)

        # Disclaimer group
        self._prompt_group = displayio.Group()

        new_label = label.Label(terminalio.FONT, text="(and returned home)")
        new_label.anchor_point = (0.5, 1.0)
        new_label.anchored_position = (64, 60)
        self._disconnect_label = new_label
        self._prompt_group.append(new_label) 

        display.main_group.append(self._prompt_group)

        self._disconnect_message_timer = 3000
    
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
                # Prevent circular dependency with local import
                from scene.gremlin.start import GremlinStart
                next_state = GremlinStart(self.scene)
                self.goto_next_state(next_state)

        if self._disconnect_message_timer > 0:
            self._disconnect_message_timer -= dt

            if self._disconnect_message_timer <= 0:
                self._disconnect_message_timer = 0
                self._disconnect_label.text = "Disconnect to resume"
                audio_controller.eighties_dystopia.skip_to_next_note()

    def exit(self):
        device = self.device
        display = device.display_controller
        display.main_group.remove(self._title_group)
        display.main_group.remove(self._prompt_group)

    def _draw_connections(self, connections):
        device = self.device
        led_controller = device.led_controller

        led_controller.fill_switchboard_color((0, 0, 0))

        has_connections = len(connections) > 0

        if has_connections:
            for c in connections:
                for i in range(0, 2):
                    device.led_controller.set_switchboard_color(c[i], (0, 255, 0))