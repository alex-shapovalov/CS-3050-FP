import arcade
import datetime
import random
import pyglet.math
from arcade.examples.array_backed_grid import SCREEN_WIDTH
from perlin_noise import PerlinNoise
from room import Room

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 1000
FLOOR_TILE_SIZE = 80
HORIZONTAL_WALL_HEIGHT = 2.5 * FLOOR_TILE_SIZE
VERTICAL_WALL_WIDTH = 0.5 * FLOOR_TILE_SIZE
WALL_SCALE = 1
WORLD_SIZE = 5
ROOM_SIZE = 9 * FLOOR_TILE_SIZE # Room size in pyarcade units
SEED = int(datetime.datetime.now().timestamp()) # Seed for world generation
INDOOR_CUTOFF = 0.51 # Every room with a noise value greater than INDOOR_CUTOFF will be an indoor room. Must be between 0 and 1.
DOOR_CHANCE = 0.75 # The probability that a given wall will have a door.

def create_y_pos_comparison(sprite):
    return sprite.position[1]

def create_horizontal_hitbox(width, height):
    return [[-width/2, -height/2], [width/2, -height/2], [width/2, 0], [-width/2, 0]]
def create_vertical_hitbox(width, height):
    return [[-width/2, -height/2], [width/2, -height/2], [width/2, 0], [-width/2, 0]]
def create_vertical_fullh_hitbox(width, height):
    return [[-width / 2, -height / 2], [width / 2, -height / 2], [width / 2, height / 2], [-width / 2, height/2]]


