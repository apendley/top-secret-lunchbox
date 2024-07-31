from scene import Scene
from scene.find_sum.play import FindSumPlay

import random

class SceneFindSum(Scene):
    ROUND_COUNT = 5

    def __init__(self, device):
        super().__init__(device)

        self._current_magic_number_index = 0
        self._magic_numbers = []

        for i in range(0, self.ROUND_COUNT):
            # Using value 0-9 for the jack values, and allowing for use of up to 5 cables,
            # the range of possible sum values is between 1 and 45.
            next_number = random.randrange(1, 46)

            # Make sure new number is not a duplicate of any other items in list
            while any(next_number == n for n in self._magic_numbers):
                next_number = random.randrange(1, 46)
            
            self._magic_numbers.append(next_number)

        # print("magic numbers:", self._magic_numbers)

    @property
    def magic_number_count(self):
        return len(self._magic_numbers)

    @property
    def current_magic_number(self):
        if self._current_magic_number_index >= self.ROUND_COUNT:
            return None

        return self._magic_numbers[self._current_magic_number_index]

    @property 
    def is_puzzle_solved(self):
        return self.current_magic_number is None
    
    def next_magic_number(self):
        self._current_magic_number_index = min(self._current_magic_number_index + 1, self.ROUND_COUNT)

    def make_first_state(self):
        return FindSumPlay(self)
