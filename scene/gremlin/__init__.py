from scene import Scene
from scene.gremlin.start import GremlinStart

import displayio
import adafruit_imageload
import random
from helper import element_exists

from game_state import GameState

class SceneGremlin(Scene):

    def __init__(self, device):
        super().__init__(device)

        self._gremlin_tileset, self._palette = adafruit_imageload.load("images/little-guy-3.bmp",
                                                                               bitmap=displayio.Bitmap,
                                                                               palette=displayio.Palette)

        self._gremlin_sprite = displayio.TileGrid(self._gremlin_tileset,
                                                  pixel_shader=self._palette,
                                                  width=1,
                                                  height=1,
                                                  tile_width = 16,
                                                  tile_height = 16)


        self._ground_tileset, _ = adafruit_imageload.load("images/ground.bmp",
                                                           bitmap=displayio.Bitmap,
                                                           palette=displayio.Palette)

        self._ground_sprite = displayio.TileGrid(self._ground_tileset,
                                                 pixel_shader=self._palette,
                                                 width=8,
                                                 height=2,
                                                 tile_width = 16,
                                                 tile_height = 16,
                                                 default_tile = 5)

        self._ground_sprite.y = 50

        ground_map = [0, 1, 1, 1, 1, 1, 1, 2,]

        for i in range(0, len(ground_map)):
            self._ground_sprite[i] = ground_map[i]

        self._connections = []

        # 45 possible connections with a single cable
        for q in range(0, GameState.JACK_COUNT - 1):
            for t in range(q + 1, GameState.JACK_COUNT):
                self._connections.append((GameState.make_connection(q, t)))

        # Populate 5 of the rooms with gremlins
        self._gremlin_count = 5
        self._gremlins_captured = 0
        self._gremlin_locations = []

        for i in range(0, self._gremlin_count):
            new_index = random.randrange(0, 45)

            while any(l == new_index for l in self._gremlin_locations):
                new_index = random.randrange(0, 45)

            self._gremlin_locations.append(new_index)

        self._gremlin_locations = sorted(self._gremlin_locations)

        # print(self._gremlin_locations)

        self._current_connection_index = None

    def make_first_state(self):
        return GremlinStart(self)

    @property
    def connection_count(self):
        return len(self._connections)

    @property
    def gremlin_count(self):
        return self._gremlin_count

    @property
    def gremlins_captured(self):
        return self._gremlins_captured

    @property
    def gremlins_remaining(self):
        return self._gremlin_count - self._gremlins_captured

    @property
    def gremlin_tileset(self):
        return self._gremlin_tileset

    @property
    def gremlin_sprite(self):
        return self._gremlin_sprite

    @property
    def ground_tileset(self):
        return self._ground_tileset

    @property
    def ground_sprite(self):
        return self._ground_sprite

    @property
    def palette(self):
        return self._palette

    @property
    def current_connection_index(self):
        return self._current_connection_index

    @current_connection_index.setter
    def current_connection_index(self, index):
        if index is not None and index >= len(self._connections):
            return

        self._current_connection_index = index

    @property
    def is_gremlin_present(self):
        if self._current_connection_index is None:
            return False

        return any(l == self._current_connection_index for l in self._gremlin_locations)

    def get_connection_index(self, connection):
        for i in range(0, len(self._connections)):
            if connection == self._connections[i]:
                return i

        return None

    def contains_gremlin(self, connection_index):
        return any(l == connection_index for l in self._gremlin_locations)

    def distance_to_closest_gremlin(self):
        if self.gremlins_remaining == 0 or self._current_connection_index is None:
            return self.connection_count - 1

        closest = None

        for i in range(0, len(self._gremlin_locations)):
            dist = abs(self._current_connection_index - self._gremlin_locations[i])
            # print(f"\ndistance[{i}]: {dist}")

            if closest == None or dist < closest:
                closest = dist

        return closest


    def set_gremlin_captured(self, connection_index):
        if connection_index is None:
            return

        if element_exists(connection_index, in_list=self._gremlin_locations):
            self._gremlins_captured += 1

            self._gremlin_locations.remove(connection_index)

    def draw_current_connection_id(self):
        if self._current_connection_index is None:
            return

        # print("self.device:", self.device)

        seven_seg = self.device.seven_seg

        text = " {:2} ".format(self._current_connection_index + 1)
        seven_seg.print(text)
        seven_seg.show()
