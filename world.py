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

import pyglet.math
from arcade.examples.array_backed_grid import SCREEN_WIDTH
from perlin_noise import PerlinNoise
from room import Room

# Constants

# screen width and height
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 1000

# Size of each floor tile in pyarcade units
FLOOR_TILE_SIZE = 80

HORI_WALL_HEIGHT = 2.5*FLOOR_TILE_SIZE
VERTI_WALL_WIDTH = 0.5*FLOOR_TILE_SIZE
WALL_SCALE = 1

# World size in rooms.
# This must be odd, or there are no courtyards. I think this is related to the perlin noise implementation.
WORLD_SIZE = 5

# Room size in pyarcade units
ROOM_SIZE = 9*FLOOR_TILE_SIZE

# Seed for world generation
SEED = int(datetime.datetime.now().timestamp())

# Every room with a noise value greater than INDOOR_CUTOFF will be an indoor room.
# Must be between 0 and 1.
# Recommend between 0.3 and 0.7.
INDOOR_CUTOFF = 0.44

# The probablity that a given wall will have a door.
DOOR_CHANCE = 0.75

def create_y_pos_comparison(sprite):
    return sprite.position[1]

def create_hori_hitbox(width,height):
    return [[-width/2, -height/2], [width/2, -height/2], [width/2, 0], [-width/2, 0]]
def create_verti_hitbox(width,height):
    return [[-width/2, -height/2], [width/2, -height/2], [width/2, 0], [-width/2, 0]]
def create_verti_fullh_hitbox(width,height):
    return [[-width / 2, -height / 2], [width / 2, -height / 2], [width / 2, height / 2], [-width / 2, height/2]]



