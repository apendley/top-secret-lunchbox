from scene import Scene
from scene.win_game.start import WinGameStart

class SceneWinGame(Scene):

    def make_first_state(self):
        return WinGameStart(self)
