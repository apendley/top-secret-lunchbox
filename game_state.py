import random

class PuzzleState:
    def __init__(self, identifier, connection, is_solved=False):
        self._identifier = None        
        self._connection = connection
        self.is_solved = is_solved

    @property
    def identifier(self):
        return self._identifier

    @property
    def connection(self):
        return self._connection

class GameState:
    JACK_COUNT = 10
    JACK_NAMES = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]

    CONNECTION_COUNT = int(JACK_COUNT / 2)

    PUZZLE_COUNT = CONNECTION_COUNT
    PUZZLE_NAMES = ["SPECTRAL DISPATCH", "ADDITIVE DISPATCH", "SYMBOLIC DISPATCH", "TEMPORAL DISPATCH", "GREMLIN DISPATCH"]

    MAIN_THEME_NOTES = (38, 46, 50, 49, 51)    

    def __init__(self):
        connections = GameState.randomized_connection_set()

        self._puzzle_states = []

        for i in range(0, GameState.PUZZLE_COUNT):
            s = PuzzleState(i, connections[i])
            self._puzzle_states.append(s)

        self.current_puzzle_index = None

        self.play_soundtrack = True        

    def is_puzzle_solved(self, identifier):
        if identifier >= len(self._puzzle_states):
            return None

        return self._puzzle_states[identifier].is_solved

    def set_puzzle_solved(self, identifier, value):
        if identifier >= len(self._puzzle_states):
            return

        self._puzzle_states[identifier].is_solved = value

    def get_puzzle_connection(self, identifier):
        if identifier >= len(self._puzzle_states):
            return None

        return self._puzzle_states[identifier].connection

    @property
    def all_puzzles_solved(self):
        return all(puzzle_state.is_solved == True for puzzle_state in self._puzzle_states)

    @property
    def num_puzzles_solved(self):
        solved = 0

        for i in range(0, GameState.PUZZLE_COUNT):
            if self._puzzle_states[i].is_solved:
                solved += 1
                
        return solved

    def note_duration_for_puzzles_solved(self):
        solved = self.num_puzzles_solved
        note_duration = 9000

        for _ in range(0, solved):
            note_duration /= 2.33

        # print(f"SOLVED: {solved}, note duration: {note_duration}")
        return int(note_duration)

    ####################
    # static helpers
    ####################
    # Returns a valid connection tuple ensuring connection[0] <= connection[1]
    def make_connection(jack_index_a, jack_index_b):
        if jack_index_a <= jack_index_b:
            return (jack_index_a, jack_index_b)
        else:
            return (jack_index_b, jack_index_a)

    # Returns a list of randomized connections from available jacks.
    # All jacks should be filled, and none should be reused in the entire set of connections.
    def randomized_connection_set():
        jack_inputs = sorted(range(GameState.JACK_COUNT), 
                             key=lambda x: random.randrange(0, GameState.JACK_COUNT))

        connections = []

        for i in range(0, GameState.CONNECTION_COUNT):
            jack_index_a = jack_inputs[i*2+0]
            jack_index_b = jack_inputs[i*2+1]

            connection = GameState.make_connection(jack_index_a, jack_index_b)
            connections.append(connection)

        return connections

    # Returns a list of randomized connections from available jacks.
    # Jacks may be reused in multiple connections.
    def randomized_connections(connection_count=CONNECTION_COUNT):
        connections = []

        for i in range(0, connection_count):
            connection = None

            while connection is None or any(c == connection for c in connections):
                jack_index_a = random.randrange(0, GameState.JACK_COUNT)
                jack_index_b = random.randrange(0, GameState.JACK_COUNT)

                # Can't connect a jack to itself
                while jack_index_b == jack_index_a:
                    jack_index_b = random.randrange(0, GameState.JACK_COUNT)

                connection = GameState.make_connection(jack_index_a, jack_index_b)

            connections.append(connection)

        return connections
