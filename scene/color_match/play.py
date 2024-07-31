from scene.state import SceneState
from scene.common.win import PuzzleWin
from scene.common.lose import PuzzleLose

import displayio
import terminalio
from adafruit_display_text import label

from game_state import GameState

class ColorMatchPlay(SceneState):
    COUNTDOWN_SECONDS = 60
    COUNTDOWN_DISPLAY_UPDATE_INTERVAL = 60

    CONNECTION_COLORS = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (255, 0, 255),
    ]    

    def enter(self):
        device = self.device

        self._target_connections = GameState.randomized_connection_set()
        self._connection_attempts_remaining = 11

        self._has_countdown_started = False
        self._countdown_timer = self.COUNTDOWN_SECONDS * 1000
        self._countdown_display_update_timer = self.COUNTDOWN_DISPLAY_UPDATE_INTERVAL

        device.led_controller.set_button_color((0, 0, 0))

        self._init_intro_card_group()
        self._init_attempts_value_group()
        self._init_attempts_title_group()

    def update(self, dt):
        device = self.device
        led_controller = device.led_controller

        self._update_switchboard(dt)
        led_controller.update()
        self._update_countdown(dt)

    def exit(self):
        display_main_group = self.device.display_controller.main_group
        display_main_group.remove(self._intro_card_group)
        display_main_group.remove(self._attempts_value_group)
        display_main_group.remove(self._attempts_title_group)

    def _update_switchboard(self, dt):
        device = self.device
        led_controller = device.led_controller

        switchboard = device.switchboard
        switchboard.scan(dt)

        if switchboard.did_change:
            device.audio_controller.eighties_dystopia.skip_to_next_note()

            connections = switchboard.get_connections()
            connections_count = len(connections)
            has_connections = connections_count > 0

            last_connections = switchboard.get_last_connections()
            last_connections_count = len(last_connections)
            has_last_connections = last_connections_count > 0

            led_controller.fill_switchboard_color((0, 0, 0))

            if has_connections:
                for connection in connections:
                    for i in range(0, 2):
                        connection_index = switchboard.connection_index(connections=self._target_connections,
                                                                        switchboard_index=connection[i])

                        color = self.CONNECTION_COLORS[connection_index]
                        led_controller.set_switchboard_color(connection[i], color)

                # If all target connections are made, go to win state
                if len(connections) == len(self._target_connections):
                    all_connections_complete = True

                    for target_connection in self._target_connections:
                        if not any(c == target_connection for c in connections):
                            all_connections_complete = False
                            break

                    if all_connections_complete:
                        next_state = PuzzleWin(self.scene)
                        self.goto_next_state(next_state)
                        return

            if connections_count > last_connections_count:
                new_connections = [i for i in connections if i not in last_connections]

                self._connection_attempts_remaining -= len(new_connections)
                self._connection_attempts_remaining = max(0, self._connection_attempts_remaining)

                # If the user has run out of turns, go to lose state
                if self._connection_attempts_remaining == 0:
                    next_state = PuzzleLose(self.scene)
                    self.goto_next_state(next_state)
                    return

                # Update label
                self._attempts_label.text = str(self._connection_attempts_remaining)

                # Start the timer and update the oled
                if not self._has_countdown_started:
                    self._has_countdown_started = True
                    self._intro_card_group.hidden = True
                    self._attempts_value_group.hidden = False
                    self._attempts_title_group.hidden = False      

                # Play sound effect for new connection
                if len(new_connections) > 0:
                    first_new_connection = new_connections[0]

                    conn_0 = switchboard.connection_index(connections=self._target_connections, 
                                                          switchboard_index=first_new_connection[0])

                    conn_1 = switchboard.connection_index(connections=self._target_connections, 
                                                          switchboard_index=first_new_connection[1])

                    if conn_0 == conn_1:
                        device.audio_controller.play_wave_file("audio/confirmation_001.wav")
                    else:
                        device.audio_controller.play_connection_sfx()

            elif connections_count < last_connections_count:
                device.audio_controller.play_disconnection_sfx()

    def _init_intro_card_group(self):
        display = self.device.display_controller

        group = displayio.Group()
        lines = ["Make a connection", "to begin", "spectral dispatch"]

        for i in range(0, len(lines)):
            new_label = label.Label(terminalio.FONT, text=lines[i])
            new_label.anchor_point = (0.5, 1.0)
            new_label.anchored_position = (64, 22 + i * 12)
            group.append(new_label)            

        display.main_group.append(group)
        self._intro_card_group = group

    def _init_attempts_value_group(self):
        display = self.device.display_controller

        group = displayio.Group(scale=3)
        group.hidden = True

        new_label = label.Label(terminalio.FONT, text = str(self._connection_attempts_remaining))
        new_label.anchor_point = (0.5, 0.0)
        new_label.anchored_position = (int(display.WIDTH/6), 0)
        group.append(new_label)
        self._attempts_label = new_label        

        display.main_group.append(group)
        self._attempts_value_group = group        

    def _init_attempts_title_group(self):
        display = self.device.display_controller

        group = displayio.Group(scale=1)
        group.hidden = True        

        center_x = int(display.WIDTH / 2)

        lines = ["attempts", "remaining"]

        for i in range(0, len(lines)):
            new_label = label.Label(terminalio.FONT, text = lines[i])
            new_label.anchor_point = (0.5, 0.0)
            new_label.anchored_position = (center_x, 34 + i * 10)
            group.append(new_label)

        display.main_group.append(group)
        self._attempts_title_group = group

    def _update_countdown(self, dt):
        if not self._has_countdown_started:
            return

        self._countdown_timer -= dt

        # Timer expired
        if self._countdown_timer <= 0:
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
        self.scene.show_countdown(self._countdown_timer, show_colon=self._countdown_timer % 1000 > 500)

