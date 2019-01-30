"""
Clone of 2048 game
http://2048game.com/

- click Play to Start
- project for PoC course by Rice University
https://www.coursera.org/course/principlescomputing1
- 2048 template
http://www.codeskulptor.org/#poc_2048_template.py

- graphical user interface "GUI class"
- provided by instructors
- and modified by TG (add game instruction)
"""

# set height and width of the grid
HEIGHT = 4
WIDTH = 4

"""
2048 GUI
"""

import simplegui
import codeskulptor
import math

# Tile Images
IMAGENAME = "assets_2048.png"
TILE_SIZE = 100
HALF_TILE_SIZE = TILE_SIZE / 2
BORDER_SIZE = 45

# Directions
UP = 1
DOWN = 2
LEFT = 3
RIGHT = 4

class GUI:
    """
    Class to run game GUI.
    """

    def __init__(self, game):
        self._draw_instruction = False
        self._rows = game.get_grid_height()
        self._cols = game.get_grid_width()
        self._frame = simplegui.create_frame('2048',
                        self._cols * TILE_SIZE + 2 * BORDER_SIZE,
                        self._rows * TILE_SIZE + 2 * BORDER_SIZE)
        self._frame.add_button('New Game', self.start, 100)
        for labels in range(20):
            self._frame.add_label("", 200)
        self._button = self._frame.add_button("How to Play", self.instruction, 100)
        self._frame.set_keydown_handler(self.keydown)
        self._frame.set_draw_handler(self.draw)
        self._frame.set_canvas_background("#BCADA1")
        self._frame.start()
        self._game = game
        url = codeskulptor.file2url(IMAGENAME)
        self._tiles = simplegui.load_image(url)
        self._directions = {"up": UP, "down": DOWN,
                            "left": LEFT, "right": RIGHT}

    def keydown(self, key):
        """
        Keydown handler
        """
        for dirstr, dirval in self._directions.items():
            if key == simplegui.KEY_MAP[dirstr]:
                self._game.move(dirval)
                break

    def instruction(self):
        """
        Show / Hide Game instructon
        """
        if self._draw_instruction == False:
            self._draw_instruction = True
            self._button.set_text("Back to Game")
        else:
            self._draw_instruction = False
            self._button.set_text("How to Play")

    def draw(self, canvas):
        """
        Draw handler
        """
        if self._draw_instruction:
            text_pos = 55
            canvas.draw_text("2048 - HOW TO PLAY?", (20, 25), 23, "White")
            for line in INSTRUCTION_TEXT:
                canvas.draw_text((line), (10, text_pos), 20, "White")
                text_pos += 23
        else:
            for row in range(self._rows):
                for col in range(self._cols):
                    tile = self._game.get_tile(row, col)
                    if tile == 0:
                        val = 0
                    else:
                        val = int(math.log(tile, 2))
                    canvas.draw_image(self._tiles,
                                      [HALF_TILE_SIZE + val * TILE_SIZE, HALF_TILE_SIZE],
                                      [TILE_SIZE, TILE_SIZE],
                                      [col * TILE_SIZE + HALF_TILE_SIZE + BORDER_SIZE,
                                       row * TILE_SIZE + HALF_TILE_SIZE + BORDER_SIZE],
                                      [TILE_SIZE, TILE_SIZE])

    def start(self):
        """
        Start the game.
        """
        self._game.reset()


def run_gui(game):
    """
    Instantiate and run the GUI.
    """
    gui = GUI(game)
    gui.start()


"""
TwentyFortyEight
"""

import random

# Directions, DO NOT MODIFY
UP = 1
DOWN = 2
LEFT = 3
RIGHT = 4

# Offsets for computing tile indices in each direction.
# DO NOT MODIFY this dictionary.
OFFSETS = {UP: (1, 0),
           DOWN: (-1, 0),
           LEFT: (0, 1),
           RIGHT: (0, -1)}


def merge(for_merge_list):
    """
    (list) -> list

    Function that merges a single row or column in 2048.

    >>> merge([2, 4, 4, 2, 2])
    [2, 8, 4, 0, 0]

    >>> merge([0, 4, 16, 16])
    [4, 32, 0, 0]
    """

    merged_list = list(for_merge_list)

    # move all zero's to the end of the list
    for zero_num in for_merge_list:
        if zero_num == 0:
            merged_list.append(0)
            merged_list.remove(0)

    # merge numbers in merged_list
    for number in range(len(merged_list) -1):
        if merged_list[number] != 0:
            if merged_list[number] == merged_list[number +1]:
                merged_list[number] *= 2
                merged_list.pop(number +1)
                merged_list.append(0)

    return merged_list


