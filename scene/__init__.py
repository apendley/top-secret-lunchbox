from scene.fsm import SceneFSM

class Scene:
    def __init__(self, device):
        self._device = device
        self._application = None
        self._fsm = SceneFSM(self)

    # Subclasses must override this and return the initial state.
    def make_first_state(self):
        return None

    @property
    def device(self):
        return self._device

    # Set by the application before calling enter(), and set to None after calling exit().
    @property
    def application(self):
        return self._application

    @application.setter
    def application(self, app):
        self._application = app

    # These are intended to be called by the application.
    def enter(self):
        first_state = self.make_first_state()

        if first_state is None:
            return

        self._fsm.set_state(first_state)

    def update(self, dt):
        device = self.device

        device.arcade_button.update()
        self._fsm.update(dt)
        device.led_controller.update()
        self._fsm.transition()

    def exit(self):
        self._fsm.set_state(None)

    def show_countdown(self, time, show_colon=True):
        device = self.device

        second = int(time / 1000)
        hundredths = int(time % 100)
        time_text = "{: 2}{:02}".format(second, hundredths)
        device.seven_seg.colon = show_colon
        device.seven_seg.print(time_text)
        device.seven_seg.show()        