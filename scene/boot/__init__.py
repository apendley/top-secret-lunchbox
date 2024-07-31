from scene import Scene
from scene.boot.start import BootStart

class SceneBoot(Scene):

    def make_first_state(self):
        return BootStart(self)
