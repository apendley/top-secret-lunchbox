from scene.state import SceneState
from scene.reaction_match.correct import ReactionMatchCorrect
from scene.common.win import PuzzleWin
from scene.common.lose import PuzzleLose

class ReactionMatchPlay(SceneState):
    COUNTDOWN_DISPLAY_UPDATE_INTERVAL = 60

    def enter(self):
        device = self.device
        led_controller = device.led_controller

        # print("next connection:", self.scene.current_connection)

        c = self.scene.current_connection
        led_controller.set_switchboard_color(c[0], (255, 255, 255))
        led_controller.set_switchboard_color(c[1], (255, 255, 255))      

        self._countdown_timer = self.scene.round_interval
        self._countdown_display_update_timer = self.COUNTDOWN_DISPLAY_UPDATE_INTERVAL

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

                        next_state = ReactionMatchCorrect(self.scene)
                        self.goto_next_state(next_state)
                        return
                    else:
                        next_state = PuzzleWin(self.scene)
                        self.goto_next_state(next_state)
                        return
                else:
                    next_state = PuzzleLose(self.scene)
                    self.goto_next_state(next_state)
                    return

        self._update_countdown(dt)


    def exit(self):
        pass

    def _update_countdown(self, dt):
        self._countdown_timer -= dt
        self._countdown_timer = max(0, self._countdown_timer)

        # Timer expired
        if self._countdown_timer == 0:
            self._show_countdown()

            next_state = PuzzleLose(self.scene)
            self.goto_next_state(next_state)
            return
        else:
            # Keep going
            self._countdown_display_update_timer -= dt

            if self._countdown_display_update_timer <= 0:
                self._countdown_display_update_timer = self.COUNTDOWN_DISPLAY_UPDATE_INTERVAL
                self._show_countdown()         

    def _show_countdown(self):
        self.scene.show_countdown(self._countdown_timer)