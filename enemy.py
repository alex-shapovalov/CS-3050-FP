import arcade
import random
import math

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 1000

SPRITE_SCALING = 0.5
ENEMY_SPEED = 250
PUSHBACK_SPEED = ENEMY_SPEED / 2
PLAYER_PADDING = 150
COL_BUFFER = 5

class Enemy(arcade.Sprite):
    def __init__(self, player_sprite, enemy_list, wall_list, health = 100, damage = 10, attack_type = "melee", image="enemy.png", scaling=SPRITE_SCALING):
        super().__init__(image, scaling)
        self.player_sprite = player_sprite
        self.enemy_list = enemy_list
        self.wall_list = wall_list
        self.health = health
        self.damage = damage
        self.attack_type = attack_type
        self.collide = False


        # Spawn somewhere random
        spawn_location = random.choice(["top", "bottom", "left", "right"])
        if spawn_location == "top":
            self.center_x = random.randint(0, SCREEN_WIDTH)
            self.center_y = SCREEN_HEIGHT + 50
        elif spawn_location == "bottom":
            self.center_x = random.randint(0, SCREEN_WIDTH)
            self.center_y = -50
        elif spawn_location == "left":
            self.center_x = -50
            self.center_y = random.randint(0, SCREEN_HEIGHT)
        elif spawn_location == "right":
            self.center_x = SCREEN_WIDTH + 50
            self.center_y = random.randint(0, SCREEN_HEIGHT)

        # self.tex = arcade.Sprite("enemy.png", scale=SPRITE_SCALING, center_x=self.center_x, center_y=self.center_y)

        # self.width = self.tex.width
        # self.height = self.tex.height/3

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


    def update(self):
        distance = math.sqrt((self.player_sprite.center_x - self.center_x) ** 2 + (self.player_sprite.center_y - self.center_y) ** 2)

        x_diff = self.player_sprite.center_x - self.center_x
        y_diff = self.player_sprite.center_y - self.center_y
        angle = math.atan2(y_diff, x_diff)

        self.change_x = 0
        self.change_y = 0

        # If enemy distance is further than player padding
        if distance > PLAYER_PADDING:
            # Enemy moves towards the player
            self.change_x = math.cos(angle) * ENEMY_SPEED
            self.change_y = math.sin(angle) * ENEMY_SPEED

        # If player is walking towards an enemy
        elif ((self.player_sprite.change_x > 0 and x_diff < 0) or
              (self.player_sprite.change_x < 0 and x_diff > 0) or
              (self.player_sprite.change_y > 0 and y_diff < 0) or
              (self.player_sprite.change_y < 0 and y_diff > 0)):
            # Push the enemy back if the player is moving towards them
            self.change_x = math.cos(angle) * -PUSHBACK_SPEED
            self.change_y = math.sin(angle) * -PUSHBACK_SPEED


        # Checking for enemy overlaps
        for enemy in self.enemy_list:
            if enemy == self:
                continue

            distance = math.sqrt((enemy.center_x - self.center_x) ** 2 + (enemy.center_y - self.center_y) ** 2)

            # Keep enemies from overlapping
            if distance < PLAYER_PADDING:
                x_diff = enemy.center_x - self.center_x
                y_diff = enemy.center_y - self.center_y
                angle_away_from_enemy = math.atan2(y_diff, x_diff)

                # Separate them at pushback_speed
                self.change_x -= math.cos(angle_away_from_enemy) * PUSHBACK_SPEED
                self.change_y -= math.sin(angle_away_from_enemy) * PUSHBACK_SPEED

        # Ensures that if the enemies collide with a wall then they would continually try to run into it,
        # causing the enemy to go into the wall hitbbox
        wall = self.collides_with_list(self.wall_list)
        if wall != []:
            # Checks every wall we are colliding with to make sure we cant run further in that direction
            for w in wall:
                if w.left + COL_BUFFER < self.center_x < w.right - COL_BUFFER and ((w.top >= self.bottom and self.change_y < 0) or (w.bottom <= self.top and self.change_y > 0)):
                    self.change_y = 0
                if w.bottom + COL_BUFFER < self.center_y-self.height/2 < w.top - COL_BUFFER and ((w.right >= self.left and self.change_x < 0) or (w.left <= self.right and self.change_x > 0)):
                    self.change_x = 0

        # super().update()

    def receive_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()
            #TODO: Add some sort of death effect / blood

    # TODO: Player takes self.damage damage, create player receive_damage class
    # def give_damage(self, player):
        # if self.attack_type == "melee":
            # Player is damaged by contact
            # self.player_sprite.receive_damage(self.damage)
        # elif self.attack_type == "ranged":
            # Player is damaged if projectile hits him
