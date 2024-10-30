import arcade
import pymunk
import math

class Player(arcade.Sprite):
    """ Player Class """

    def __init__(self, health, damage, sprite_scaling, screen_width, screen_height):
        """Initialize player"""

        # initialize player
        super().__init__(
            filename="player.png",
            scale=sprite_scaling,
        )


        # following values are subject to change
        self.health: int = damage
        self.damage: int = health
        self.center_x = screen_width / 2
        self.center_y = screen_height / 2

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


    # def update(self):
    #     """ Move the player """

        # self.center_x += self.change_x
        # self.center_y += self.change_y
        #
        # self.tex.center_x = self.center_x
        # self.tex.center_y = self.center_y + self.tex.height/2


    def update_velocity(self, vel):
        if vel[0] != -1:
            self.velocity[0] = vel[0]
        if vel[1] != -1:
            self.velocity[1] = vel[1]

        return self.velocity