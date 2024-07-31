from scene.boot import SceneBoot
from scene.menu import SceneMenu
from scene.color_match import SceneColorMatch
from scene.find_sum import SceneFindSum
from scene.symbol_match import SceneSymbolMatch
from scene.reaction_match import SceneReactionMatch
from scene.gremlin import SceneGremlin
from scene.win_game import SceneWinGame

import gc

class Application:
    def __init__(self, device):
        self._device = device
        self._scene = None
        self._next_scene_class = None

        self._scene_classes = [
            SceneBoot,
            SceneMenu,
            SceneColorMatch,
            SceneFindSum,
            SceneSymbolMatch,
            SceneReactionMatch,
            SceneGremlin,
            SceneWinGame
        ]

    @property
    def scene(self):
        return self._scene

    @property
    def device(self):
        return self._device

    def update(self, dt):
        if self._scene is not None:
            self._scene.update(dt)

        if self._next_scene_class is not None:
            next_scene = self._next_scene_class(self._device)
            self._next_scene_class = None
            self._goto_scene(next_scene)

        self.device.audio_controller.update(dt)

    def goto_scene(self, scene_index):
        if scene_index >= len(self._scene_classes):
            return

        self._next_scene_class = self._scene_classes[scene_index]

    def _goto_scene(self, scene):
        if self._scene is not None:
            self._scene.exit()
            self._scene.application = None

        gc.collect()
        self._scene = scene

        if scene is not None:
            self._scene.application = self
            scene.enter()
