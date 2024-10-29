import arcade
import time
import enemy

PLAYER_PADDING = 150
UPDATES_PER_FRAME = 5

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
        self.damage = damage
        self.health: int = health
        self.center_x: int = 50
        self.center_y: int = 50
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.damaged = False
        self.damaged_time = 0
        self.original_texture = arcade.load_texture("player.png")
        self.damaged_texture = arcade.load_texture("player_damaged.png")
        
        self.is_attacking = False
        self.delta_time = 0

        self.idle_texture_pair = load_texture_pair(f"player.png")

        self.walking_texture_pair = load_texture_pair(f"player.png")

        self.curr_texture = 0
        self.attack_animation = []
        for i in range(3):
            filename = f'player_anim_frames/player-f{i+1}.png'
            texture = load_texture_pair(filename)
            self.attack_animation.append(texture)


    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.damaged and time.time() - self.damaged_time > 0.2:
            self.damaged = False

        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.idle_texture_pair[0]
        else:
            self.texture = self.walking_texture_pair[0]

        if self.is_attacking:
            self.curr_texture += 0.5
            if self.curr_texture >= len(self.attack_animation):
                self.curr_texture = 0
                self.is_attacking = False
            self.texture = self.attack_animation[int(self.curr_texture)][0] # change direction 
            
        
        
    # def update_animation(self, delta_time: float = 1 / 60):

    #     # attack animation
    #     if self.is_attacking:
    #         self.curr_texture += 0.25
    #         print(int(self.curr_texture))
    #         if self.curr_texture == 3:
    #             self.curr_texture = 0
                
    #         self.texture = self.attack_animation[int(self.curr_texture)][0] # change direction 
            
    #     self.is_attacking = False
        
        
    def player_receive_damage(self, amount):
        # Invincibility frames
        if time.time() - self.damaged_time >= 1.5:
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