class World(arcade.Window):
    
    
    def __init__(self, color):
        random.seed()

        # Variables that will hold sprite lists
        self.player_list = None

        self.wall_list = arcade.SpriteList(use_spatial_hash = True)
        self.wall_front_list = arcade.SpriteList(use_spatial_hash = True)
        self.wall_back_list = arcade.SpriteList(use_spatial_hash = True)
        self.floor_list = arcade.SpriteList(use_spatial_hash = True)

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
                x = j * ROOM_SIZE - 0.5*ROOM_SIZE*WORLD_SIZE + 0.5*SCREEN_WIDTH
                y = i * ROOM_SIZE - 0.5*ROOM_SIZE*WORLD_SIZE + 0.5*SCREEN_HEIGHT

                if i == 0:  # If we are on the south edge, there is no door to the south
                    south = False
                else:
                    south = self.rooms[i-1][j].north

                if j == 0: # If we are on the west edge, there is no door to the west
                    west = False
                else:
                    west = self.rooms[i][j-1].east

                north = False
                if i != WORLD_SIZE-1 and random.random() < DOOR_CHANCE:
                    north = True

                east = False
                if j != WORLD_SIZE-1 and random.random() < DOOR_CHANCE:
                    east = True

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

                # For outdoor rooms, only generate walls if at the edge of the map
                if self.rooms[i][j].indoor == False:
                    # south
                    if i == 0:
                        curr_width = 8 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("wall_hori_8.png",
                                                         scale=WALL_SCALE,
                                                         image_width=curr_width,
                                                         image_height=HORI_WALL_HEIGHT,
                                                         center_x=int(x + 0 * FLOOR_TILE_SIZE + 0.5 * curr_width),
                                                         center_y=int(y + 0 * FLOOR_TILE_SIZE + 0.5 * HORI_WALL_HEIGHT), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_hori_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_list.append(self.wall_sprite)
                        curr_width = 1 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("wall_hori.png",
                                                         scale=WALL_SCALE,
                                                         image_width=curr_width,
                                                         image_height=HORI_WALL_HEIGHT,
                                                         center_x=int(x + 8 * FLOOR_TILE_SIZE + 0.5 * curr_width),
                                                         center_y=int(y + 0 * FLOOR_TILE_SIZE + 0.5 * HORI_WALL_HEIGHT), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_hori_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_list.append(self.wall_sprite)
                    # north
                    if i == WORLD_SIZE-1:
                        curr_width = 8 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("wall_hori_8.png",
                                                         scale=WALL_SCALE,
                                                         image_width=curr_width,
                                                         image_height=HORI_WALL_HEIGHT,
                                                         center_x=int(x + 0 * FLOOR_TILE_SIZE + 0.5 * curr_width),
                                                         center_y=int(y + 8.5 * FLOOR_TILE_SIZE + 0.5 * HORI_WALL_HEIGHT), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = [[0,-self.wall_sprite.height/2],[0,-self.wall_sprite.height/2],[0,-self.wall_sprite.height/2],[0,-self.wall_sprite.height/2]]
                        self.wall_list.append(self.wall_sprite)
                        curr_width = 1 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("wall_hori.png",
                                                         scale=WALL_SCALE,
                                                         image_width=curr_width,
                                                         image_height=HORI_WALL_HEIGHT,
                                                         center_x=int(x + 8 * FLOOR_TILE_SIZE + 0.5 * curr_width),
                                                         center_y=int(
                                                             y + 8.5 * FLOOR_TILE_SIZE + 0.5 * HORI_WALL_HEIGHT), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_hori_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_list.append(self.wall_sprite)
                    # west
                    if j == 0:
                        curr_height = 11 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("wall_verti_9.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTI_WALL_WIDTH,
                                                         image_height=curr_height,
                                                         center_x=int(x + 0.5 * VERTI_WALL_WIDTH),
                                                         center_y=int(y + 0.5 * curr_height),hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_verti_fullh_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_front_list.append(self.wall_sprite)
                    # east
                    if j == WORLD_SIZE-1:
                        curr_height = 11 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("wall_verti_9.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTI_WALL_WIDTH,
                                                         image_height=curr_height,
                                                         center_x=int(x + 17.5 * VERTI_WALL_WIDTH),
                                                         center_y=int(y + 0.5 * curr_height),hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_verti_fullh_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_front_list.append(self.wall_sprite)

                # For indoor rooms, create the walls based on where doors are
                elif self.rooms[i][j].indoor:
                    # south
                    if self.rooms[i][j].south:
                        curr_width = 3 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("wall_hori_3.png",
                                                         scale=WALL_SCALE,
                                                         image_width=curr_width,
                                                         image_height=HORI_WALL_HEIGHT,
                                                         center_x= int((x + 0.5 * FLOOR_TILE_SIZE) + (1/2)*curr_width),
                                                         center_y= int(y + 0 * FLOOR_TILE_SIZE + (1/2)*HORI_WALL_HEIGHT), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = [[0,-self.wall_sprite.height/2],[0,-self.wall_sprite.height/2],[0,-self.wall_sprite.height/2],[0,-self.wall_sprite.height/2]]
                        self.wall_list.append(self.wall_sprite)
                        self.wall_sprite = arcade.Sprite("wall_hori_3.png",
                                                         scale=WALL_SCALE,
                                                         image_width=3 * FLOOR_TILE_SIZE,
                                                         image_height=HORI_WALL_HEIGHT,
                                                         center_x=int(x + 5.5 * FLOOR_TILE_SIZE + (1/2)*curr_width),
                                                         center_y=int(y + 0 * FLOOR_TILE_SIZE + (1/2)*HORI_WALL_HEIGHT),hit_box_algorithm=None)
                        self.wall_sprite.hit_box = [[0,-self.wall_sprite.height/2],[0,-self.wall_sprite.height/2],[0,-self.wall_sprite.height/2],[0,-self.wall_sprite.height/2]]
                        self.wall_list.append(self.wall_sprite)
                    else:
                        curr_width = 8 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("wall_hori_8.png",
                                                         scale=WALL_SCALE,
                                                         image_width=8 * FLOOR_TILE_SIZE,
                                                         image_height=HORI_WALL_HEIGHT,
                                                         center_x=int(x + 0.5 * FLOOR_TILE_SIZE + 0.5 * curr_width),
                                                         center_y=int(y + 0 * FLOOR_TILE_SIZE + 0.5*HORI_WALL_HEIGHT), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_hori_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_list.append(self.wall_sprite)
                    # north
                    if self.rooms[i][j].north:
                        curr_width = 3 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("wall_hori_3.png",
                                                         scale = WALL_SCALE,
                                                         image_width = 3*FLOOR_TILE_SIZE,
                                                         image_height = HORI_WALL_HEIGHT,
                                                         center_x = int(x+0.5*FLOOR_TILE_SIZE + 0.5*curr_width),
                                                         center_y = int(y+8.5*FLOOR_TILE_SIZE + 0.5*HORI_WALL_HEIGHT),hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_hori_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_list.append(self.wall_sprite)
                        self.wall_sprite = arcade.Sprite("wall_hori_3.png",
                                                         scale = WALL_SCALE,
                                                         image_width = 3 * FLOOR_TILE_SIZE,
                                                         image_height = HORI_WALL_HEIGHT,
                                                         center_x = int(x + 5.5 * FLOOR_TILE_SIZE + 0.5*curr_width),
                                                         center_y = int(y + 8.5 * FLOOR_TILE_SIZE + 0.5*HORI_WALL_HEIGHT), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_hori_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_list.append(self.wall_sprite)
                    else:
                        curr_width = 8 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("wall_hori_8.png",
                                                         scale = WALL_SCALE,
                                                         image_width = 8 * FLOOR_TILE_SIZE,
                                                         image_height = HORI_WALL_HEIGHT,
                                                         center_x = int(x + 0.5 * FLOOR_TILE_SIZE + 0.5*curr_width),
                                                         center_y = int(y + 8.5 * FLOOR_TILE_SIZE + 0.5*HORI_WALL_HEIGHT), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_hori_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_list.append(self.wall_sprite)

                    # west
                    if self.rooms[i][j].west:
                        curr_height = 5.5 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("wall_verti_3.5_lower.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTI_WALL_WIDTH,
                                                         image_height=5.5 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5*VERTI_WALL_WIDTH),
                                                         center_y=int(y + 0.5*curr_height), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_verti_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_front_list.append(self.wall_sprite)

                        #TODO Add to seperate sprite list for drawing z-index - always be behind player:
                        self.wall_sprite = arcade.Sprite("wall_verti_3.5.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTI_WALL_WIDTH,
                                                         image_height=5.5 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5 * VERTI_WALL_WIDTH),
                                                         center_y=int(y + 0.5 * curr_height + 5.5 * FLOOR_TILE_SIZE), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_verti_fullh_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_back_list.append(self.wall_sprite)
                    else:
                        curr_height = 11 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("wall_verti_9.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTI_WALL_WIDTH,
                                                         image_height=11 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5 * VERTI_WALL_WIDTH),
                                                         center_y=int(y + 0.5 * curr_height), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_verti_fullh_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_front_list.append(self.wall_sprite)

                    # east
                    if self.rooms[i][j].east:
                        curr_height = 5.5 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("wall_verti_3.5_lower.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTI_WALL_WIDTH,
                                                         image_height=5.5 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5*VERTI_WALL_WIDTH + 8.5 * FLOOR_TILE_SIZE),
                                                         center_y=int(y + 0.5*curr_height), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_verti_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_front_list.append(self.wall_sprite)
                        self.wall_sprite = arcade.Sprite("wall_verti_3.5.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTI_WALL_WIDTH,
                                                         image_height=5.5 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5*VERTI_WALL_WIDTH + 8.5 * FLOOR_TILE_SIZE),
                                                         center_y=int(y + 0.5*curr_height + 5.5 * FLOOR_TILE_SIZE), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_verti_fullh_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_back_list.append(self.wall_sprite)
                    else:
                        curr_height = 11 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("wall_verti_9.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTI_WALL_WIDTH,
                                                         image_height=11 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5 * VERTI_WALL_WIDTH + 8.5 * FLOOR_TILE_SIZE),
                                                         center_y=int(y + 0.5 * curr_height), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_verti_fullh_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_front_list.append(self.wall_sprite)

                    # Make the floors
                    for k in range(9):
                        for l in range(9):
                            self.floor_sprite = arcade.Sprite("floor.png",
                                                         scale=WALL_SCALE,
                                                         image_width=FLOOR_TILE_SIZE,
                                                         image_height=FLOOR_TILE_SIZE,
                                                         center_x=int(x + k * FLOOR_TILE_SIZE),
                                                         center_y=int(y + l * FLOOR_TILE_SIZE),
                                                              )
                            self.floor_list.append(self.floor_sprite)


        # sort sprite list by y coordinate, so they will be drawn in the correct order
        self.wall_list.sort(key = create_y_pos_comparison, reverse=True)

    def find_room(self, vec2_pos: pyglet.math.Vec2):
        room: Room
        curr_room = None
        for room_r in self.rooms:
            for room in room_r:
                right = room.x + ROOM_SIZE
                top = room.y + ROOM_SIZE
                if room.x < vec2_pos.x < right and room.y < vec2_pos.y < top:
                    return room

        return None


    def setup(self):
        pass