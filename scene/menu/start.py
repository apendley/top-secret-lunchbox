from scene.state import SceneState
from scene.menu.selected import MenuSelected

import displayio
import vectorio
import terminalio
from adafruit_display_text import label
from helper import element_exists, animate_pulse
import scenes

from game_state import GameState

class MenuStart(SceneState):
    SB_CENTER_X = 36
    SB_CENTER_SPACE = 0

    def enter(self):
        device = self.device                
        switchboard = device.switchboard    
        display = device.display_controller
        led_controller = device.led_controller
        audio_controller = device.audio_controller

        device.game_state.current_puzzle_index = None

        self._menu_scenes = [
            scenes.COLOR_MATCH,
            scenes.FIND_SUM,
            scenes.SYMBOL_MATCH,
            scenes.REACTION_MATCH,
            scenes.GREMLIN,
        ]

        # Generate menu connections from game state
        self._menu_connections = []

        for i in range(0, GameState.PUZZLE_COUNT):
            self._menu_connections.append(device.game_state.get_puzzle_connection(i))

        self._invalid_connections = []

        # draw separator
        palette = displayio.Palette(1)
        palette[0] = 0xFFFFFF        
        self._display_separator = vectorio.Rectangle(pixel_shader=palette, width=4, height=64, x=62, y=0)
        self._display_separator.hidden = True
        display.main_group.append(self._display_separator)

        # Set up menu labels
        self._menu_labels = []

        for i in range(0, 5):
            jack_name_a = GameState.JACK_NAMES[self._menu_connections[i][0]]
            jack_name_b = GameState.JACK_NAMES[self._menu_connections[i][1]]
            new_label = label.Label(terminalio.FONT, text = f"{jack_name_a} -- {jack_name_b}")
            new_label.anchor_point = (0, 0.5)
            new_label.anchored_position = (0, 5 + i * 13)
            new_label.hidden = True
            self._menu_labels.append(new_label)
            display.main_group.append(new_label)

        # Set up disconnect labels
        self._disconnect_cables_group = displayio.Group(scale=2)
        self._disconnect_cables_group.hidden = True
        display.main_group.append(self._disconnect_cables_group)        

        scaled_width = int(display.WIDTH / 2)
        scaled_height = int(display.HEIGHT / 2)
        center_x = int(scaled_width / 2)
        center_y = scaled_height / 2

        new_label = label.Label(terminalio.FONT, text = "Disconnect")
        new_label.anchor_point = (0.5, 0.5)
        new_label.anchored_position = (center_x, center_y - 5)
        self._disconnect_cables_group.append(new_label)

        new_label = label.Label(terminalio.FONT, text = "to resume")
        new_label.anchor_point = (0.5, 0.5)
        new_label.anchored_position = (center_x, center_y + 5)
        self._disconnect_cables_group.append(new_label)        

        # Initialize connection state
        switchboard.reset_connections()
        switchboard.scan()

        connections = switchboard.get_connections()
        connections_count = len(connections)
        has_connections = connections_count > 0

        self._invalid_connections = connections.copy()

        if has_connections:
            led_controller.fill_switchboard_color((0, 0, 0))
            self._draw_invalid_connection_leds()
        else:
            led_controller.fill_switchboard_color((0, 0, 255))

        self._play_soundtrack_changed()

        # Render menu or disconnect screen
        self._reset_switchboard_renderer()
        if has_connections:
            self._show_disconnect_screen()
        else:
            self._show_menu()

        display.set_switchboard_renderer_active(True)

        self._switchboard_pulse_timer = 0

    def update(self, dt):
        device = self.device 
        switchboard = device.switchboard
        led_controller = device.led_controller
        arcade_button = device.arcade_button

        if arcade_button.fell:
            device.game_state.play_soundtrack = not device.game_state.play_soundtrack
            self._play_soundtrack_changed()
        
        if arcade_button.value == False:
            led_controller.set_button_color((128, 128, 128))

        switchboard.scan(dt)

        if switchboard.did_change:
            connections = switchboard.get_connections()
            connections_count = len(connections)
            has_connections = connections_count > 0

            last_connections = switchboard.get_last_connections()
            last_connections_count = len(last_connections)
            has_last_connections = last_connections_count > 0

            has_invalid_connections = len(self._invalid_connections) > 0

            # Clear switchboard LEDs; we'll redraw any relevant ones.
            led_controller.fill_switchboard_color((0, 0, 0))

            # Remove outdated invalid connections.
            if connections_count < last_connections_count:
                device.audio_controller.eighties_dystopia.skip_to_next_note()
                device.audio_controller.play_disconnection_sfx()

                removed_connections = [i for i in last_connections if i not in connections]
                # print("connection(s) removed:", removed_connections)

                for removed_connection in removed_connections:
                    # Remove any connections from the invalid list that are no longer connected.
                    # NOTE: There is most definitely a more python-y way to do this.
                    removed_connections = []                    

                    if element_exists(removed_connection, in_list=self._invalid_connections):
                        removed_connections.append(removed_connection)

                    for removed in removed_connections:
                        self._invalid_connections.remove(removed)

                if connections_count == 0:
                    self._show_menu()

            # If a new connection is detected, and there are currently invalid connections,
            # add the new connection to the invalid connections. Otherwise, if the new connection
            # is one of the mapped menu connections, go to the corresponding menu.
            # Otherwise, the new connection is invalid, add it to the invalid list.
            elif connections_count > last_connections_count:
                new_connections = [i for i in connections if i not in last_connections]
                # print("connection(s) added:", new_connections)

                has_invalid_connections = len(self._invalid_connections) > 0

                for new_connection in new_connections:
                    if has_invalid_connections:
                        # Add new connections to the invalid connections list
                        self._invalid_connections.append(new_connection)
                        device.audio_controller.play_connection_sfx()
                        device.audio_controller.eighties_dystopia.skip_to_next_note()
                    else:
                        if element_exists(new_connection, in_list=self._menu_connections):
                            menu_index = self._menu_connections.index(new_connection)

                            # has this puzzle already been solved?
                            if device.game_state.is_puzzle_solved(menu_index):
                                self._invalid_connections.append(new_connection)
                                self._show_disconnect_screen()
                            else:
                                device.audio_controller.play_wave_file("audio/confirmation_001.wav")

                                scene_index = self._menu_scenes[menu_index]
                                device.game_state.current_puzzle_index = menu_index

                                for i in range(0, 2):
                                    device.led_controller.set_switchboard_color(new_connection[i], (0, 0, 255))

                                next_state = MenuSelected(self.scene, 
                                                          connection=new_connection,
                                                          scene_index=scene_index,
                                                          scene_name=GameState.PUZZLE_NAMES[menu_index])

                                self.goto_next_state(next_state)
                                return
                        else:
                            self._invalid_connections.append(new_connection)
                            self._show_disconnect_screen()

            # Draw invalid connections
            self._draw_invalid_connection_leds()

        # Pulse the switchboard LEDs when there are no connections
        self._draw_pulse(dt)

    def exit(self):
        device = self.device
        display = device.display_controller

        # Remove UI elements from display
        main_group = display.main_group

        main_group.remove(self._display_separator)

        for label in self._menu_labels:
            main_group.remove(label)

        main_group.remove(self._disconnect_cables_group)

        # Deactivate switchboard renderer
        display.set_switchboard_renderer_active(False)

    def _reset_switchboard_renderer(self):
        sb_renderer = self.device.display_controller.switchboard_renderer
        sb_renderer.set_center_x(self.SB_CENTER_X)
        sb_renderer.set_center_space(self.SB_CENTER_SPACE)
        sb_renderer.hide_labels = False
        sb_renderer.hide_jacks = False

    def _draw_invalid_connection_leds(self):
        for connection in self._invalid_connections:
            for i in range(0, 2):
                self.device.led_controller.set_switchboard_color(connection[i], (255, 0, 0))

    def _show_menu(self):
        device = self.device

        sb_renderer = self.device.display_controller.switchboard_renderer
        sb_renderer.hide_labels = False
        sb_renderer.hide_jacks = False
        sb_renderer.blit()

        for i in range(0, GameState.PUZZLE_COUNT):
            label = self._menu_labels[i]
            label.hidden = device.game_state.is_puzzle_solved(i)

        self._disconnect_cables_group.hidden = True

    def _show_disconnect_screen(self):
        device = self.device

        device.audio_controller.play_connection_sfx()
        device.audio_controller.eighties_dystopia.skip_to_next_note()

        sb_renderer = self.device.display_controller.switchboard_renderer
        sb_renderer.hide_labels = True
        sb_renderer.hide_jacks = True
        sb_renderer.blit()     

        for label in self._menu_labels:
            label.hidden = True

        self._display_separator.hidden = True
        self._disconnect_cables_group.hidden = False

    def _draw_pulse(self, dt):
        device = self.device

        (self._switchboard_pulse_timer, c) = animate_pulse(self._switchboard_pulse_timer, 
                                                           dt=dt, 
                                                           period=2000, 
                                                           color=(0, 0, 255), 
                                                           min_brightness=91,
                                                           offset=64)

        if not device.switchboard.has_connections:
            device.led_controller.fill_switchboard_color(c)

        if device.arcade_button.value == True:
            device.led_controller.set_button_color(c)

    def _play_soundtrack_changed(self):
        device = self.device
        eighties_dystopia = device.audio_controller.eighties_dystopia

        if device.game_state.play_soundtrack:
            # Get note duration based on the number of puzzles solved
            note_duration = device.game_state.note_duration_for_puzzles_solved()
            eighties_dystopia.play(GameState.MAIN_THEME_NOTES,
                                                    note_duration=note_duration)
        else:
            eighties_dystopia.stop()
