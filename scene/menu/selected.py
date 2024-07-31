from scene.state import SceneState

from helper import clamp
import displayio
import terminalio
from adafruit_display_text import label

from game_state import GameState

class MenuSelected(SceneState):

    def __init__(self, scene, connection, scene_index, scene_name):
        super().__init__(scene)    
        self._connection = connection
        self._scene_index = scene_index
        self._scene_name = scene_name

    def enter(self):
        device = self.device
        display = device.display_controller

        device.audio_controller.eighties_dystopia.skip_to_next_note()

        device.led_controller.set_button_color((0, 0, 0))

        for i in range(0, 2):
            device.led_controller.set_switchboard_color(self._connection[i], (255, 0, 255))

        # Test name group
        # Split on space, and up to first two words will be displayed on their own line.
        words = self._scene_name.split(" ")
        word_count = clamp(len(words), 1, 2)

        self._title_group = displayio.Group(scale=2)

        for i in range(0, word_count):
            new_label = label.Label(terminalio.FONT, text = words[i])
            new_label.anchor_point = (0.5, 0.0)
            new_label.anchored_position = (32, 0 + i * 10)
            self._title_group.append(new_label)

        display.main_group.append(self._title_group)

        # Prompt group
        self._prompt_group = displayio.Group()

        new_label = label.Label(terminalio.FONT, text = "Disconnect to resume")
        new_label.anchor_point = (0.5, 1.0)
        new_label.anchored_position = (64, 60)
        self._prompt_group.append(new_label)        

        display.main_group.append(self._prompt_group)

    def update(self, dt):
        device = self.device                
        switchboard = device.switchboard
        led_controller = device.led_controller
        audio_controller = device.audio_controller

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
                audio_controller.eighties_dystopia.skip_to_next_note()

                # Lower volume when solving puzzles
                audio_controller.synth_volume = device.audio_controller.low_synth_volume            

                self.application.goto_scene(self._scene_index)

    def exit(self):
        device = self.device

        main_group = device.display_controller.main_group
        main_group.remove(self._prompt_group)
        main_group.remove(self._title_group)

        device.led_controller.fill_switchboard_color((0, 0, 0))