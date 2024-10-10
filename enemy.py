import arcade
import random
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

SPRITE_SCALING = 0.5
ENEMY_SPEED = 4
PUSHBACK_SPEED = ENEMY_SPEED / 2
PLAYER_PADDING = 150

class Enemy(arcade.Sprite):
    def __init__(self, player_sprite, enemy_list, image="enemy.png", scaling=SPRITE_SCALING):
        super().__init__(image, scaling)
        self.player_sprite = player_sprite
        self.enemy_list = enemy_list

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

    def update(self):
        distance = math.sqrt((self.player_sprite.center_x - self.center_x) ** 2 + (self.player_sprite.center_y - self.center_y) ** 2)

        x_diff = self.player_sprite.center_x - self.center_x
        y_diff = self.player_sprite.center_y - self.center_y
        angle = math.atan2(y_diff, x_diff)

        is_player_moving_towards_enemy = (
                (self.player_sprite.change_x > 0 and x_diff < 0) or
                (self.player_sprite.change_x < 0 and x_diff > 0) or
                (self.player_sprite.change_y > 0 and y_diff < 0) or
                (self.player_sprite.change_y < 0 and y_diff > 0))

        if distance > PLAYER_PADDING:
            # Enemy moves towards the player
            self.change_x = math.cos(angle) * ENEMY_SPEED
            self.change_y = math.sin(angle) * ENEMY_SPEED

        elif is_player_moving_towards_enemy:
            # Push the enemy back if the player is moving towards them
            self.change_x = math.cos(angle) * -PUSHBACK_SPEED
            self.change_y = math.sin(angle) * -PUSHBACK_SPEED

        else:
            self.change_x = 0
            self.change_y = 0

        for enemy in self.enemy_list:
            if enemy == self:
                continue

            distance = math.sqrt((enemy.center_x - self.center_x) ** 2 + (enemy.center_y - self.center_y) ** 2)

            # Keep enemies from overlapping
            if distance < PLAYER_PADDING:
                x_diff = enemy.center_x - self.center_x
                y_diff = enemy.center_y - self.center_y
                angle_away_from_enemy = math.atan2(y_diff, x_diff)

                # Seperate them at pushback_speed
                self.change_x -= math.cos(angle_away_from_enemy) * PUSHBACK_SPEED
                self.change_y -= math.sin(angle_away_from_enemy) * PUSHBACK_SPEED

        super().update()
