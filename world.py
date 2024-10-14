"""
Move Sprite With Keyboard

Simple program to show moving a sprite with the keyboard.
The sprite_move_keyboard_better.py example is slightly better
in how it works, but also slightly more complex.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_move_keyboard
"""

import arcade
import datetime
from perlin_noise import PerlinNoise
from room import Room


#Constants

WORLD_SIZE = 9      # World size in rooms.
ROOM_SIZE = 400     # Room size in pyarcade units
SEED = int(datetime.datetime.now().timestamp())  # Seed for world generation
# Every room with a noise value greater than INDOOR_CUTOFF will be an indoor room.
# Should be between 0 and 1.
INDOOR_CUTOFF = 0.4

class World(arcade.Window):

    def __init__(self, color):

        # Variables that will hold sprite lists
        self.player_list = None
        #
        # # Set up the player info
        self.player_sprite = None

        # Set the background color
        arcade.set_background_color(color)

        # Let's make some noise
        world_noise = PerlinNoise(octaves=100, seed=int(SEED))

        # Create 2d array, to hold all the noise rooms
        rows, cols = (WORLD_SIZE, WORLD_SIZE)
        rooms = [[0 for i in range(cols)] for j in range(rows)]
        for i in range(cols):
            for j in range(rows):
                indoor = (( world_noise.noise(coordinates = [i/rows,j/cols]) + 1 ) / 2) >= INDOOR_CUTOFF
                size = ROOM_SIZE
                x = j * ROOM_SIZE
                y = i * ROOM_SIZE
                rooms[i][j] = Room(x = x, y = y, size = size, indoor = indoor)
        #print(rooms)

        # Create 2d array, to hold all the rooms



    def setup(self):
        pass