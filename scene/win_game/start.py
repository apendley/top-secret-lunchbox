from scene.state import SceneState
from scene.win_game.connect import WinGameConnect

class WinGameStart(SceneState):

    def enter(self):
        device = self.device
        led_controller = device.led_controller
        audio_controller = device.audio_controller
        seven_seg = device.seven_seg

        audio_controller.eighties_dystopia.stop()        
        audio_controller.wave_volume = 0.9

        seven_seg.fill(0)
        seven_seg.show()

        led_controller.set_button_color((0, 0, 0))
        led_controller.fill_switchboard_color((0, 0, 0))

        self._wait_timer = 1000

    def update(self, dt):
        self._wait_timer = max(self._wait_timer - dt, 0)

        if self._wait_timer == 0:
            next_state = WinGameConnect(self.scene)
            self.goto_next_state(next_state)

    def exit(self):
        pass