import arcade
import pymunk
import math
import time
import enemy

PLAYER_PADDING = 150
UPDATES_PER_FRAME = 5

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
        self.health: int = damage
        self.damage: int = health

        self.player.center_x = screen_width / 2
        self.player.center_y = screen_height / 2

        hitbox = []
        self.hitbox_width = self.width
        self.hitbox_height = self.height/3
        num_points = 20  # Adjust for more precision
        for i in range(num_points):
            angle = math.radians(360 / num_points * i)
            x = self.hitbox_width * math.cos(angle)
            y = self.hitbox_height * math.sin(angle) - self.height
            hitbox.append((x, y))
        self.set_hit_box(hitbox)

        self.velocity = [0,0]

        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.damaged = False
        self.damaged_time = 0
        self.original_texture = arcade.load_texture("player.png")
        self.damaged_texture = arcade.load_texture_pair("player_damaged.png")
        
        self.is_attacking = False
        self.last_attack_time = 0

        self.facing = FACING_RIGHT

        self.idle_texture_pair = load_texture_pair(f"player.png")

        self.walking_texture_pair = load_texture_pair(f"player.png")

        self.curr_texture = 0
        self.attack_animation = []
        for i in range(3):
            filename = f'player_anim_frames/player-f{i+1}.png'
            texture = load_texture_pair(filename)
            self.attack_animation.append(texture)
        


    def update_velocity(self, vel):
        if vel[0] != -1:
            self.velocity[0] = vel[0]
        if vel[1] != -1:
            self.velocity[1] = vel[1]

        return self.velocity
    

    def update(self):
        if self.damaged and time.time() - self.damaged_time > 0.2:
            self.damaged = False

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
            self.texture = self.walking_texture_pair[self.facing]

        if self.is_attacking:
            self.curr_texture += 0.35
            if self.curr_texture >= len(self.attack_animation):
                self.curr_texture = 0
                self.is_attacking = False
            self.texture = self.attack_animation[int(self.curr_texture)][self.facing] 

    def player_receive_damage(self, amount):
        # Invincibility frames
        if time.time() - self.damaged_time >= 1.5:
            self.texture = self.damaged_texture[self.facing]
            self.health -= amount
            self.damaged = True
            self.damaged_time = time.time()
            print(f"Player received damage")
            if self.health <= 0:
                self.kill()
        else:
            pass

    def player_give_damage(self, enemy_list):
        enemies_to_damage = []
        for enemy in enemy_list:
            if enemy.distance <= PLAYER_PADDING + 250:
                enemies_to_damage.append(enemy)
        
        for enemy in enemies_to_damage:
            enemy.enemy_receive_damage()

        # if self.attack_type == "melee":
            # Player is damaged by contact
            # self.player_sprite.receive_damage(self.damage)
        # elif self.attack_type == "ranged":
            # Player is damaged if projectile hits him
