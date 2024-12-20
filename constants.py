import arcade
import datetime

# constants.py file

# Game Settings
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "Game"
MOVEMENT_SPEED = 350
ENEMY_SPAWN_INTERVAL = 5
SPRITE_SCALING = 0.5
PLAYER_HEALTH = 100
PLAYER_DAMAGE = 50
ENEMY_HEALTH = 100
ENEMY_DAMAGE = 10
MAX_ENEMIES = 15
POTION_PADDING = 25
COLOR = arcade.color.AMAZON

# Enemy AI
ENEMY_SPEED = 250
PUSHBACK_SPEED = ENEMY_SPEED / 2
ENEMY_PLAYER_PADDING = 50
COL_BUFFER = 5
RAND_MOVE_TIME = 2
CHANGE_MOVE_TIME = 8
TARGET_DOOR_BUFFER = 25
STUCK_TIME = 8
MAX_CHASE_TIME = 1.5
CHASE_RANGE = 100
FACING_RIGHT = 0
FACING_LEFT = 1
SKELETON = 1
ZOMBIE = 2
GHOST = 3
GHOST_DMG_MULTIPLIER = 0.5
DROP_HEALING_POTION = 1
TARGETS = {
    "wait": 4,
    "player": 3,
    "door": 2,
    "center": 1,
    "wander": 0
}

# World Settings
FLOOR_TILE_SIZE = 80
HORIZONTAL_WALL_HEIGHT = 2.5 * FLOOR_TILE_SIZE
VERTICAL_WALL_WIDTH = 0.5 * FLOOR_TILE_SIZE
WALL_SCALE = 1
WORLD_SIZE = 5
ROOM_SIZE = 9 * FLOOR_TILE_SIZE # Room size in pyarcade units
SEED = int(datetime.datetime.now().timestamp()) # Seed for world generation
INDOOR_CUTOFF = 0.51 # Every room with a noise value greater than INDOOR_CUTOFF will be an indoor room. Must be between 0 and 1.
DOOR_CHANCE = 0.75 # The probability that a given wall will have a door.

# Misc Settings
PLAYER_PLAYER_PADDING = 150
UPDATES_PER_FRAME = 5
WALL_WIDTH = 79
HEALING_FACTOR = 10