from scene import Scene
from scene.reaction_match.start import ReactionMatchStart

from game_state import GameState

class SceneReactionMatch(Scene):

    def __init__(self, device):
        super().__init__(device)

        self._connection_count = 5
        self._round_interval = 3000

        self._symbols = [
            "^",
            "`",
            "g",
            "b",
            "d",
            "_",
            "h",
            "i",
            "c",
            "f"
        ];

        self.current_sequence_index = 0
        self._connection_sequence = GameState.randomized_connections(self._connection_count)

    @property
    def connection_count(self):
        return self._connection_count

    @property
    def round_interval(self):
        return self._round_interval

    @property
    def current_connection(self):
        return self._connection_sequence[self.current_sequence_index]

    def get_symbol(self, index):
        if index >= len(self._symbols):
            return ""

        return self._symbols[index]

    def make_first_state(self):
        return ReactionMatchStart(self)