class World(arcade.Window):
    """ Class for procedural room and world generation """
    def __init__(self, color):
        random.seed()

        # Variables that will hold sprite lists
        self.player_list = None

        self.wall_list = arcade.SpriteList(use_spatial_hash = True)
        self.wall_front_list = arcade.SpriteList(use_spatial_hash = True)
        self.wall_back_list = arcade.SpriteList(use_spatial_hash = True)
        self.wall_cover_list = arcade.SpriteList(use_spatial_hash=True)
        self.floor_list_outdoor = arcade.SpriteList(use_spatial_hash = True)
        self.floor_list_indoor = arcade.SpriteList(use_spatial_hash = True)

        # Set up the player info
        self.player_sprite = None

        # Set the background color
        arcade.set_background_color(color)

        # Create 2d array, to hold all the rooms
        rows, cols = (WORLD_SIZE, WORLD_SIZE)
        self.rooms = []

        # Let's make some noise
        world_noise = PerlinNoise(octaves=WORLD_SIZE, seed=int(SEED))
        noise_vals = [[((world_noise([i/2, j/2]) + 1 )/ 2) for j in range(cols)] for i in range(rows)]

        for i in range(rows):
            self.rooms.append([])
            for j in range(cols):
                indoor = noise_vals[i][j] <= INDOOR_CUTOFF
                size = ROOM_SIZE
                x = j * ROOM_SIZE - 0.5 * ROOM_SIZE*WORLD_SIZE + 0.5 * SCREEN_WIDTH
                y = i * ROOM_SIZE - 0.5 * ROOM_SIZE*WORLD_SIZE + 0.5 * SCREEN_HEIGHT

                # If we are on the south edge, there is no door to the south
                if i == 0:
                    south = False
                else:
                    south = self.rooms[i-1][j].north

                # If we are on the west edge, there is no door to the west
                if j == 0:
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

                self.rooms[i].append(Room(x = x, y = y, size = size, indoor = indoor, north = north, south = south, west = west, east = east))

                # For outdoor rooms, only generate walls if at the edge of the map or if wall is bordering an indoor room
                if self.rooms[i][j].indoor == False:
                    # South
                    if i == 0:
                        curr_width = 8 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_horizontal_8.png",
                                                         scale=WALL_SCALE,
                                                         image_width=curr_width,
                                                         image_height=HORIZONTAL_WALL_HEIGHT,
                                                         center_x=int(x + 0 * FLOOR_TILE_SIZE + 0.5 * curr_width),
                                                         center_y=int(y + 0 * FLOOR_TILE_SIZE + 0.5 * HORIZONTAL_WALL_HEIGHT), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_horizontal_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_list.append(self.wall_sprite)
                        curr_width = 1 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_horizontal.png",
                                                         scale=WALL_SCALE,
                                                         image_width=curr_width,
                                                         image_height=HORIZONTAL_WALL_HEIGHT,
                                                         center_x=int(x + 8 * FLOOR_TILE_SIZE + 0.5 * curr_width),
                                                         center_y=int(y + 0 * FLOOR_TILE_SIZE + 0.5 * HORIZONTAL_WALL_HEIGHT), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_horizontal_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_list.append(self.wall_sprite)

                    # Add bottom walls to room if bordering indoor room
                    if self.rooms[i][j].south and self.rooms[i-1][j].indoor:
                        curr_width = 3 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_horizontal_3.png",
                                                         scale=WALL_SCALE,
                                                         image_width=curr_width,
                                                         image_height=HORIZONTAL_WALL_HEIGHT,
                                                         center_x=int(
                                                             (x + 0.5 * FLOOR_TILE_SIZE) + (1 / 2) * curr_width),
                                                         center_y=int(y + 0 * FLOOR_TILE_SIZE + (1/2)*HORIZONTAL_WALL_HEIGHT),
                                                         hit_box_algorithm=None)
                        self.wall_sprite.hit_box = [[0,-self.wall_sprite.height/2],[0,-self.wall_sprite.height/2],[0,-self.wall_sprite.height/2],[0,-self.wall_sprite.height/2]]
                        self.wall_list.append(self.wall_sprite)
                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_horizontal_3.png",
                                                         scale=WALL_SCALE,
                                                         image_width=curr_width,
                                                         image_height=HORIZONTAL_WALL_HEIGHT,
                                                         center_x=int(
                                                             x + 5.5 * FLOOR_TILE_SIZE + (1 / 2) * curr_width),
                                                         center_y=int(
                                                             y + 0 * FLOOR_TILE_SIZE + (1/2)*HORIZONTAL_WALL_HEIGHT),
                                                         hit_box_algorithm=None)
                        self.wall_sprite.hit_box = [[0,-self.wall_sprite.height/2],[0,-self.wall_sprite.height/2],[0,-self.wall_sprite.height/2],[0,-self.wall_sprite.height/2]]
                        self.wall_list.append(self.wall_sprite)

                    if not self.rooms[i][j].south and self.rooms[i-1][j].indoor:
                        curr_width = 8 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_horizontal_8.png",
                                                         scale=WALL_SCALE,
                                                         image_width=8 * FLOOR_TILE_SIZE,
                                                         image_height=HORIZONTAL_WALL_HEIGHT,
                                                         center_x=int(x + 0.5 * FLOOR_TILE_SIZE + 0.5 * curr_width),
                                                         center_y=int(
                                                             y + 0 * FLOOR_TILE_SIZE + 0.5 * HORIZONTAL_WALL_HEIGHT),
                                                         hit_box_algorithm=None)
                        self.wall_sprite.hit_box = [[0, -self.wall_sprite.height / 2],
                                                    [0, -self.wall_sprite.height / 2],
                                                    [0, -self.wall_sprite.height / 2],
                                                    [0, -self.wall_sprite.height / 2]]
                        self.wall_list.append(self.wall_sprite)

                    # North
                    if i == WORLD_SIZE-1:
                        curr_width = 8 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_horizontal_8.png",
                                                         scale=WALL_SCALE,
                                                         image_width=curr_width,
                                                         image_height=HORIZONTAL_WALL_HEIGHT,
                                                         center_x=int(x + 0 * FLOOR_TILE_SIZE + 0.5 * curr_width),
                                                         center_y=int(y + 8.5 * FLOOR_TILE_SIZE + 0.5 * HORIZONTAL_WALL_HEIGHT), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_horizontal_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_list.append(self.wall_sprite)
                        curr_width = 1 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_horizontal.png",
                                                         scale=WALL_SCALE,
                                                         image_width=curr_width,
                                                         image_height=HORIZONTAL_WALL_HEIGHT,
                                                         center_x=int(x + 8 * FLOOR_TILE_SIZE + 0.5 * curr_width),
                                                         center_y=int(
                                                             y + 8.5 * FLOOR_TILE_SIZE + 0.5 * HORIZONTAL_WALL_HEIGHT), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_horizontal_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_list.append(self.wall_sprite)

                    # West
                    if j == 0:
                        curr_height = 11 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_vertical_9.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTICAL_WALL_WIDTH,
                                                         image_height=curr_height,
                                                         center_x=int(x + 0.5 * VERTICAL_WALL_WIDTH),
                                                         center_y=int(y + 0.5 * curr_height),hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_vertical_fullh_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_front_list.append(self.wall_sprite)
                    self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_cover.png",
                                                     scale=WALL_SCALE,
                                                     image_width=VERTICAL_WALL_WIDTH,
                                                     image_height=2 * FLOOR_TILE_SIZE,
                                                     center_x=int(x + 0.5 * VERTICAL_WALL_WIDTH),
                                                     center_y=int(y + 10 * FLOOR_TILE_SIZE),
                                                     hit_box_algorithm=None)
                    self.wall_cover_list.append(self.wall_sprite)

                    if self.rooms[i][j].west and self.rooms[i][j-1].indoor:
                        curr_height = 5.5 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_vertical_3.5_lower.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTICAL_WALL_WIDTH,
                                                         image_height=5.5 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5 * VERTICAL_WALL_WIDTH),
                                                         center_y=int(y + 0.5 * curr_height), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_vertical_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_front_list.append(self.wall_sprite)

                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_vertical_3.5.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTICAL_WALL_WIDTH,
                                                         image_height=5.5 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5 * VERTICAL_WALL_WIDTH),
                                                         center_y=int(y + 0.5 * curr_height + 5.5 * FLOOR_TILE_SIZE),
                                                         hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_vertical_fullh_hitbox(self.wall_sprite.width,
                                                                             self.wall_sprite.height)
                        self.wall_back_list.append(self.wall_sprite)
                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_cover.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTICAL_WALL_WIDTH,
                                                         image_height=2 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5 * VERTICAL_WALL_WIDTH),
                                                         center_y=int(y + 10 * FLOOR_TILE_SIZE), hit_box_algorithm=None)
                        self.wall_cover_list.append(self.wall_sprite)
                    elif not self.rooms[i][j].west and self.rooms[i][j-1].indoor:
                        curr_height = 11 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_vertical_9.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTICAL_WALL_WIDTH,
                                                         image_height=11 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5 * VERTICAL_WALL_WIDTH),
                                                         center_y=int(y + 0.5 * curr_height), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_vertical_fullh_hitbox(self.wall_sprite.width,
                                                                             self.wall_sprite.height)
                        self.wall_front_list.append(self.wall_sprite)

                    # East
                    if j == WORLD_SIZE-1:
                        curr_height = 11 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_vertical_9.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTICAL_WALL_WIDTH,
                                                         image_height=curr_height,
                                                         center_x=int(x + 17.5 * VERTICAL_WALL_WIDTH),
                                                         center_y=int(y + 0.5 * curr_height),hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_vertical_fullh_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_front_list.append(self.wall_sprite)
                    self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_cover.png",
                                                     scale=WALL_SCALE,
                                                     image_width=VERTICAL_WALL_WIDTH,
                                                     image_height=2 * FLOOR_TILE_SIZE,
                                                     center_x=int(x + 0.5 * VERTICAL_WALL_WIDTH + 8.5 * FLOOR_TILE_SIZE),
                                                     center_y=int(y + 10 * FLOOR_TILE_SIZE),
                                                     hit_box_algorithm=None)
                    self.wall_cover_list.append(self.wall_sprite)

                    # Make the floors
                    vertical_offset = 0
                    horizontal_offset = 0
                    horizontal_range_reduction = 0
                    vertical_range_reduction = 0
                    # If we are on the south edge
                    if i == 0:
                        vertical_offset = FLOOR_TILE_SIZE
                        vertical_range_reduction = 1
                    # If we are on the west edge
                    if j == 0:
                        horizontal_offset = FLOOR_TILE_SIZE
                        horizontal_range_reduction = 1

                    for k in range(10 - horizontal_range_reduction):
                        for l in range(10 - vertical_range_reduction):
                            self.floor_sprite = arcade.Sprite("sprites/world/misc/grass.png",
                                                              scale=WALL_SCALE,
                                                              image_width=FLOOR_TILE_SIZE,
                                                              image_height=FLOOR_TILE_SIZE,
                                                              center_x=int(x + k * FLOOR_TILE_SIZE + horizontal_offset),
                                                              center_y=int(y + l * FLOOR_TILE_SIZE + vertical_offset))
                            self.floor_list_outdoor.append(self.floor_sprite)

                # For indoor rooms, create the walls based on where doors are
                elif self.rooms[i][j].indoor:
                    # South
                    if self.rooms[i][j].south:
                        curr_width = 3 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_horizontal_3.png",
                                                         scale=WALL_SCALE,
                                                         image_width=curr_width,
                                                         image_height=HORIZONTAL_WALL_HEIGHT,
                                                         center_x= int((x + 0.5 * FLOOR_TILE_SIZE) + (1/2)*curr_width),
                                                         center_y= int(y + 0 * FLOOR_TILE_SIZE + (1/2)*HORIZONTAL_WALL_HEIGHT), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = [[0,-self.wall_sprite.height/2],[0,-self.wall_sprite.height/2],[0,-self.wall_sprite.height/2],[0,-self.wall_sprite.height/2]]
                        self.wall_list.append(self.wall_sprite)
                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_horizontal_3.png",
                                                         scale=WALL_SCALE,
                                                         image_width=3 * FLOOR_TILE_SIZE,
                                                         image_height=HORIZONTAL_WALL_HEIGHT,
                                                         center_x=int(x + 5.5 * FLOOR_TILE_SIZE + (1/2)*curr_width),
                                                         center_y=int(y + 0 * FLOOR_TILE_SIZE + (1/2)*HORIZONTAL_WALL_HEIGHT),hit_box_algorithm=None)
                        self.wall_sprite.hit_box = [[0,-self.wall_sprite.height/2],[0,-self.wall_sprite.height/2],[0,-self.wall_sprite.height/2],[0,-self.wall_sprite.height/2]]
                        self.wall_list.append(self.wall_sprite)
                        if i != 0 and not self.rooms[i-1][j].indoor:
                            self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_horizontal_3.png",
                                                             scale=WALL_SCALE,
                                                             image_width=curr_width,
                                                             image_height=HORIZONTAL_WALL_HEIGHT,
                                                             center_x=int(
                                                                 (x + 0.5 * FLOOR_TILE_SIZE) + (1 / 2) * curr_width),
                                                             center_y=int(y + 0 * FLOOR_TILE_SIZE + (1/2)*HORIZONTAL_WALL_HEIGHT-VERTICAL_WALL_WIDTH),
                                                             hit_box_algorithm=None)
                            self.wall_sprite.hit_box = create_horizontal_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                            self.wall_list.append(self.wall_sprite)
                            self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_horizontal_3.png",
                                                             scale=WALL_SCALE,
                                                             image_width=3 * FLOOR_TILE_SIZE,
                                                             image_height=HORIZONTAL_WALL_HEIGHT,
                                                             center_x=int(
                                                                 x + 5.5 * FLOOR_TILE_SIZE + (1 / 2) * curr_width),
                                                             center_y=int(
                                                                 y + 0 * FLOOR_TILE_SIZE + (1/2)*HORIZONTAL_WALL_HEIGHT-VERTICAL_WALL_WIDTH),
                                                             hit_box_algorithm=None)
                            self.wall_sprite.hit_box = create_horizontal_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                            self.wall_list.append(self.wall_sprite)

                    else:
                        curr_width = 8 * FLOOR_TILE_SIZE
                        if i == 0:
                            self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_horizontal_8.png",
                                                             scale=WALL_SCALE,
                                                             image_width=8 * FLOOR_TILE_SIZE,
                                                             image_height=HORIZONTAL_WALL_HEIGHT,
                                                             center_x=int(x + 0.5 * FLOOR_TILE_SIZE + 0.5 * curr_width),
                                                             center_y=int(y + 0 * FLOOR_TILE_SIZE + 0.5*HORIZONTAL_WALL_HEIGHT), hit_box_algorithm=None)
                            self.wall_sprite.hit_box = create_horizontal_hitbox(self.wall_sprite.width,
                                                                          self.wall_sprite.height)
                            self.wall_list.append(self.wall_sprite)
                        else:
                            self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_horizontal_8.png",
                                                             scale=WALL_SCALE,
                                                             image_width=8 * FLOOR_TILE_SIZE,
                                                             image_height=HORIZONTAL_WALL_HEIGHT,
                                                             center_x=int(x + 0.5 * FLOOR_TILE_SIZE + 0.5 * curr_width),
                                                             center_y=int(
                                                                 y + 0 * FLOOR_TILE_SIZE + 0.5 * HORIZONTAL_WALL_HEIGHT),
                                                             hit_box_algorithm=None)
                            self.wall_sprite.hit_box = [[0, -self.wall_sprite.height / 2],
                                                        [0, -self.wall_sprite.height / 2],
                                                        [0, -self.wall_sprite.height / 2],
                                                        [0, -self.wall_sprite.height / 2]]
                            self.wall_list.append(self.wall_sprite)
                            if not self.rooms[i - 1][j].indoor:
                                curr_width = 8 * FLOOR_TILE_SIZE
                                self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_horizontal_8.png",
                                                                 scale=WALL_SCALE,
                                                                 image_width=8 * FLOOR_TILE_SIZE,
                                                                 image_height=HORIZONTAL_WALL_HEIGHT,
                                                                 center_x=int(
                                                                     x + 0.5 * FLOOR_TILE_SIZE + 0.5 * curr_width),
                                                                 center_y=int(
                                                                     y + 0 * FLOOR_TILE_SIZE + 0.5 * HORIZONTAL_WALL_HEIGHT - VERTICAL_WALL_WIDTH),
                                                                 hit_box_algorithm=None)
                                self.wall_sprite.hit_box = create_horizontal_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                                self.wall_list.append(self.wall_sprite)


                    # North
                    if self.rooms[i][j].north:
                        curr_width = 3 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_horizontal_3.png",
                                                         scale = WALL_SCALE,
                                                         image_width = 3*FLOOR_TILE_SIZE,
                                                         image_height = HORIZONTAL_WALL_HEIGHT,
                                                         center_x = int(x+0.5*FLOOR_TILE_SIZE + 0.5*curr_width),
                                                         center_y = int(y+8.5*FLOOR_TILE_SIZE + 0.5*HORIZONTAL_WALL_HEIGHT),hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_horizontal_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_list.append(self.wall_sprite)
                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_horizontal_3.png",
                                                         scale = WALL_SCALE,
                                                         image_width = 3 * FLOOR_TILE_SIZE,
                                                         image_height = HORIZONTAL_WALL_HEIGHT,
                                                         center_x = int(x + 5.5 * FLOOR_TILE_SIZE + 0.5*curr_width),
                                                         center_y = int(y + 8.5 * FLOOR_TILE_SIZE + 0.5*HORIZONTAL_WALL_HEIGHT), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_horizontal_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_list.append(self.wall_sprite)
                    else:
                        curr_width = 8 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_horizontal_8.png",
                                                         scale = WALL_SCALE,
                                                         image_width = 8 * FLOOR_TILE_SIZE,
                                                         image_height = HORIZONTAL_WALL_HEIGHT,
                                                         center_x = int(x + 0.5 * FLOOR_TILE_SIZE + 0.5*curr_width),
                                                         center_y = int(y + 8.5 * FLOOR_TILE_SIZE + 0.5*HORIZONTAL_WALL_HEIGHT), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_horizontal_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_list.append(self.wall_sprite)

                    # West
                    if self.rooms[i][j].west:
                        curr_height = 5.5 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_vertical_3.5_lower.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTICAL_WALL_WIDTH,
                                                         image_height=5.5 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5*VERTICAL_WALL_WIDTH),
                                                         center_y=int(y + 0.5*curr_height), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_vertical_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_front_list.append(self.wall_sprite)

                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_vertical_3.5.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTICAL_WALL_WIDTH,
                                                         image_height=5.5 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5 * VERTICAL_WALL_WIDTH),
                                                         center_y=int(y + 0.5 * curr_height + 5.5 * FLOOR_TILE_SIZE), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_vertical_fullh_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_back_list.append(self.wall_sprite)
                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_cover.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTICAL_WALL_WIDTH,
                                                         image_height=2 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5 * VERTICAL_WALL_WIDTH),
                                                         center_y=int(y + 10 * FLOOR_TILE_SIZE), hit_box_algorithm=None)
                        self.wall_cover_list.append(self.wall_sprite)

                        if not self.rooms[i][j-1].indoor:
                            self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_vertical_3.5_lower.png",
                                                             scale=WALL_SCALE,
                                                             image_width=VERTICAL_WALL_WIDTH,
                                                             image_height=5.5 * FLOOR_TILE_SIZE,
                                                             center_x=int(x + 0.5 * VERTICAL_WALL_WIDTH - VERTICAL_WALL_WIDTH),
                                                             center_y=int(y + 0.5 * curr_height),
                                                             hit_box_algorithm=None)
                            self.wall_sprite.hit_box = create_vertical_hitbox(self.wall_sprite.width,
                                                                           self.wall_sprite.height)
                            self.wall_front_list.append(self.wall_sprite)
                            self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_vertical_3.5.png",
                                                             scale=WALL_SCALE,
                                                             image_width=VERTICAL_WALL_WIDTH,
                                                             image_height=5.5 * FLOOR_TILE_SIZE,
                                                             center_x=int(x + 0.5 * VERTICAL_WALL_WIDTH - VERTICAL_WALL_WIDTH),
                                                             center_y=int(y + 0.5 * curr_height + 5.5 * FLOOR_TILE_SIZE),
                                                             hit_box_algorithm=None)
                            self.wall_sprite.hit_box = create_vertical_fullh_hitbox(self.wall_sprite.width,
                                                                                 self.wall_sprite.height)
                            self.wall_back_list.append(self.wall_sprite)

                    else:
                        curr_height = 11 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_vertical_9.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTICAL_WALL_WIDTH,
                                                         image_height=11 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5 * VERTICAL_WALL_WIDTH),
                                                         center_y=int(y + 0.5 * curr_height), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_vertical_fullh_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_front_list.append(self.wall_sprite)
                        if not self.rooms[i][j].west and not self.rooms[i][j - 1].indoor:
                            curr_height = 11 * FLOOR_TILE_SIZE
                            self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_vertical_9.png",
                                                             scale=WALL_SCALE,
                                                             image_width=VERTICAL_WALL_WIDTH,
                                                             image_height=11 * FLOOR_TILE_SIZE,
                                                             center_x=int(
                                                                 x + 0.5 * VERTICAL_WALL_WIDTH - VERTICAL_WALL_WIDTH),
                                                             center_y=int(y + 0.5 * curr_height),
                                                             hit_box_algorithm=None)
                            self.wall_sprite.hit_box = create_vertical_fullh_hitbox(self.wall_sprite.width,
                                                                                 self.wall_sprite.height)
                            self.wall_back_list.append(self.wall_sprite)


                    self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_cover.png",
                                                     scale=WALL_SCALE,
                                                     image_width=VERTICAL_WALL_WIDTH,
                                                     image_height=2 * FLOOR_TILE_SIZE,
                                                     center_x=int(x + 0.5 * VERTICAL_WALL_WIDTH),
                                                     center_y=int(y + 10 * FLOOR_TILE_SIZE),
                                                     hit_box_algorithm=None)
                    self.wall_cover_list.append(self.wall_sprite)

                    # east
                    if self.rooms[i][j].east:
                        curr_height = 5.5 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_vertical_3.5_lower.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTICAL_WALL_WIDTH,
                                                         image_height=5.5 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5*VERTICAL_WALL_WIDTH + 8.5 * FLOOR_TILE_SIZE),
                                                         center_y=int(y + 0.5*curr_height), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_vertical_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_front_list.append(self.wall_sprite)

                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_vertical_3.5.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTICAL_WALL_WIDTH,
                                                         image_height=5.5 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5*VERTICAL_WALL_WIDTH + 8.5 * FLOOR_TILE_SIZE),
                                                         center_y=int(y + 0.5*curr_height + 5.5 * FLOOR_TILE_SIZE), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_vertical_fullh_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_back_list.append(self.wall_sprite)

                    else:
                        curr_height = 11 * FLOOR_TILE_SIZE
                        self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_vertical_9.png",
                                                         scale=WALL_SCALE,
                                                         image_width=VERTICAL_WALL_WIDTH,
                                                         image_height=11 * FLOOR_TILE_SIZE,
                                                         center_x=int(x + 0.5 * VERTICAL_WALL_WIDTH + 8.5 * FLOOR_TILE_SIZE),
                                                         center_y=int(y + 0.5 * curr_height), hit_box_algorithm=None)
                        self.wall_sprite.hit_box = create_vertical_fullh_hitbox(self.wall_sprite.width, self.wall_sprite.height)
                        self.wall_back_list.append(self.wall_sprite)

                    self.wall_sprite = arcade.Sprite("sprites/world/wall/wall_cover.png",
                                                     scale=WALL_SCALE,
                                                     image_width=VERTICAL_WALL_WIDTH,
                                                     image_height=2 * FLOOR_TILE_SIZE,
                                                     center_x=int(x + 0.5 * VERTICAL_WALL_WIDTH + 8.5 * FLOOR_TILE_SIZE),
                                                     center_y=int(y + 10 * FLOOR_TILE_SIZE),
                                                     hit_box_algorithm=None)
                    self.wall_cover_list.append(self.wall_sprite)

                    # Make the floors
                    vertical_offset = 0
                    horizontal_offset = 0
                    horizontal_range_reduction = 0
                    vertical_range_reduction = 0
                    # If we are on the south edge
                    if i == 0:
                        vertical_offset = FLOOR_TILE_SIZE
                        vertical_range_reduction = 1
                    # If we are on the west edge
                    if j == 0:
                        horizontal_offset = FLOOR_TILE_SIZE
                        horizontal_range_reduction = 1

                    for k in range(9 - horizontal_range_reduction):
                        for l in range(9 - vertical_range_reduction):
                            self.floor_sprite = arcade.Sprite("sprites/world/misc/floor.png",
                                                              scale=WALL_SCALE,
                                                              image_width=FLOOR_TILE_SIZE,
                                                              image_height=FLOOR_TILE_SIZE,
                                                              center_x=int(x + k * FLOOR_TILE_SIZE + horizontal_offset),
                                                              center_y=int(y + l * FLOOR_TILE_SIZE + vertical_offset))
                            self.floor_list_indoor.append(self.floor_sprite)


        # sort sprite list by y coordinate, so they will be drawn in the correct order
        self.wall_list.sort(key = create_y_pos_comparison, reverse=True)

    def get_adj_rooms(self, room: Room):
        """ Method for finding the adjacent rooms of a given room, useful for enemies to know where they can move """
        adj_rooms = []
        for r in range(len(self.rooms)):
            for c in range(len(self.rooms[r])):
                # Add each adjacent room
                if self.rooms[r][c] == room:
                    # North
                    if r + 1 <= len(self.rooms)-1:
                        adj_rooms.append(self.rooms[r+1][c])
                    else:
                        adj_rooms.append(None)
                    # South
                    if r > 0:
                        adj_rooms.append(self.rooms[r-1][c])
                    else:
                        adj_rooms.append(None)
                    # East
                    if c + 1 <= len(self.rooms[r]) - 1:
                        adj_rooms.append(self.rooms[r][c+1])
                    else:
                        adj_rooms.append(None)
                    # West
                    if c > 0:
                        adj_rooms.append(self.rooms[r][c-1])
                    else:
                        adj_rooms.append(None)
                    return adj_rooms
        return None

    def find_room(self, vec2_pos: pyglet.math.Vec2):
        """ Helper method for enemy to find a room """
        room: Room
        r = 0
        for room_r in self.rooms:
            c = 0
            for room in room_r:
                right = room.x + ROOM_SIZE
                top = room.y + ROOM_SIZE
                if room.x < vec2_pos.x < right and room.y < vec2_pos.y < top:
                    return room
                c += 1
            r += 1

        return None

    def setup(self):
        pass