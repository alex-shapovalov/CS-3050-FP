import arcade
import random
import math
import time

import pyglet.math

SPRITE_SCALING = 0.5
ENEMY_SPEED = 250
PUSHBACK_SPEED = ENEMY_SPEED / 2
PLAYER_PADDING = 1
COL_BUFFER = 5
RAND_MOVE_TIME = 2
CHANGE_MOVE_TIME = 4
TARGET_DOOR_BUFFER = 20
STUCK_TIME = 8
MAX_CHASE_TIME = 1.5
CHASE_RANGE = 20

TARGETS = {
    "player": 3,
    "door": 2,
    "center": 1,
    "wander": 0
}


class Enemy(arcade.Sprite):
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
        self.target = None
        self.target_type = TARGETS["wander"]
        self.move_time = 0
        self.chase_time = 0
        self.room = world.find_room(pyglet.math.Vec2(self.center_x, self.center_y))
        self.wait_until_room = False
        self.next_center_loc = None

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

        # Determine which self.room we are in:

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

    def update(self, delta_time: float = 1 / 60):

        self.move_time += delta_time
        self.chase_time += delta_time

        player_room = self.world.find_room(pyglet.math.Vec2(self.player.center_x, self.player.center_y))
        chasing = False

        if self.wait_until_room and self.move_time > STUCK_TIME:
            self.wait_until_room = False

        # Check if the enemy is in the same room, if not see if we are chasing hte player into another room
        if self.room != player_room and self.chase_time <= MAX_CHASE_TIME and self.target_type == TARGETS["player"]:
            chasing = True

        # Determines if the enemy should follow the player or randomly move around the world
        if self.target is None or (
                not chasing and self.move_time >= CHANGE_MOVE_TIME and not self.wait_until_room):
            self.next_center_loc = None
            # Have enemy randomly choose how to walk: 1->pick a door to go through | 2-4->randomly move in the current room
            choice = random.randint(1, 4)
            if choice == 1:
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
                if self.room.south:
                    door_loc = pyglet.math.Vec2(self.room.x + self.room.size / 2, self.room.y + TARGET_DOOR_BUFFER * 2)
                    next_room_center.append(pyglet.math.Vec2(self.room.x + self.room.size / 2,
                                                             self.room.y - self.room.size / 2))
                    doors.append(door_loc)
                if self.room.east:
                    door_loc = pyglet.math.Vec2(self.room.x + self.room.size - TARGET_DOOR_BUFFER * 2,
                                                self.room.y + self.room.size / 2)
                    next_room_center.append(pyglet.math.Vec2(self.room.x + self.room.size + self.room.size / 2,
                                                             self.room.y + self.room.size / 2))
                    doors.append(door_loc)
                if self.room.west:
                    door_loc = pyglet.math.Vec2(self.room.x + TARGET_DOOR_BUFFER * 2, self.room.y + self.room.size / 2)
                    next_room_center.append(
                        pyglet.math.Vec2(self.room.x - self.room.size / 2, self.room.y + self.room.size / 2))
                    doors.append(door_loc)

                # Choose a random door
                room_choice = random.randint(0, len(doors) - 1)
                door_choice = doors[room_choice]
                self.next_center_loc = next_room_center[room_choice]

                # Update current target
                self.target = door_choice
                self.target_type = TARGETS["door"]

                # Ensures we only change our target once we enter the new room
                self.wait_until_room = True

            else:
                # Picks a random point within our current room and sets our target to wander
                self.target = pyglet.math.Vec2(random.randint(self.room.x + 80, self.room.x + self.room.size - 80),
                                               random.randint(self.room.y + 80, self.room.y + self.room.size - 80))
                self.target_type = TARGETS["wander"]

            self.move_time = 0

        elif self.room == player_room or chasing:
            # If we are in the room with the player go towards the player
            self.target = pyglet.math.Vec2(self.player.center_x, self.player.center_y)
            self.target_type = TARGETS["player"]

        self.calculate_distance()

        x_diff = self.target.x - self.center_x
        y_diff = self.target.y - self.center_y
        angle = math.atan2(y_diff, x_diff)

        self.change_x = 0
        self.change_y = 0

        # If enemy distance is further than player padding
        if self.distance > 20:
            # Enemy moves towards the target
            self.change_x = math.cos(angle) * ENEMY_SPEED
            self.change_y = math.sin(angle) * ENEMY_SPEED

        elif self.distance <= 20 and self.target_type == TARGETS["door"]:
            self.target = self.next_center_loc
            self.target_type = TARGETS["center"]
            self.next_center_loc = None

        # If our target is player and we are still in range, reset chase timer
        if self.distance <= CHASE_RANGE and self.target_type == TARGETS["player"]:
            self.chase_time = 0

        # elif self.distance < PLAYER_PADDING and self.target_type == TARGETS["player"]:
        #     # Invincibility frames
        #     self.player.player_receive_damage(self.damage)
        #
        #     # If player is walking towards an enemy
        #     if ((self.player.change_x > 0 > x_diff) or
        #             (self.player.change_x < 0 < x_diff) or
        #             (self.player.change_y > 0 > y_diff) or
        #             (self.player.change_y < 0 < y_diff)):
        #         # Push the enemy back if the player is moving towards them
        #         self.change_x = math.cos(angle) * -PUSHBACK_SPEED
        #         self.change_y = math.sin(angle) * -PUSHBACK_SPEED
        #
        # # Checking for enemy overlaps
        # for enemy in self.enemy_list:
        #     if enemy == self:
        #         continue
        #
        #     self.calculate_distance()
        #
        #     # Keep enemies from overlapping
        #     if self.distance < PLAYER_PADDING:
        #         x_diff = enemy.center_x - self.center_x
        #         y_diff = enemy.center_y - self.center_y
        #         angle_away_from_enemy = math.atan2(y_diff, x_diff)
        #
        #         # Separate them at pushback_speed
        #         self.change_x -= math.cos(angle_away_from_enemy) * PUSHBACK_SPEED
        #         self.change_y -= math.sin(angle_away_from_enemy) * PUSHBACK_SPEED

        # Ensures that if the enemies collide with a wall then they won't continually try to run into it,
        # causing the enemy to go into the wall hitbbox
        wall = (self.collides_with_list(self.world.wall_list) + self.collides_with_list(self.world.wall_front_list) +
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
            # This means we made it into the desired room
            self.wait_until_room = False

    def calculate_distance(self):
        self.distance = math.sqrt((self.target.x - self.center_x) ** 2 + (self.target.y - self.center_y) ** 2)

    def enemy_receive_damage(self):
        self.health -= self.player_damage
        if self.health <= 0:
            self.kill()
            # TODO: Add some sort of death effect / blood

    # TODO: Player takes self.damage damage, create player receive_damage class
    def enemy_give_damage(self):
        if self.attack_type == "melee":
            # Player is damaged by contact
            self.player.player_receive_damage(self.damage)
        elif self.attack_type == "ranged":
            x = 0
            # Player is damaged if projectile hits him
