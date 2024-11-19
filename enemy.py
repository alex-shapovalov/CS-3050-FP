import arcade
import random
import math
import time
from damage import DamageText

import pyglet.math

SPRITE_SCALING = 0.5
ENEMY_SPEED = 250
PUSHBACK_SPEED = ENEMY_SPEED / 2
PLAYER_PADDING = 50
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

TARGETS = {
    "wait": 4,
    "player": 3,
    "door": 2,
    "center": 1,
    "wander": 0
}


def load_texture_pair(filename):
    """
        Load a texture pair, with the second being a mirror image.
        """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


class Enemy(arcade.Sprite):
    """ Class which handles enemy logic, movement, and damage """

    def __init__(self, player, player_damage, enemy_list, world, sprite_scaling, screen_width, screen_height,
                 health=100, damage=10, attack_type="melee", image="enemy.png"):
        super().__init__(image, sprite_scaling)
        self.player = player
        self.player_damage = player_damage
        self.enemy_list = enemy_list
        self.world = world
        self.health = health
        self.damage = damage
        self.attack_type = attack_type
        self.distance = None
        self.last_damage_time = 0
        self.collide = False
        self.damage_text = []

        # Spawn somewhere random
        spawn_location = random.choice(["top", "bottom", "left", "right"])
        if spawn_location == "top":
            self.center_x = random.randint(0, screen_width)
            self.center_y = screen_height + 50
        elif spawn_location == "bottom":
            self.center_x = random.randint(0, screen_width)
            self.center_y = -50
        elif spawn_location == "left":
            self.center_x = -50
            self.center_y = random.randint(0, screen_height)
        elif spawn_location == "right":
            self.center_x = screen_width + 50
            self.center_y = random.randint(0, screen_height)

        self.target = pyglet.math.Vec2(self.center_x, self.center_y)
        self.target_type = TARGETS["wait"]
        self.move_time = 0
        self.chase_time = 0
        self.room = world.find_room(pyglet.math.Vec2(self.center_x, self.center_y))
        self.adj_rooms = world.get_adj_rooms(self.room)
        self.wait_until_room = False
        self.next_center_loc = None
        self.near_center = False

        # Determine which self.room we are in:

        self.rand_num = random.randint(1, 3)

        hitbox = []
        self.hitbox_width = self.width
        self.hitbox_height = self.height / 3
        num_points = 20  # Adjust for more precision
        for i in range(num_points):
            angle = math.radians(360 / num_points * i)
            x = self.hitbox_width * math.cos(angle)
            y = self.hitbox_height * math.sin(angle) - self.height
            hitbox.append((x, y))
        self.set_hit_box(hitbox)

        self.facing = FACING_RIGHT

        if self.rand_num == SKELETON:
            self.idle_texture_pair = load_texture_pair(f"enemy.png")

            self.walk_curr_texture = 0
            self.walking_animation = []
            for i in range(4):
                filename = f'Skele_anim/skele_anim-f{i + 1}.png'
                texture = load_texture_pair(filename)
                self.walking_animation.append(texture)
        elif self.rand_num == ZOMBIE:
            self.idle_texture_pair = load_texture_pair(f"Zombie_anim/zomb_anim-f1.png")

            self.walk_curr_texture = 0
            self.walking_animation = []
            for i in range(4):
                filename = f'Zombie_anim/zomb_anim-f{i + 1}.png'
                texture = load_texture_pair(filename)
                self.walking_animation.append(texture)
        else:
            self.idle_texture_pair = load_texture_pair(f"ghost.png")

    def update_targets(self, delta_time):
        if self.rand_num != GHOST:
            # Update timers for enemy movement
            self.calculate_distance()
            self.move_time += delta_time


            chasing = False

            # If an enemy gets stuck trying to get into a room, after a certain amount of trying the enemy gives up
            if self.wait_until_room and self.move_time > STUCK_TIME:
                self.wait_until_room = False


            # Check if the enemy is in the same room, if not see if we are chasing hte player into another room
            if self.room != self.player.room and self.chase_time <= MAX_CHASE_TIME and self.target_type == TARGETS[
                "player"]:
                self.chase_time += delta_time
                chasing = True

            # Determines if the enemy should follow the player or randomly move around the world
            if not chasing and self.move_time >= CHANGE_MOVE_TIME and not self.wait_until_room and not self.near_center:
                # Have enemy randomly choose how to walk: 1->pick a door to go through | 2-4->randomly move in the current room
                choice = random.randint(1, 4)
                if choice != 1:
                    # find the doors of the current room
                    self.next_center_loc = None
                    doors, next_room_center = self.find_doors()

                    options = [i for i in range(len(doors)) if doors[i]]
                    # if not self.room.indoor:
                    #     options += [room for room in self.adj_rooms if room.indoor]

                    # Choose a random doors
                    room_choice = random.randint(0, len(options) - 1)

                    if not self.room.indoor and not self.adj_rooms[options[room_choice]].indoor:
                        # We chose an adjacent outdoor room, no need to go through a door
                        self.target = pyglet.math.Vec2(
                            random.randint(self.adj_rooms[options[room_choice]].x + 100,
                                           self.adj_rooms[options[room_choice]].x + self.room.size - 100),
                            random.randint(self.adj_rooms[options[room_choice]].y + 100,
                                           self.adj_rooms[options[room_choice]].y + self.room.size - 100))
                        self.target_type = TARGETS["wander"]
                        # print("wander outdoors")


                    else:
                        # We chose an indoor room we must go through the door:
                        door_choice = doors[options[room_choice]]
                        self.next_center_loc = next_room_center[options[room_choice]]

                        # Update current target
                        self.target = door_choice
                        self.target_type = TARGETS["door"]
                        # print("go through door")

                        # Ensures we only change our target once we enter the new room
                    self.wait_until_room = True

                else:
                    # Picks a random point within our current room and sets our target to wander
                    self.target = pyglet.math.Vec2(
                        random.randint(self.room.x + 100, self.room.x + self.room.size - 100),
                        random.randint(self.room.y + 100, self.room.y + self.room.size - 100))
                    self.target_type = TARGETS["wander"]
                    # print("wander")

                self.move_time = 0

            elif self.room != self.player.room and chasing:
                # If we are chasing the player and they enter another room, chase them into that room
                doors, next_room_center = self.find_doors()
                choice = -1
                if self.player.room.x - 5 <= self.room.x <= self.player.room.x + 5:
                    if self.player.room.y > self.room.y:
                        choice = 0
                    else:
                        choice = 1
                else:
                    if self.player.room.x > self.room.x:
                        choice = 2
                    else:
                        choice = 3

                # If the player moved into another outdoor tile, we dont need to worry about going through doors
                if not self.room.indoor and not self.adj_rooms[choice].indoor:
                    self.target = pyglet.math.Vec2(self.player.center_x, self.player.center_y)
                    self.target_type = TARGETS["player"]
                    # print("chase between outdoor")
                else:
                    # player went through a door so we must too
                    self.target = doors[choice]
                    self.next_center_loc = next_room_center[choice]
                    self.target_type = TARGETS["door"]
                    self.wait_until_room = True
                    # print("chase through door")
                self.move_time = 0

            elif self.room == self.player.room:
                # # If we are in the room with the player go towards the player
                self.target = pyglet.math.Vec2(self.player.center_x, self.player.center_y)
                self.target_type = TARGETS["player"]

            elif self.move_time < CHANGE_MOVE_TIME and self.distance <= 10:
                self.target_type = TARGETS["wait"]
                self.target = pyglet.math.Vec2(self.center_x, self.center_y)
                # print("waiting")
        else:
            self.target = pyglet.math.Vec2(self.player.center_x, self.player.center_y)
            self.target_type = TARGETS["player"]

        if self.target == None:
            # print("target was none")
            self.target = pyglet.math.Vec2(self.center_x, self.center_y)
            self.target_type = TARGETS["wait"]

    def update_walls_room(self):
        wall = (self.collides_with_list(self.world.wall_list) + self.collides_with_list(
            self.world.wall_front_list) +
                self.collides_with_list(self.world.wall_back_list))

        if wall:
            # Checks every wall we are colliding with to make sure we cant run further in that direction
            for w in wall:
                if w.left + COL_BUFFER < self.center_x < w.right - COL_BUFFER:
                    if (w.center_y - w.height < self.center_y - self.height and self.change_y < 0) or (
                            w.center_y - w.height > self.center_y - self.height and self.change_y > 0):
                        self.change_y = 0
                elif w.bottom + COL_BUFFER < self.center_y - self.height < w.top - COL_BUFFER:
                    if (w.center_x - w.width < self.center_x + self.width and self.change_x < 0) or (
                            w.center_x + w.width > self.center_x - self.width and self.change_x > 0):
                        self.change_x = 0

        curr_room = self.world.find_room(pyglet.math.Vec2(self.center_x, self.center_y))
        if self.room != curr_room:
            self.room = curr_room
            self.adj_rooms = self.world.get_adj_rooms(self.room)
            # This means we made it into the desired room
            self.wait_until_room = False
            self.chase_time = 0

    def update(self, delta_time: float = 1 / 60):
        """ Constantly re-calculates where the player is for following along with collisions and pushbacks """

        # See if our current target needs to be updated
        self.update_targets(delta_time)

        x_diff = self.target.x - self.center_x
        y_diff = self.target.y - self.center_y
        angle = math.atan2(y_diff, x_diff)

        self.change_x = 0
        self.change_y = 0
        self.calculate_distance()

        if self.distance > 20:
            # Enemy moves towards the target
            self.change_x = math.cos(angle) * ENEMY_SPEED
            self.change_y = math.sin(angle) * ENEMY_SPEED
        elif self.distance <= 20 and self.target_type == TARGETS["door"]:
            # print("door now to center")
            self.target = self.next_center_loc
            self.target_type = TARGETS["center"]
            self.wait_until_room = False
            self.near_center = True
            self.next_center_loc = None
        elif self.distance <= self.room.size / 2 and self.target_type == TARGETS["center"]:
            self.near_center = False

        # If our target is player and we are still in range, reset chase timer
        if self.distance <= CHASE_RANGE and self.target_type == TARGETS["player"]:
            self.chase_time = 0

        if self.distance < PLAYER_PADDING and self.target_type == TARGETS["player"]:
            # Invincibility frames
            self.player.player_receive_damage(self.damage)

            # If player is walking towards an enemy
            if ((self.player.change_x > 0 > x_diff) or
                    (self.player.change_x < 0 < x_diff) or
                    (self.player.change_y > 0 > y_diff) or
                    (self.player.change_y < 0 < y_diff)):
                # Push the enemy back if the player is moving towards them
                self.change_x = math.cos(angle) * -PUSHBACK_SPEED
                self.change_y = math.sin(angle) * -PUSHBACK_SPEED

        # Checking for enemy overlaps
        for enemy in self.enemy_list:
            if enemy == self:
                continue

            enemy_dist = math.sqrt((self.target.x - self.center_x) ** 2 + (self.target.y - self.center_y) ** 2)

            # Keep enemies from overlapping
            if enemy_dist < PLAYER_PADDING:
                x_diff = enemy.center_x - self.center_x
                y_diff = enemy.center_y - self.center_y
                angle_away_from_enemy = math.atan2(y_diff, x_diff)

                # Separate them at pushback_speed
                self.change_x -= math.cos(angle_away_from_enemy) * PUSHBACK_SPEED
                self.change_y -= math.sin(angle_away_from_enemy) * PUSHBACK_SPEED

        # Ensures that if the non-ghost enemies collide with a wall then they won't continually
        # try to run into it, causing the enemy to go into the wall hitbbox
        if self.rand_num != GHOST:
            self.update_walls_room()

        temp_const = 10

        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.idle_texture_pair[self.facing]
        else:
            if self.change_x < 0 and (self.change_y < 0 or self.change_y > 0):
                self.facing = FACING_LEFT
            elif self.change_x > 0 and (self.change_y < 0 or self.change_y > 0):
                self.facing = FACING_RIGHT
            elif self.change_x < 0:
                self.facing = FACING_LEFT
            elif self.change_x > 0:
                self.facing = FACING_RIGHT
            if self.rand_num == ZOMBIE or self.rand_num == SKELETON:
                # walking animation code
                self.walk_curr_texture += delta_time * 10
                if self.walk_curr_texture >= len(self.walking_animation):
                    self.walk_curr_texture = 0
                    self.is_attacking = False
                self.texture = self.walking_animation[int(self.walk_curr_texture)][self.facing]
            else:
                self.texture = self.idle_texture_pair[self.facing]

    def calculate_distance(self):
        """ Calculates distance between enemy and player """
        self.distance = math.sqrt((self.target.x - self.center_x) ** 2 + (self.target.y - self.center_y) ** 2)

    def find_doors(self):
        doors = []
        next_room_center = []
        # Check to see what doors the current room has:
        # Each if stores the doors location and the center of the room on the other side
        if self.room.north:
            door_loc = pyglet.math.Vec2(self.room.x + self.room.size / 2,
                                        self.room.y + self.room.size - TARGET_DOOR_BUFFER)
            next_room_center.append(pyglet.math.Vec2(self.room.x + self.room.size / 2,
                                                     self.room.y + self.room.size + self.room.size / 2))
            doors.append(door_loc)
        else:
            next_room_center.append(None)
            doors.append(None)

        if self.room.south:
            door_loc = pyglet.math.Vec2(self.room.x + (self.room.size / 2), self.room.y + TARGET_DOOR_BUFFER * 6)
            next_room_center.append(pyglet.math.Vec2(self.room.x + self.room.size / 2,
                                                     self.room.y - self.room.size / 2))
            doors.append(door_loc)
        else:
            next_room_center.append(None)
            doors.append(None)

        if self.room.east:
            door_loc = pyglet.math.Vec2(self.room.x + self.room.size - TARGET_DOOR_BUFFER * 2,
                                        self.room.y + self.room.size / 2)
            next_room_center.append(pyglet.math.Vec2(self.room.x + self.room.size + self.room.size / 2,
                                                     self.room.y + self.room.size / 2))
            doors.append(door_loc)
        else:
            next_room_center.append(None)
            doors.append(None)

        if self.room.west:
            door_loc = pyglet.math.Vec2(self.room.x + TARGET_DOOR_BUFFER * 2, self.room.y + self.room.size / 2)
            next_room_center.append(
                pyglet.math.Vec2(self.room.x - self.room.size / 2, self.room.y + self.room.size / 2))
            doors.append(door_loc)
        else:
            next_room_center.append(None)
            doors.append(None)

        return doors, next_room_center

    def draw_damage_texts(self):
        """ Draws damage texts on enemy hit """
        for text in self.damage_text:
            text.draw()

    def update_damage_texts(self):
        """ Removes expired texts from the list """
        self.damage_text = [text for text in self.damage_text if text.update()]

    def enemy_receive_damage(self):
        """ Gives damage to a hit enemy """
        self.damage_text.append(DamageText(self.center_x, self.center_y, self.player_damage))
        self.health -= self.player_damage
        if self.health <= 0:
            self.kill()
            self.player.score += 1

    def enemy_give_damage(self):
        """ Gives damage from an enemy to the player """
        if self.attack_type == "melee":
            # Player is damaged by contact
            self.player.player_receive_damage(self.damage)
