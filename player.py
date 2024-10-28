import arcade
import time
import enemy

PLAYER_PADDING = 150

class Player(arcade.Sprite):
    """ Player Class """

    def __init__(self, health, damage, sprite_scaling, screen_width, screen_height):
        """Initialize player"""

        # initialize player
        super().__init__(
            filename="player.png",
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


    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.damaged and time.time() - self.damaged_time > 0.2:
            self.damaged = False

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
