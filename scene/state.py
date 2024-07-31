
class SceneState:
    def __init__(self, scene):
        self._scene = scene
        self._fsm_next_state = None

    @property
    def application(self):
        return self._scene.application

    @property
    def scene(self):
        return self._scene

    @property
    def device(self):
        return self._scene.device

    def goto_next_state(self, scene_state):
        self._fsm_next_state = scene_state

    def enter(self):
        pass

    def update(self, dt):
        pass

    def exit(self):
        pass