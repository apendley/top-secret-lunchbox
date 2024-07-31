from scene.state import SceneState
from scene.boot.finish import BootFinish

class BootWait(SceneState):

    def enter(self):
        self._wait_timer = 1000

    def update(self, dt):
        self._wait_timer = max(self._wait_timer - dt, 0)

        if self._wait_timer == 0:
            next_state = BootFinish(self.scene)
            self.goto_next_state(next_state)

    def exit(self):
        pass