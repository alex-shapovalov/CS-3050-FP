# Base code from: https://api.arcade.academy/en/latest/examples/sprite_move_keyboard.html#sprite-move-keyboard
import arcade
import pyglet
from world import World
from creatures import Creature


SPRITE_SCALING = 0.5

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "Move Sprite with Keyboard Example"

MOVEMENT_SPEED = 5

COLOR = arcade.color.AMAZON

class Game(arcade.Window):
    def __init__(self, width, height, title):
     # Call the parent class initializer
        super().__init__(width, height, title)

        self.background = arcade.load_texture("grass.jfif")

        self.world = World(COLOR)
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    def setup(self):
        self.world.setup()
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = Creature("player.png", 0.5)
        self.player_sprite.center_x = SCREEN_WIDTH/2
        self.player_sprite.center_y = SCREEN_HEIGHT/2
        self.player_list.append(self.player_sprite)

    #TODO: Spawn enemies off screen

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()
        self.camera.use()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH/2, SCREEN_HEIGHT/2,
                                            self.background)
        arcade.draw_lrwh_rectangle_textured(SCREEN_WIDTH / 2, 0,
                                            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                            self.background)

        # Draw the rooms.
        # For now, indoor rooms are just grey rectangles.
        # The background is already green, so there's no need to draw the outdoor rooms.
        for i in range(len(self.world.rooms)):
            for j in range(len(self.world.rooms[i])):
                room = self.world.rooms[i][j];
                if (room.indoor):
                    arcade.draw_rectangle_filled(room.x, room.y, room.size, room.size, arcade.color.BATTLESHIP_GREY)

        # Draw all the sprites.
        self.player_list.draw()


    def on_update(self, delta_time):
        """ Movement and game logic """

        # Move the player

        self.player_list.update()
        cam_loc = pyglet.math.Vec2(self.player_sprite.center_x - SCREEN_WIDTH/2, self.player_sprite.center_y - SCREEN_HEIGHT/2)
        self.camera.move(cam_loc)

    def on_key_press(self, key, modifiers):

        """Called whenever a key is pressed. """

        # If the player presses a key, update the speed

        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = MOVEMENT_SPEED

        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = -MOVEMENT_SPEED

        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -MOVEMENT_SPEED

        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = MOVEMENT_SPEED


    def on_key_release(self, key, modifiers):

        """Called when the user releases a key. """

        # If a player releases a key, zero out the speed.

        # This doesn't work well if multiple keys are pressed.

        # Use 'better move by keyboard' example if you need to

        # handle this.

        if key == arcade.key.UP or key == arcade.key.DOWN or key == arcade.key.W or key == arcade.key.S:

            self.player_sprite.change_y = 0

        elif key == arcade.key.LEFT or key == arcade.key.RIGHT or key == arcade.key.A or key == arcade.key.D:

            self.player_sprite.change_x = 0
            
    #TODO: Camera follows player movement


def main():
    """ Main function """
    window = Game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()