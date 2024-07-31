from scene.state import SceneState
from scene.common.lose import PuzzleLose
from scene.common.win import PuzzleWin
from scene.gremlin.captured import GremlinCaptured

import displayio

class GremlinConnectionGremlin(SceneState):

    GREMLIN_IDLE = 0
    GREMLIN_RUN = 1
    GREMLIN_CAUGHT = 2

    GREMLIN_IDLE_DURATION = 1200
    GREMLIN_RUN_DURATION = 1200
    GREMLIN_CAUGHT_DURATION = 2000

    def enter(self):
        device = self.device
        display = device.display_controller
        switchboard = device.switchboard
        led_controller = device.led_controller
        audio_controller = device.audio_controller

        led_controller.fill_switchboard_color((0, 0, 0))
        led_controller.set_button_color((0, 0, 0))

        self.scene.draw_current_connection_id()

        # Add ground sprite
        display.main_group.append(self.scene.ground_sprite)

        # Create scaled group for sprites
        self._sprite_group = displayio.Group(scale=3)
        display.main_group.append(self._sprite_group)

        self._init_gremlin()

        # We really shouldn't even be here if there aren't any connections...
        if switchboard.has_connections:
            connections = switchboard.get_connections()
            self._connection = connections[0]
            
            for i in range(0, 2):
                led_controller.set_switchboard_color(self._connection[i], (0, 255, 0))

        led_controller.set_button_color((0, 0, 255))

    def update(self, dt):
        self._update_gremlin(dt)

        device = self.device
        audio_controller = device.audio_controller
        switchboard = device.switchboard

        switchboard.scan()

        # Messing with the switchboard here is an instant loss
        if switchboard.did_change:
            if switchboard.has_connections:
                audio_controller.play_connection_sfx()
            else:
                audio_controller.play_disconnection_sfx()

            next_state = PuzzleLose(self.scene)
            self.goto_next_state(next_state)
            return

    def exit(self):
        device = self.device
        display = device.display_controller

        display.main_group.remove(self.scene.ground_sprite)
        
        self._sprite_group.remove(self.scene.gremlin_sprite)
        display.main_group.remove(self._sprite_group)

    def _init_gremlin(self):
        self._gremlin_run_x = 0        
        self._set_gremlin_state(self.GREMLIN_IDLE)
        self._sprite_group.append(self.scene.gremlin_sprite)        

    def _set_gremlin_state(self, state):
        self._gremlin_state = state

        if state == self.GREMLIN_IDLE:
            self._gremlin_state_timer = self.GREMLIN_IDLE_DURATION

            self.scene.gremlin_sprite.x = 14
            self.scene.gremlin_sprite.y = 0

            self.scene.gremlin_sprite[0] = 0
        elif state == self.GREMLIN_RUN:
            self.device.audio_controller.play_wave_file("audio/minimize_006.wav")

            self._gremlin_state_timer = self.GREMLIN_RUN_DURATION

            self._gremlin_run_x = 14.0
            self.scene.gremlin_sprite.x = int(self._gremlin_run_x)
            self.scene.gremlin_sprite.y = 0

            self._gremlin_sprite_animation_delay = 75
            self._gremlin_sprite_animation_timer = 0
            self._gremlin_sprite_frame = 0
            self._gremlin_sprite_frame_count = 4
            self.scene.gremlin_sprite[0] = 1

            led_controller = self.device.led_controller
            color = (255, 0, 0)
            led_controller.set_button_color(color)

            for i in range(0, 2):
                led_controller.set_switchboard_color(self._connection[i], color)
        elif state == self.GREMLIN_CAUGHT:
            self.device.audio_controller.play_wave_file("audio/question_001.wav")
            self.device.led_controller.set_button_color((0, 255, 0))
            self._gremlin_state_timer = self.GREMLIN_CAUGHT_DURATION

            self._gremlin_sprite_animation_delay = 100
            self._gremlin_sprite_animation_timer = 0
            self._gremlin_sprite_frame = 0
            self._gremlin_sprite_frame_count = 2
            self.scene.gremlin_sprite[0] = 0

    def _update_gremlin(self, dt):
        if self._gremlin_state == self.GREMLIN_IDLE:
            if self.device.arcade_button.rose:
                    self._set_gremlin_state(self.GREMLIN_CAUGHT)

            self._gremlin_state_timer = max(0, self._gremlin_state_timer - dt)

            if self._gremlin_state_timer == 0:
                self._set_gremlin_state(self.GREMLIN_RUN)
        elif self._gremlin_state == self.GREMLIN_RUN:
            self._animate_gremlin_run(dt)
            self.scene.gremlin_sprite.x = int(self._gremlin_run_x)

            self._gremlin_state_timer = max(0, self._gremlin_state_timer - dt)

            if self._gremlin_state_timer == 0:
                next_state = PuzzleLose(self.scene)
                self.goto_next_state(next_state)
                return
        elif self._gremlin_state == self.GREMLIN_CAUGHT:
            self._animate_gremlin_captured(dt)

            self._gremlin_state_timer = max(0, self._gremlin_state_timer - dt)

            if self._gremlin_state_timer == 0:
                self.scene.set_gremlin_captured(self.scene.current_connection_index)

                if self.scene.gremlins_remaining == 0:
                    next_state = PuzzleWin(self.scene)
                    self.goto_next_state(next_state)
                    return
                else:
                    self.device.audio_controller.eighties_dystopia.skip_to_next_note()
                    next_state = GremlinCaptured(self.scene)
                    self.goto_next_state(next_state)
                    return

    def _animate_gremlin_captured(self, dt):
        self._gremlin_sprite_animation_timer += dt

        if self._gremlin_sprite_animation_timer >= self._gremlin_sprite_animation_delay:
            self._gremlin_sprite_animation_timer -= self._gremlin_sprite_animation_delay
            self._gremlin_sprite_frame +=1

            if self._gremlin_sprite_frame >= self._gremlin_sprite_frame_count:
                self._gremlin_sprite_frame = 0

            if self._gremlin_sprite_frame == 0:
                self.scene.gremlin_sprite[0] = 5
            else:
                self.scene.gremlin_sprite[0] = 0

    def _animate_gremlin_run(self, dt):
        self._gremlin_run_x += dt / 40

        self._gremlin_sprite_animation_timer += dt

        if self._gremlin_sprite_animation_timer >= self._gremlin_sprite_animation_delay:
            self._gremlin_sprite_animation_timer -= self._gremlin_sprite_animation_delay
            self._gremlin_sprite_frame +=1

            if self._gremlin_sprite_frame >= self._gremlin_sprite_frame_count:
                self._gremlin_sprite_frame = 0

            self.scene.gremlin_sprite[0] = self._gremlin_sprite_frame + 1