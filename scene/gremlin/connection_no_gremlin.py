from scene.state import SceneState
from scene.common.lose import PuzzleLose

from helper import map_range, gamma8

class GremlinConnectionNoGremlin(SceneState):

    def enter(self):
        device = self.device
        display = device.display_controller
        switchboard = device.switchboard
        led_controller = device.led_controller

        device.led_controller.fill_switchboard_color((0, 0, 0))
        device.led_controller.set_button_color((0, 0, 0))

        self.scene.draw_current_connection_id()

        display.main_group.append(self.scene.ground_sprite)

        # print("closest gremlin distance:", self.scene.distance_to_closest_gremlin())

        # We really shouldn't even be here if there aren't any connections...
        if switchboard.has_connections:
            connections = switchboard.get_connections()
            first_connection = connections[0]
            
            # Adjust brightness based on distance to nearest gremlin            
            cutoff = 5
            closest = self.scene.distance_to_closest_gremlin()

            if closest <= cutoff:
                closest = min(closest, cutoff)

                b = map_range(closest, 1, cutoff, 255, 91)
                b = int(b)
                color = (0, b, 0)
                color = gamma8(color)

                led_controller.set_switchboard_color(first_connection[0], color)
                led_controller.set_switchboard_color(first_connection[1], color)
            else:
                color = gamma8((0, 0, 100))
                led_controller.set_switchboard_color(first_connection[0], color)
                led_controller.set_switchboard_color(first_connection[1], color)

    def update(self, dt):
        device = self.device
        switchboard = device.switchboard
        audio_controller = device.audio_controller

        switchboard.scan()

        if switchboard.did_change:
            if switchboard.has_connections:
                audio_controller.play_connection_sfx()

                next_state = PuzzleLose(self.scene)
                self.goto_next_state(next_state)
                return
            else:
                audio_controller.play_disconnection_sfx()
                audio_controller.eighties_dystopia.skip_to_next_note()

                # Prevent circular dependency with local import
                from scene.gremlin.start import GremlinStart
                next_state = GremlinStart(self.scene)
                self.goto_next_state(next_state)
                return

    def exit(self):
        self.device.display_controller.main_group.remove(self.scene.ground_sprite)