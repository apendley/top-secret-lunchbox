import board
import digitalio
import random
from helper import element_exists
from game_state import GameState

class Switchboard:
    def __init__(self, *pin_names_params):
        pin_names = list(pin_names_params)

        self._pin_count = len(pin_names)
        self._state = [None] * self._pin_count
        self._last_state = [None] * self._pin_count
        self._pins = [None] * self._pin_count

        # Set all pins to input with pull-ups
        for pin_index in range(0, self._pin_count):
            pin = digitalio.DigitalInOut(pin_names[pin_index])
            pin.direction = digitalio.Direction.INPUT
            pin.pull = digitalio.Pull.UP
            self._pins[pin_index] = pin

    @property 
    def pin_count(self):
        return self._pin_count

    # Resets connection state
    def reset_connections(self):
        self._last_state = [None] * self._pin_count
        self._state = [None] * self._pin_count

    # Scan and update connection state
    def scan(self, dt=0):
        for pin_index in range(0, self._pin_count):
            self._last_state[pin_index] = self._state[pin_index]
            self._state[pin_index] = None

        # With this algorithm takes up to 45 calls to 
        # _are_pins_connected() to scan entire switchboard.
        for q in range(0, self._pin_count - 1):
            if self._state[q] is None:
                for t in range(q + 1, self._pin_count):
                    if self._are_pins_connected(q, t):
                        self._state[q] = t
                        self._state[t] = q
                        break

    # Returns true if last scan does not match the scan before it
    @property
    def did_change(self):
        for pin_index in range(0, self._pin_count):
            if self._last_state[pin_index] != self._state[pin_index]:
                return True

        return False

    # Returns true if there are any connections
    @property 
    def has_connections(self):
        return any(p != None for p in self._state)

    # Return all connections since the last scan
    def get_connections(self):
        connections = []

        for pin_index in range(0, self._pin_count):
            other_pin_index = self._state[pin_index]
            
            if other_pin_index is not None:
                exists_1 = element_exists((pin_index, other_pin_index), in_list=connections)
                exists_2 = element_exists((other_pin_index, pin_index), in_list=connections)

                if not (exists_1 or exists_2):
                    connections.append(GameState.make_connection(pin_index, other_pin_index))

        return connections

    # Return connections from before the last scan
    def get_last_connections(self):
        connections = []

        for pin_index in range(0, self._pin_count):
            other_pin_index = self._last_state[pin_index]

            if other_pin_index is not None:
                exists_1 = element_exists((pin_index, other_pin_index), in_list=connections)
                exists_2 = element_exists((other_pin_index, pin_index), in_list=connections)

                if not (exists_1 or exists_2):
                    connections.append(GameState.make_connection(pin_index, other_pin_index))

        return connections        

    ####################
    # Helper
    ####################

    # Given a list of connections, return the connection index that the switchboard_index is connected to (or None if not connected)
    def connection_index(self, connections, switchboard_index):
        for c in range(0, len(connections)):
            if connections[c][0] == switchboard_index or connections[c][1] == switchboard_index:
                return c

        return None

    ####################
    # Private
    ####################

    def _are_pins_connected(self, output_index, input_index):
        output_pin = self._pins[output_index]
        input_pin = self._pins[input_index]

        # To test whether the pins are connected, set the first as output and the second as input
        output_pin.direction = digitalio.Direction.OUTPUT

        # Set the output pin low
        output_pin.value = False

        # If connected, the low signal should be detected on the input pin,
        is_connected = (input_pin.value == False)

        # Set the output pin back to its default state
        output_pin.direction = digitalio.Direction.INPUT
        output_pin.pull = digitalio.Pull.UP

        return is_connected