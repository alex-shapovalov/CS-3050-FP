import arcade

class Player(arcade.Sprite):
    """ Player Class """

    def __init__(self, health, damage, sprite_scaling, screen_width, screen_height):
        """Initialize player"""

        # initialize player
        super().__init__(
            filename="char_hit_box.png",
            scale=sprite_scaling,
            hit_box_algorithm='Simple'
        )


        # following values are subject to change
        self.health: int = damage
        self.damage: int = health
        self.center_x = screen_width / 2
        self.center_y = screen_height / 2

        self.tex = arcade.Sprite("player.png", scale=sprite_scaling)

        self.width = self.tex.width
        self.height = self.tex.height/3


        self.screen_width: int = screen_width
        self.screen_height: int = screen_height


    def update(self):
        """ Move the player """

        self.center_x += self.change_x
        self.center_y += self.change_y

        self.tex.center_x = self.center_x
        self.tex.center_y = self.center_y + self.tex.height/2
