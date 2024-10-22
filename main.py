# Base code from: https://api.arcade.academy/en/latest/examples/sprite_move_keyboard.html#sprite-move-keyboard
import arcade
import pymunk
import pyglet
from world import World
from player import Player
from enemy import Enemy

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "Game"

MOVEMENT_SPEED = 200
ENEMY_SPAWN_INTERVAL = 5

COLOR = arcade.color.AMAZON


class Game(arcade.Window):
    def __init__(self, width, height, title):
        # Call the parent class initializer
        super().__init__(width, height, title)

        self.background = arcade.load_texture("grass.jfif")

        self.physics_engine = None

        # Keeps track of enemy spawns
        self.enemy_list = arcade.SpriteList()
        self.time_since_last_spawn = 0
        self.spawn_time = ENEMY_SPAWN_INTERVAL

        self.world = World(COLOR)
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.scene = arcade.Scene()
        self.wall_list = arcade.SpriteList()

    def setup(self):
        self.world.setup()
        """ Set up the game and initialize the variables. """

        self.scene.add_sprite_list("enemy_back")
        self.scene.add_sprite_list("player_back")
        self.scene.add_sprite_list("enemy_mid_b")
        self.scene.add_sprite_list("enemy_mid_f")
        self.scene.add_sprite_list("player_fore")
        self.scene.add_sprite_list("enemy_fore")
        self.scene.add_sprite_list("test_hbs")

        wall = arcade.Sprite("wall.png", SPRITE_SCALING, center_x=SCREEN_WIDTH / 2, center_y=SCREEN_HEIGHT / 2 + 250,
                             hit_box_algorithm=None)
        self.wall_list.append(wall)
        self.scene.add_sprite_list_after("wall", "enemy_mid_b", False, self.wall_list)

        # Set up the player
        self.player_sprite = Player(5, 5, SPRITE_SCALING, SCREEN_WIDTH, SCREEN_HEIGHT)

        self.physics_engine = arcade.PymunkPhysicsEngine()
        self.physics_engine.add_sprite(self.player_sprite, mass=1, moment=arcade.PymunkPhysicsEngine.MOMENT_INF, collision_type="player")
        self.physics_engine.add_sprite_list(self.wall_list, body_type=1)

    # TODO: Spawn enemies off screen

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()
        self.camera.use()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                            self.background)
        arcade.draw_lrwh_rectangle_textured(SCREEN_WIDTH / 2, 0,
                                            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                            self.background)

        # Draw the rooms.
        # For now, indoor rooms are just grey rectangles.
        # The background is already green, so there's no need to draw the outdoor rooms.
        for i in range(len(self.world.rooms)):
            for j in range(len(self.world.rooms[i])):
                room = self.world.rooms[i][j]
                if (room.indoor):
                    arcade.draw_rectangle_filled(room.x, room.y, room.size, room.size, arcade.color.BATTLESHIP_GREY)

        self.scene.draw()
        self.player_sprite.draw()

    def on_update(self, delta_time):
        """ Movement and game logic """

        self.physics_engine.step()

        # Move the player

        self.player_sprite.update()
        cam_loc = pyglet.math.Vec2(self.player_sprite.center_x - SCREEN_WIDTH / 2,
                                   self.player_sprite.center_y - SCREEN_HEIGHT / 2)
        self.camera.move(cam_loc)

        self.time_since_last_spawn += delta_time
        # If an enemy hasn't spawned in x amount of time, spawn another
        if self.time_since_last_spawn > self.spawn_time:
            # Create a new enemy to spawn
            enemy = Enemy(self.player_sprite, self.enemy_list)
            self.enemy_list.append(enemy)
            self.time_since_last_spawn = 0
            self.physics_engine.add_sprite(enemy, mass = 2, moment=arcade.PymunkPhysicsEngine.MOMENT_INF, collision_type="enemy")

        # TODO: Add code to spawn boss after time interval or after x amount of enemies killed

        # Update enemies
        self.enemy_list.update()

        # get the closest wall to the player
        p_wall = arcade.get_closest_sprite(self.player_sprite, self.wall_list)

        # Check if the players y-index is above or below the closest wall's y
        # Adds player.tex to the scene so we only disply the player's texture, not its hitbox
        if self.player_sprite.center_y - self.player_sprite.height / 2 < p_wall[0].center_y - p_wall[
            0].height / 2 and self.player_sprite.tex not in self.scene.get_sprite_list("player_fore"):
            self.scene.get_sprite_list("player_fore").append(self.player_sprite.tex)

            if self.player_sprite.tex in self.scene.get_sprite_list("player_back"):
                self.scene.get_sprite_list("player_back").remove(self.player_sprite.tex)

        elif self.player_sprite.center_y - self.player_sprite.height / 2 > p_wall[0].center_y - p_wall[
            0].height / 2 and self.player_sprite.tex not in self.scene.get_sprite_list("player_back"):
            self.scene.get_sprite_list("player_back").append(self.player_sprite.tex)

            if self.player_sprite.tex in self.scene.get_sprite_list("player_fore"):
                self.scene.get_sprite_list("player_fore").remove(self.player_sprite.tex)

        # Update enemies z-index:
        for enem in self.enemy_list:
            # get closest wall to enemy
            self.physics_engine.set_velocity(enem, (enem.change_x, enem.change_y))

            e_wall = arcade.get_closest_sprite(enem, self.wall_list)

            # find bottom point of sprites for later
            enem_bottom = enem.center_y - enem.height / 2
            e_wall_bottom = e_wall[0].center_y - e_wall[0].height / 2

            # Remove enem from scene sprite lists to avoid conflicts when appending later
            # Uses enem.tex because then we are only displaying their texture not their hitbox
            if enem.tex in self.scene.get_sprite_list("enemy_back"):
                self.scene.get_sprite_list("enemy_back").remove(enem.tex)
            elif enem.tex in self.scene.get_sprite_list("enemy_mid_b"):
                self.scene.get_sprite_list("enemy_mid_b").remove(enem.tex)
            elif enem.tex in self.scene.get_sprite_list("enemy_mid_f"):
                self.scene.get_sprite_list("enemy_mid_f").remove(enem.tex)
            elif enem.tex in self.scene.get_sprite_list("enemy_fore"):
                self.scene.get_sprite_list("enemy_fore").remove(enem.tex)

            # Determine if enemy is above or below the closest wall and the player
            if enem_bottom < e_wall_bottom:
                if enem_bottom > self.player_sprite.center_y - self.player_sprite.height / 2:
                    self.scene.get_sprite_list("enemy_mid_f").append(enem.tex)
                else:
                    self.scene.get_sprite_list("enemy_fore").append(enem.tex)

            elif enem_bottom > e_wall_bottom:
                if enem_bottom < self.player_sprite.center_y - self.player_sprite.height / 2:
                    self.scene.get_sprite_list("enemy_mid_b").append(enem.tex)
                else:
                    self.scene.get_sprite_list("enemy_back").append(enem.tex)

            if enem not in self.scene.get_sprite_list("test_hbs"):
                self.scene.add_sprite("test_hbs", enem)

    def on_key_press(self, key, modifiers):

        """Called whenever a key is pressed. """

        # If the player presses a key, update the speed

        vec_vel = [0, 0]

        if key == arcade.key.UP or key == arcade.key.W:
            # self.player_sprite.change_y = MOVEMENT_SPEED
            vec_vel[1] = MOVEMENT_SPEED

        elif key == arcade.key.DOWN or key == arcade.key.S:
            # self.player_sprite.change_y = -MOVEMENT_SPEED
            vec_vel[1] = -MOVEMENT_SPEED

        elif key == arcade.key.LEFT or key == arcade.key.A:
            # self.player_sprite.change_x = -MOVEMENT_SPEED
            vec_vel[0] = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            # self.player_sprite.change_x = MOVEMENT_SPEED
            vec_vel[0] = MOVEMENT_SPEED

        self.physics_engine.set_velocity(self.player_sprite, vec_vel)
    def on_key_release(self, key, modifiers):

        """Called when the user releases a key. """

        # If a player releases a key, zero out the speed.

        # This doesn't work well if multiple keys are pressed.

        # Use 'better move by keyboard' example if you need to

        # handle this.

        # if key == arcade.key.UP or key == arcade.key.DOWN or key == arcade.key.W or key == arcade.key.S:
        #     self.player_sprite.change_y = 0
        #
        # elif key == arcade.key.LEFT or key == arcade.key.RIGHT or key == arcade.key.A or key == arcade.key.D:
        #
        #     self.player_sprite.change_x = 0

        if key == arcade.key.UP or key == arcade.key.DOWN or key == arcade.key.W or key == arcade.key.S or  key == arcade.key.LEFT or key == arcade.key.RIGHT or key == arcade.key.A or key == arcade.key.D:
            self.physics_engine.set_velocity(self.player_sprite, (0,0))


def main():
    """ Main function """
    window = Game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
