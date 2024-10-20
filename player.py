import arcade

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
        self.health: int = damage
        self.damage: int = health
        self.center_x: int = 50
        self.center_y: int = 50

        self.screen_width: int = screen_width
        self.screen_height: int = screen_height


    def update(self):
        """ Move the player """

        self.center_x += self.change_x

        self.center_y += self.change_y