class TwentyFortyEight:
    """
    Class to run the game logic.
    """

    def __init__(self, grid_height, grid_width):

        self._grid_height = grid_height
        self._grid_width = grid_width
        self.reset()

        # computing a list of the indices for the initial tiles in given direction
        self._directions = {UP:[[0, dummy_i] for dummy_i in range(self._grid_width)], \
                           DOWN:[[(self._grid_height -1), dummy_i] for dummy_i in range(self._grid_width)], \
                           LEFT:[[dummy_i, 0] for dummy_i in range(self._grid_height)], \
                           RIGHT:[[dummy_i, (self._grid_width -1)] for dummy_i in range(self._grid_height)]}

    def reset(self):
        """
        Reset the game so the grid is empty except for two
        initial tiles.
        """
        self._grid = [[0 for dummy_col in range(self._grid_width)]\
                      for dummy_row in range(self._grid_height)]

        for dummy_new_tile in range(2):
            self.new_tile()

    def __str__(self):
        """
        Return a string representation of the grid for debugging.
        """
        game_grid = ""

        for row in list(self._grid):
            game_grid += str(row)
            game_grid += "\n"

        return game_grid

    def get_grid_height(self):
        """
        Get the height of the board.
        """
        return self._grid_height

    def get_grid_width(self):
        """
        Get the width of the board.
        """
        return self._grid_width

    def move(self, direction):
        """
        Move all tiles in the given direction and add
        a new tile if any tiles moved and grid is not full.
        """
        tiles_moved = False

        #set inner loop range so tiles moves correctly on any grid size
        inner_loop_range = self._grid_height
        if direction > 2:
            inner_loop_range = self._grid_width

        """
        create list of coordinates on the grid of first
        tile in row/column for merge in given direction

        direction(UP)
        >>> ([0, 0], [0, 1], [0, 2], [0, 3]) # grid WIDTH == 4
        """
        for indicator in list(self._directions[direction]):
            tile_idx = list(indicator)
            list_for_merge = []
            merged_tiles_idx = []

            # create a list of row/column for merge
            for dummy_j in range(inner_loop_range):
                list_for_merge.append(self._grid[tile_idx[0]][tile_idx[1]])
                merged_tiles_idx.append([tile_idx[0], tile_idx[1]])
                tile_idx[0] += OFFSETS[direction][0]
                tile_idx[1] += OFFSETS[direction][1]

            #  merge row/column using out side class helper function - merge()
            temp_list_for_merge = list(list_for_merge)
            list_for_merge = merge(list_for_merge)

            if temp_list_for_merge != list_for_merge:
                tiles_moved = True

                for tile in range(len(list_for_merge)):
                    self.set_tile(merged_tiles_idx[tile][0], \
                                  merged_tiles_idx[tile][1], list_for_merge[tile])
        if tiles_moved:
            self.new_tile()

    def new_tile(self):
        """
        Create a new tile in a randomly selected empty
        square.  The new tile is "2" 90% of the time and
        "4" 10% of the time.
        """

        # create list of empty squares
        empty_squares = []
        for col in range(self._grid_height):
            for row in range(self._grid_width):
                if self._grid[col][row] == 0:
                    empty_squares.append([col, row])

        # create new tile in one of empty_squares
        if len(empty_squares) > 0:
            tile = random.choice([2] * 9 + [4])
            empty_sq = random.choice(empty_squares)
            self._grid[empty_sq[0]][empty_sq[1]] = tile

    def set_tile(self, row, col, value):
        """
        Set the tile at position row, col to have the given value.
        """
        self._grid[row][col] = value

    def get_tile(self, row, col):
        """
        Return the value of the tile at position row, col.
        """
        return self._grid[row][col]


INSTRUCTION_TEXT = \
["2048 is a simple grid-based numbers game.", \
"The object of the game is to combine tiles with the same",\
"number to make larger numbered tiles. You 'win' when you", \
"create a 2048 tile.", \
"You will have a grid of tiles (size can be modify, ", \
"check code - line 41) and two numbers on start: '2' 90%",\
"of the time and '4' 10% of the time. On each turn, you may",\
"slide all of the tiles on the board in one direction",\
"(left, right, up, or down).When you do so, all of the", \
"tiles on the board slide as far as they can go in the", \
"given direction leaving no empty squares between the tiles.",\
"Further, if two tiles of the same number end up next to", \
"each other, they merge to form a new tile with twice the", \
"value. If any tile slide, new random tile will be given", \
"with the same manner as on start. If no tiles would combine", \
"or slide in a given direction, then that is not a legal", \
"move, and you cannot make that move on the current turn.", \
"If there are no free tiles on the grid, the game ends.", \
"You can hit New Game button to reset Game, any time."]


#run the game
run_gui(TwentyFortyEight(HEIGHT, WIDTH))
