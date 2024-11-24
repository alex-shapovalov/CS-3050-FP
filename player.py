import arcade
import pyglet
import math
import time
import enemy

PLAYER_PADDING = 150
UPDATES_PER_FRAME = 5
WALL_WIDTH = 79

FACING_RIGHT = 0
FACING_LEFT = 1

HEALING_FACTOR = 10

def load_texture_pair(filename):
        """ Load a texture pair, with the second being a mirror image """
        return [
            arcade.load_texture(filename),
            arcade.load_texture(filename, flipped_horizontally=True)
        ]

class Player(arcade.Sprite):
    """ Class which handles enemy logic, movement, and damage """
    def __init__(self, health, damage, sprite_scaling, world, screen_width, screen_height):
        super().__init__(
            scale=sprite_scaling
        )

        self.health: int = health
        self.damage: int = damage
        self.score = 0
        self.center_x = screen_width / 2
        self.center_y = screen_height / 2
        self.original_texture = arcade.load_texture("sprites/player_walk/player.png")
        self.width = self.original_texture.width/2
        self.height = self.original_texture.height

        hitbox = []
        self.hitbox_width = self.width/3
        self.hitbox_height = self.height/6
        num_points = 20
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
        self.world = world
        self.room = self.world.find_room(pyglet.math.Vec2(self.center_x,self.center_y))
        self.idle_texture_pair = load_texture_pair(f"sprites/player_walk/player.png")
        self.walking_texture_pair = load_texture_pair(f"sprites/player_walk/player.png")
        self.damaged_texture = arcade.load_texture_pair("sprites/player_walk/player_damaged.png")
        self.axe = arcade.Sprite(scale=sprite_scaling, hit_box_algorithm=None)
        self.axe_texture = load_texture_pair("sprites/misc/axe.png")
        self.axe.texture = self.axe_texture[self.facing]
        self.axe.position = self.position

        self.attack_curr_texture = 0
        self.attack_animation = []
        for i in range(3):
            filename = f'sprites/player_attack/player_attack_{i+1}.png'
            texture = load_texture_pair(filename)
            self.attack_animation.append(texture)

        self.walk_curr_texture = 0
        self.walking_animation = []
        for i in range(4):
            filename = f'sprites/player_walk/player_walk_{i+1}.png'
            texture = load_texture_pair(filename)
            self.walking_animation.append(texture)


    def update_velocity(self, vel):
        """ Keeps velocity to a manageable value """
        if vel[0] != -1:
            self.velocity[0] = vel[0]
        if vel[1] != -1:
            self.velocity[1] = vel[1]

        return self.velocity

    def on_update(self, delta_time):
        """ Continually updating the player instance """
        self.axe.visible = True

        room = self.world.find_room(pyglet.math.Vec2(self.center_x,self.center_y))
        if room != self.room:
            self.room = room

        if self.damaged and time.time() - self.damaged_time > 0.2:
            self.damaged = False

        if self.is_attacking:
            # So the animation looks smoother, make axe invisible when the user attacks.
            self.axe.visible = False

            # attack animation
            self.attack_curr_texture += delta_time * 20
            if self.attack_curr_texture >= len(self.attack_animation):
                self.attack_curr_texture = 0
                self.is_attacking = False
            self.texture = self.attack_animation[int(self.attack_curr_texture)][self.facing]
        else:
            # If the user moves in the other direction, flip the player and axe sprites to face that direction. 
            self.axe.texture = self.axe_texture[self.facing]
            if self.change_x == 0 and self.change_y == 0 and not self.damaged:
                # idle sprite
                self.texture = self.idle_texture_pair[self.facing]
            elif self.damaged:
                # damaged texture
                self.texture = self.damaged_texture[self.facing]
            else:
                # change the direction the player is facing depending on the movement
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

                # walking animation that loops as long as player is moving and not being damaged
                self.walk_curr_texture += delta_time*10
                if self.walk_curr_texture >= len(self.walking_animation):
                    self.walk_curr_texture = 0
                    self.is_attacking = False
                self.texture = self.walking_animation[int(self.walk_curr_texture)][self.facing]

    def player_receive_damage(self, amount):
        """ Receive damage from enemy, includes invincibility frames """
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
        """ Inflict damage onto enemy if its in range """
        for enemy in enemy_list:
            if enemy.target_type == 3:
                # Re-calculate distance to ensure player can always hit enemy in range
                enemy.calculate_distance()
                if enemy.distance <= PLAYER_PADDING:
                    return enemy.enemy_receive_damage()
                
    def heal_player(self):
        """ Heal player the amount of the healing factor """
        if self.health + HEALING_FACTOR > 100:
            self.health = 100
        else:
            self.health += HEALING_FACTOR
