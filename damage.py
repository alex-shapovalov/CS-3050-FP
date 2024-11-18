import arcade
import time


class DamageText:
    """ Class that handles damage text popups on enemy hit """
    def __init__(self, x, y, damage, duration=1.0):
        self.x = x
        self.y = y
        self.damage = damage
        self.duration = duration
        self.start_time = time.time()

    def draw(self):
        """ Draw the damagee text """
        arcade.draw_text("-" + str(self.damage), self.x, self.y, arcade.color.RED, font_size=20, anchor_x="center")

    def update(self):
        """ Fades the damage text upwards """
        self.y += 2
        return time.time() - self.start_time < self.duration