import arcade
import random
import math
import time

ENEMY_SPEED = 4
PUSHBACK_SPEED = ENEMY_SPEED / 2
PLAYER_PADDING = 150

class Enemy(arcade.Sprite):
    def __init__(self, player, player_damage, enemy_list, sprite_scaling, screen_width, screen_height, health = 100, damage = 10, attack_type = "melee", image="enemy.png"):
        super().__init__(image, sprite_scaling)
        self.player = player
        self.player_damage = player_damage
        self.enemy_list = enemy_list
        self.health = health
        self.damage = damage
        self.attack_type = attack_type
        self.distance = None
        self.last_damage_time = 0

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

    def update(self):
        self.distance = math.sqrt((self.player.center_x - self.center_x) ** 2 + (self.player.center_y - self.center_y) ** 2)

        x_diff = self.player.center_x - self.center_x
        y_diff = self.player.center_y - self.center_y
        angle = math.atan2(y_diff, x_diff)

        # If enemy distance is further than player padding
        if self.distance > PLAYER_PADDING:
            # Enemy moves towards the player
            self.change_x = math.cos(angle) * ENEMY_SPEED
            self.change_y = math.sin(angle) * ENEMY_SPEED

        elif self.distance < PLAYER_PADDING:
            # Invincibility frames
            self.player.player_receive_damage(self.damage)

            # If player is walking towards an enemy
            if ((self.player.change_x > 0 and x_diff < 0) or
                    (self.player.change_x < 0 and x_diff > 0) or
                    (self.player.change_y > 0 and y_diff < 0) or
                    (self.player.change_y < 0 and y_diff > 0)):
                # Push the enemy back if the player is moving towards them
                self.change_x = math.cos(angle) * -PUSHBACK_SPEED
                self.change_y = math.sin(angle) * -PUSHBACK_SPEED

        else:
            self.change_x = 0
            self.change_y = 0

        # Checking for enemy overlaps
        for enemy in self.enemy_list:
            if enemy == self:
                continue

            self.distance = math.sqrt((enemy.center_x - self.center_x) ** 2 + (enemy.center_y - self.center_y) ** 2)

            # Keep enemies from overlapping
            if self.distance < PLAYER_PADDING:
                x_diff = enemy.center_x - self.center_x
                y_diff = enemy.center_y - self.center_y
                angle_away_from_enemy = math.atan2(y_diff, x_diff)

                # Separate them at pushback_speed
                self.change_x -= math.cos(angle_away_from_enemy) * PUSHBACK_SPEED
                self.change_y -= math.sin(angle_away_from_enemy) * PUSHBACK_SPEED

        super().update()

    def enemy_receive_damage(self):
        self.health -= self.player_damage
        if self.health <= 0:
            self.kill()
            #TODO: Add some sort of death effect / blood

    # TODO: Player takes self.damage damage, create player receive_damage class
    def enemy_give_damage(self):
        if self.attack_type == "melee":
            # Player is damaged by contact
            self.player.player_receive_damage(self.damage)
        elif self.attack_type == "ranged":
            x = 0
            # Player is damaged if projectile hits him