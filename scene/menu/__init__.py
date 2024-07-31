from scene import Scene
from scene.menu.start import MenuStart

class SceneMenu(Scene):

    def make_first_state(self):
        return MenuStart(self)