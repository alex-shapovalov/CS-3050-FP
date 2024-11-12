import arcade
import pymunk
import math
import time
import enemy

PLAYER_PADDING = 150
UPDATES_PER_FRAME = 5
WALL_WIDTH = 79

FACING_RIGHT = 0
FACING_LEFT = 1

def load_texture_pair(filename):
        """
        Load a texture pair, with the second being a mirror image.
        """
        return [
            arcade.load_texture(filename),
            arcade.load_texture(filename, flipped_horizontally=True)
        ]

class Player(arcade.Sprite):
    """ Player Class """

    
    def __init__(self, health, damage, sprite_scaling, screen_width, screen_height):
        """Initialize player"""

        # initialize player
        super().__init__(
            scale=sprite_scaling
        )


        # following values are subject to change
        self.health: int = health
        self.damage: int = damage

        self.center_x = screen_width / 2
        self.center_y = screen_height / 2

        self.original_texture = arcade.load_texture("player.png")
        self.width = self.original_texture.width/2
        self.height = self.original_texture.height

        hitbox = []
        self.hitbox_width = self.width/3
        self.hitbox_height = self.height/6
        num_points = 20  # Adjust for more precision
        for i in range(num_points):
            angle = math.radians(360 / num_points * i)
            x = self.hitbox_width * math.cos(angle)
            y = self.hitbox_height * math.sin(angle) - self.height/2
            hitbox.append((x, y))
        self.set_hit_box(hitbox)

        self.velocity = [0,0]

        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.damaged = False
        self.damaged_time = 0

        self.is_attacking = False

        self.facing = FACING_RIGHT

        self.idle_texture_pair = load_texture_pair(f"player.png")
        self.walking_texture_pair = load_texture_pair(f"player.png")
        self.damaged_texture = arcade.load_texture_pair("player_damaged.png")

        self.attack_curr_texture = 0
        self.attack_animation = []
        for i in range(3):
            filename = f'player_anim_frames/player-f{i+1}.png'
            texture = load_texture_pair(filename)
            self.attack_animation.append(texture)

        self.walk_curr_texture = 0
        self.walking_animation = []
        for i in range(4):
            filename = f'player_walk_anim/player_walk-f{i+1}.png'
            texture = load_texture_pair(filename)
            self.walking_animation.append(texture)
        

    def update_velocity(self, vel):
        if vel[0] != -1:
            self.velocity[0] = vel[0]
        if vel[1] != -1:
            self.velocity[1] = vel[1]

        return self.velocity
    

    def update(self):
        if self.damaged and time.time() - self.damaged_time > 0.2:
            self.damaged = False

        if self.is_attacking:
            self.attack_curr_texture += .5
            if self.attack_curr_texture >= len(self.attack_animation):
                self.attack_curr_texture = 0
                self.is_attacking = False
            self.texture = self.attack_animation[int(self.attack_curr_texture)][self.facing] 
        else:
            if self.change_x == 0 and self.change_y == 0 and not self.damaged:
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

                if not self.damaged:
                    self.texture = self.walking_texture_pair[self.facing]

                self.walk_curr_texture += 0.35
                if self.walk_curr_texture >= len(self.walking_animation):
                    self.walk_curr_texture = 0
                    self.is_attacking = False
                self.texture = self.walking_animation[int(self.walk_curr_texture)][self.facing] 

    def player_receive_damage(self, amount):
        # Invincibility frames
        if time.time() - self.damaged_time >= 1.5:
            self.texture = self.damaged_texture[self.facing]
            self.health -= amount
            self.damaged = True
            self.damaged_time = time.time()
            if self.health <= 0:
                self.kill()
        else:
            pass

    def player_give_damage(self, enemy_list):
        for enemy in enemy_list:
            enemy.calculate_distance() # recalculate distance to ensure player can always hit enemy in range
            if enemy.distance <= WALL_WIDTH: # this if statement is subject to change
                enemy.enemy_receive_damage()
