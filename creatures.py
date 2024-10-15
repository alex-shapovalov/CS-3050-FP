import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class Creature(arcade.Sprite):
    """ Player Class """

    def update(self):

        """ Move the player """

        # Move player.

        # Remove these lines if physics engine is moving player.

        self.center_x += self.change_x

        self.center_y += self.change_y