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
import random
from perlin_noise import PerlinNoise
from room import Room

# Constants

# Size of each floor tile in pyarcade units
FLOOR_TILE_SIZE = 80

HORI_WALL_HEIGHT = 2.5*FLOOR_TILE_SIZE
VERTI_WALL_WIDTH = 0.5*FLOOR_TILE_SIZE
WALL_SCALE = 1

# World size in rooms.
# This must be odd, or there are no courtyards. I think this is related to the perlin noise implementation.
WORLD_SIZE = 11

# Room size in pyarcade units
ROOM_SIZE = 9*FLOOR_TILE_SIZE

# Seed for world generation
SEED = int(datetime.datetime.now().timestamp())

# Every room with a noise value greater than INDOOR_CUTOFF will be an indoor room.
# Must be between 0 and 1.
# Recommend between 0.3 and 0.7.
INDOOR_CUTOFF = 0.43

# The probablity that a given wall will have a door.
DOOR_CHANCE = 0.75

def create_y_pos_comparison(sprite):
    return sprite.position[1]

class World(arcade.Window):

    def __init__(self, color):
        random.seed()

        # Variables that will hold sprite lists
        self.player_list = None

        self.wall_list = arcade.SpriteList(use_spatial_hash = True)

        #
        # # Set up the player info
        self.player_sprite = None

        # Set the background color
        arcade.set_background_color(color)

        # Let's make some noise
        world_noise = PerlinNoise(octaves=100, seed=int(SEED))

        # Create 2d array, to hold all the rooms
        rows, cols = (WORLD_SIZE, WORLD_SIZE)
        self.rooms = [[0 for i in range(rows)] for j in range(cols)]
        for i in range(rows):
            for j in range(cols):
                indoor = (( world_noise.noise(coordinates = [i/rows,j/cols]) + 1 ) / 2) >= INDOOR_CUTOFF
                size = ROOM_SIZE
                x = j * ROOM_SIZE
                y = i * ROOM_SIZE

                if i == 0:  # If we are on the south edge, there is no room to the south
                    south = False
                else:       # If the room south of us has a door to the north, we need a door to the south
                    south = self.rooms[i-1][j].north

                if j == 0:
                    east = False
                else:
                    east = self.rooms[i][j-1].west

                north = False
                if i != WORLD_SIZE-1 and random.random() < DOOR_CHANCE:
                    north = True

                west = False
                if j != WORLD_SIZE-1 and random.random() < DOOR_CHANCE:
                    west = True

                if north and south and west and east == False:
                    doorFactor = random.randrange(0, 3)
                    if doorFactor == 0:
                        north = True
                    elif doorFactor == 1:
                        north = True
                    elif doorFactor == 2:
                        north = True
                    elif doorFactor == 3:
                        north = True

                self.rooms[i][j] = Room(x = x, y = y,
                                        size = size, indoor = indoor,
                                        north = north, south = south, west = west, east = east)

                # Create the walls based on where doors are
                if self.rooms[i][j].indoor:
                    # south
                    if self.rooms[i][j].south:
                        curr_width = 3 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("wall_hori_3.png",
                                                         scale=WALL_SCALE,
                                                         image_width=curr_width,
                                                         image_height=HORI_WALL_HEIGHT,
                                                         center_x= int((x + 0.5 * FLOOR_TILE_SIZE) + (1/2)*curr_width),
                                                         center_y= int(y + 0 * FLOOR_TILE_SIZE + (1/2)*HORI_WALL_HEIGHT),
                                                         )
                        self.wall_list.append(self.wall_sprite)
                        self.wall_sprite = arcade.Sprite("wall_hori_3.png",
                                                         scale=WALL_SCALE,
                                                         image_width=3 * FLOOR_TILE_SIZE,
                                                         image_height=HORI_WALL_HEIGHT,
                                                         center_x=int(x + 5.5 * FLOOR_TILE_SIZE + (1/2)*curr_width),
                                                         center_y=int(y + 0 * FLOOR_TILE_SIZE + (1/2)*HORI_WALL_HEIGHT)),
                        self.wall_list.append(self.wall_sprite[0])
                    else:
                        curr_width = 8 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("wall_hori_8.png",
                                                         scale=WALL_SCALE,
                                                         image_width=8 * FLOOR_TILE_SIZE,
                                                         image_height=HORI_WALL_HEIGHT,
                                                         center_x=int(x + 0.5 * FLOOR_TILE_SIZE + 0.5 * curr_width),
                                                         center_y=int(y + 0 * FLOOR_TILE_SIZE + 0.5*HORI_WALL_HEIGHT)),
                        self.wall_list.append(self.wall_sprite[0])
                    # north
                    if self.rooms[i][j].north:
                        curr_width = 3 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("wall_hori_3.png",
                                                         scale = WALL_SCALE,
                                                         image_width = 3*FLOOR_TILE_SIZE,
                                                         image_height = HORI_WALL_HEIGHT,
                                                         center_x = int(x+0.5*FLOOR_TILE_SIZE + 0.5*curr_width),
                                                         center_y = int(y+8.5*FLOOR_TILE_SIZE + 0.5*HORI_WALL_HEIGHT),
                                                         )
                        self.wall_list.append(self.wall_sprite)
                        self.wall_sprite = arcade.Sprite("wall_hori_3.png",
                                                         scale = WALL_SCALE,
                                                         image_width = 3 * FLOOR_TILE_SIZE,
                                                         image_height = HORI_WALL_HEIGHT,
                                                         center_x = int(x + 5.5 * FLOOR_TILE_SIZE + 0.5*curr_width),
                                                         center_y = int(y + 8.5 * FLOOR_TILE_SIZE + 0.5*HORI_WALL_HEIGHT), )
                        self.wall_list.append(self.wall_sprite)
                    else:
                        curr_width = 8 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("wall_hori_8.png",
                                                         scale = WALL_SCALE,
                                                         image_width = 8 * FLOOR_TILE_SIZE,
                                                         image_height = HORI_WALL_HEIGHT,
                                                         center_x = int(x + 0.5 * FLOOR_TILE_SIZE + 0.5*curr_width),
                                                         center_y = int(y + 8.5 * FLOOR_TILE_SIZE + 0.5*HORI_WALL_HEIGHT), )
                        self.wall_list.append(self.wall_sprite)

                    # west
                    if self.rooms[i][j].west:
                        curr_height = 5.5 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("wall_verti_3.5.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTI_WALL_WIDTH,
                                                         image_height=5.5 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5*VERTI_WALL_WIDTH),
                                                         center_y=int(y + 0.5*curr_height))
                        self.wall_list.append(self.wall_sprite)
                        self.wall_sprite = arcade.Sprite("wall_verti_3.5.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTI_WALL_WIDTH,
                                                         image_height=5.5 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5 * VERTI_WALL_WIDTH),
                                                         center_y=int(y + 0.5 * curr_height + 5.5 * FLOOR_TILE_SIZE))
                        self.wall_list.append(self.wall_sprite)
                    else:
                        curr_height = 11 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("wall_verti_9.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTI_WALL_WIDTH,
                                                         image_height=11 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5 * VERTI_WALL_WIDTH),
                                                         center_y=int(y + 0.5 * curr_height))
                        self.wall_list.append(self.wall_sprite)

                    # east
                    if self.rooms[i][j].east:
                        curr_height = 5.5 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("wall_verti_3.5.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTI_WALL_WIDTH,
                                                         image_height=5.5 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5*VERTI_WALL_WIDTH + 8.5 * FLOOR_TILE_SIZE),
                                                         center_y=int(y + 0.5*curr_height))
                        self.wall_list.append(self.wall_sprite)
                        self.wall_sprite = arcade.Sprite("wall_verti_3.5.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTI_WALL_WIDTH,
                                                         image_height=5.5 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5*VERTI_WALL_WIDTH + 8.5 * FLOOR_TILE_SIZE),
                                                         center_y=int(y + 0.5*curr_height + 5.5 * FLOOR_TILE_SIZE))
                        self.wall_list.append(self.wall_sprite)
                    else:
                        curr_height = 11 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("wall_verti_9.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTI_WALL_WIDTH,
                                                         image_height=11 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5 * VERTI_WALL_WIDTH + 8.5 * FLOOR_TILE_SIZE),
                                                         center_y=int(y + 0.5 * curr_height))
                        self.wall_list.append(self.wall_sprite)

                    # sort sprite list by y coordinate, so they will be drawn in the correct order
                    self.wall_list.sort(key = create_y_pos_comparison, reverse=True)



    def setup(self):
        pass