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
from perlin_noise import PerlinNoise
import datetime

#Constants
WORLD_SIZE = 8              # World size in rooms. This should be an even number, or the player might get stuck in a wall.
ROOM_SIZE = 400             # Room size in pyarcade units
SEED = int(datetime.now())  # Seed for world generation

class World(arcade.Window):

    def __init__(self, color):

        # Variables that will hold sprite lists
        self.player_list = None
        #
        # # Set up the player info
        self.player_sprite = None

        # Set the background color
        arcade.set_background_color(color)

        noise = PerlinNoise(n_dims=2, octaves=1, seed=int(SEED)) #Returns a Perlin Noise object



    def setup(self):
        pass