import gc

class SceneFSM:
    def __init__(self, scene):
        self._scene = scene
        self._state = None

    @property
    def game(self):
        return self._scene

    @property
    def device(self):
        return self._scene.device

    def set_state(self, state):
        if self._state is not None:
            self._state.exit()
            self._state = None

        gc.collect()
        # print("Free memory:", gc.mem_free())

        self._state = state

        if self._state is not None:
            self._state.enter()

    def update(self, dt):
        if self._state is None:
            return
        
        self._state.update(dt)

    def transition(self):
        next_state = self._state._fsm_next_state

        if next_state is None:
            return
            
        self._state._fsm_next_state = None
        self.set_state(next_state)
