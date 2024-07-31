import displayio
import vectorio
import terminalio
from adafruit_display_text import label

from game_state import GameState

# Ideally, we'd just lump all the sprites in a group, and then add/remove that group
# to a parent group. Currently however there seems to be a bug where the display state of
# vectorio objects in a group is not updated when it's parent group is removed from *its*
# parent group. To work around this, we're just keeping track of each vectorio shape
# and adding/removing them manually from the display group that's rendering them.

class SwitchboardRenderer:

    RADIUS = 5
    COLS = [-1, 1]
    ROW_COUNT = 5

    def __init__(self):
        self._jack_sprites = []
        self._hide_labels = True
        self._hide_jacks = False
        self._center_x = 0
        self._center_space = 0

        # Set up palettes
        outer_palette = displayio.Palette(1)
        outer_palette[0] = 0xFFFFFF

        inner_palette = displayio.Palette(1)
        inner_palette[0] = 0

        # Build "sprites"
        for col in range(0, len(self.COLS)):
            for row in range(0, self.ROW_COUNT):
                x = self._get_jack_sprite_x(col)
                title_x = self._get_jack_title_x(col)
                y = self._get_jack_y(row)

                jack_index = row + (col * self.ROW_COUNT)

                outer_circle = vectorio.Circle(pixel_shader=outer_palette, radius=self.RADIUS, x=x, y=y)
                inner_circle = vectorio.Circle(pixel_shader=inner_palette, radius=self.RADIUS-2, x=x, y=y)
                title_label = label.Label(terminalio.FONT, text=GameState.JACK_NAMES[jack_index], x=title_x, y=y)
                title_label.hidden = True

                # Due to the natural order of the for loops, we can just append the sprites.
                self._jack_sprites.append((outer_circle, inner_circle, title_label))

    def add_to_group(self, group):
        for (outer_circle, inner_circle, title_label) in self._jack_sprites:
            group.append(outer_circle)
            group.append(inner_circle)
            group.append(title_label)

    def remove_from_group(self, group):
        for (outer_circle, inner_circle, title_label) in self._jack_sprites:
            group.remove(outer_circle)
            group.remove(inner_circle)
            group.remove(title_label)

    def set_center_x(self, cx):
        self._center_x = cx

        for col in range(0, len(self.COLS)):
            for row in range(0, self.ROW_COUNT):
                x = self._get_jack_sprite_x(col)
                title_x = self._get_jack_title_x(col)

                jack_index = row + (col * self.ROW_COUNT)
                (outer_circle, inner_circle, title_label) = self._jack_sprites[jack_index]
                outer_circle.x = x
                inner_circle.x = x
                title_label.x = title_x

    def set_center_space(self, space):
        self._center_space = space

        for col in range(0, len(self.COLS)):
            for row in range(0, self.ROW_COUNT):
                x = self._get_jack_sprite_x(col)
                title_x = self._get_jack_title_x(col)

                jack_index = row + (col * self.ROW_COUNT)
                (outer_circle, inner_circle, title_label) = self._jack_sprites[jack_index]
                outer_circle.x = x
                inner_circle.x = x
                title_label.x = title_x                

    def blit(self):
        for index in range(0, len(self._jack_sprites)):
            sprite = self._jack_sprites[index]
            sprite[0].hidden = self._hide_jacks
            sprite[1].hidden = self._hide_jacks
            sprite[2].hidden = self._hide_labels

    # Display is not updated after calling/setting these!
    # You will need to call blit() to flush the state to the display.
    def hide(self):
        self.hide_labels = True
        self.hide_jacks = True

    @property
    def hide_labels(self):
        return self._hide_labels

    @hide_labels.setter
    def hide_labels(self, value):
        self._hide_labels = value

    @property
    def hide_jacks(self):
        return self._hide_jacks

    @hide_jacks.setter
    def hide_jacks(self, value):
        self._hide_jacks = value        

    # 
    # Private
    # 
    def _get_jack_sprite_x(self, col):
        return self._center_x + 64 + (self.COLS[col] * (10 + self._center_space))

    def _get_jack_title_x(self, col):
        return (self._center_x - 2) + 64 + (self.COLS[col] * (24 + self._center_space))

    def _get_jack_y(self, row):
        return 5 + row * 13