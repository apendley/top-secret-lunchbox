from scene import Scene
from scene.color_match.play import ColorMatchPlay

class SceneColorMatch(Scene):

    def make_first_state(self):
        return ColorMatchPlay(self)