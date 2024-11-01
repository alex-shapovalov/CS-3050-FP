# Base code from: https://api.arcade.academy/en/latest/examples/sprite_move_keyboard.html#sprite-move-keyboard
import math

import arcade
import pymunk
import pyglet
from world import World
from player import Player
from enemy import Enemy
from menu import MenuView, GuideView, EscView

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "Game"

MOVEMENT_SPEED = 350
ENEMY_SPAWN_INTERVAL = 5
SPRITE_SCALING = 0.5
PLAYER_HEALTH = 100
PLAYER_DAMAGE = 50

COLOR = arcade.color.AMAZON

class Game(arcade.View):
    def __init__(self):
        # Call the parent class initializer
        super().__init__()

        self.background = arcade.load_texture("grass.jfif")

        self.physics_engine = None
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.title = SCREEN_TITLE

        # Keeps track of enemy spawns
        self.enemy_list = arcade.SpriteList()
        self.time_since_last_spawn = 0
        self.spawn_time = ENEMY_SPAWN_INTERVAL

        # Keeps track of world
        self.world = World(COLOR)
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.scene = arcade.Scene()
        self.wall_list = arcade.SpriteList()

    def cleanup(self):
        self.enemy_list = None
        self.player = None
        self.wall_list = None
        self.scene = None
        self.world = None
        self.camera = None

    def setup(self):
        # Setting up the game itself
        self.world.setup()

        # Setting up wall interactions

        self.scene.add_sprite_list("enemy_back")
        self.scene.add_sprite_list("player_back")
        self.scene.add_sprite_list("enemy_mid_b")
        self.scene.add_sprite_list("enemy_mid_f")
        self.scene.add_sprite_list("player_fore")
        self.scene.add_sprite_list("enemy_fore")

        wall = arcade.Sprite("wall.png", SPRITE_SCALING, center_x=SCREEN_WIDTH / 2, center_y=SCREEN_HEIGHT / 2 + 250, hit_box_algorithm=None)
        wall_hb = [[-wall.width, -wall.height], [wall.width, -wall.height], [wall.width, -wall.height/2], [-wall.width, -wall.height/2]]

        wall.set_hit_box(wall_hb)
        self.wall_list.append(wall)
        self.scene.add_sprite_list_after("wall", "enemy_mid_b", False, self.wall_list)

        # Set up the player
        self.player = Player(PLAYER_HEALTH, PLAYER_DAMAGE, SPRITE_SCALING, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.player.center_x = SCREEN_WIDTH / 2
        self.player.center_y = SCREEN_HEIGHT / 2

        self.scene.add_sprite("player_fore", self.player)

        self.physics_engine = arcade.PymunkPhysicsEngine()
        self.physics_engine.add_sprite(self.player, mass=10, moment=arcade.PymunkPhysicsEngine.MOMENT_INF, collision_type="player")
        self.physics_engine.add_sprite_list(self.wall_list, body_type=1, collision_type="wall")

    def on_draw(self):
        # Render the screen
        self.clear()
        self.camera.use()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, self.background)
        arcade.draw_lrwh_rectangle_textured(SCREEN_WIDTH / 2, 0, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, self.background)

        # Draw the rooms. For now, indoor rooms are just grey rectangles. The background is already green, so there's no need to draw the outdoor rooms.
        for i in range(len(self.world.rooms)):
            for j in range(len(self.world.rooms[i])):
                room = self.world.rooms[i][j]
                if (room.indoor):
                    arcade.draw_rectangle_filled(room.x, room.y, room.size, room.size, arcade.color.BATTLESHIP_GREY)

        self.player.draw()
        self.scene.draw()

        self.player.draw_hit_box((1,0,0))
        for i in self.enemy_list:
            i.draw_hit_box((1,0,0))

        for i in self.wall_list:
            i.draw_hit_box((1,0,0))

        if self.player.damaged:
            if self.player.health <= 0:
                # Close 'Game' window
                menu = MenuView(start_game, show_guide, exit_game, SCREEN_WIDTH, SCREEN_HEIGHT)
                arcade.get_window().show_view(menu)


    def on_update(self, delta_time):
        """ Movement and game logic """

        self.time_since_last_spawn += delta_time
        # If an enemy hasn't spawned in x amount of time, spawn another
        if self.time_since_last_spawn > self.spawn_time:
            # Create a new enemy to spawn
            enemy = Enemy(self.player, PLAYER_DAMAGE, self.enemy_list, self.wall_list, SPRITE_SCALING, SCREEN_WIDTH, SCREEN_HEIGHT)
            self.enemy_list.append(enemy)
            self.time_since_last_spawn = 0
            self.physics_engine.add_sprite(enemy, mass = 1,  moment=arcade.PymunkPhysicsEngine.MOMENT_INF, collision_type="enemy")
            self.scene.add_sprite("enemy_fore", enemy)

        # TODO: Add code to spawn boss after time interval or after x amount of enemies killed

        # Update enemies
        self.enemy_list.update()

        # Get the closest wall to the player
        p_wall = arcade.get_closest_sprite(self.player, self.wall_list)

        # Check if the players y-index is above or below the closest wall's y
        if self.player.center_y - self.player.height / 2 < p_wall[0].center_y - p_wall[
            0].height / 2 and self.player not in self.scene.get_sprite_list("player_fore"):
            self.scene.get_sprite_list("player_fore").append(self.player)

            if self.player in self.scene.get_sprite_list("player_back"):
                self.scene.get_sprite_list("player_back").remove(self.player)
            if self.player in self.scene.get_sprite_list("player_back"):
                self.scene.get_sprite_list("player_back").remove(self.player)

        elif self.player.center_y - self.player.height / 2 > p_wall[0].center_y - p_wall[
            0].height / 2 and self.player not in self.scene.get_sprite_list("player_back"):
            self.scene.get_sprite_list("player_back").append(self.player)
        elif self.player.center_y - self.player.height / 2 > p_wall[0].center_y - p_wall[
            0].height / 2 and self.player not in self.scene.get_sprite_list("player_back"):
            self.scene.get_sprite_list("player_back").append(self.player)

            if self.player in self.scene.get_sprite_list("player_fore"):
                self.scene.get_sprite_list("player_fore").remove(self.player)
            if self.player in self.scene.get_sprite_list("player_fore"):
                self.scene.get_sprite_list("player_fore").remove(self.player)

        # Update enemies z-index:
        for enemy in self.enemy_list:
            # get closest wall to enemy
            self.physics_engine.set_velocity(enemy, (enemy.change_x, enemy.change_y))

            e_wall = arcade.get_closest_sprite(enemy, self.wall_list)

            # find bottom point of sprites for later
            enem_bottom = enemy.center_y - enemy.height / 2
            e_wall_bottom = e_wall[0].center_y - e_wall[0].height / 2

            # Remove enem from scene sprite lists to avoid conflicts when appending later
            if enemy in self.scene.get_sprite_list("enemy_back"):
                self.scene.get_sprite_list("enemy_back").remove(enemy)
            elif enemy in self.scene.get_sprite_list("enemy_mid_b"):
                self.scene.get_sprite_list("enemy_mid_b").remove(enemy)
            elif enemy in self.scene.get_sprite_list("enemy_mid_f"):
                self.scene.get_sprite_list("enemy_mid_f").remove(enemy)
            elif enemy in self.scene.get_sprite_list("enemy_fore"):
                self.scene.get_sprite_list("enemy_fore").remove(enemy)

            # Determine if enemy is above or below the closest wall and the player
            if enem_bottom < e_wall_bottom:
                if enem_bottom > self.player.center_y - self.player.height / 2:
                    self.scene.get_sprite_list("enemy_mid_f").append(enemy)
                else:
                    self.scene.get_sprite_list("enemy_fore").append(enemy)

            elif enem_bottom > e_wall_bottom:
                if enem_bottom < self.player.center_y - self.player.height / 2:
                    self.scene.get_sprite_list("enemy_mid_b").append(enemy)
                else:
                    self.scene.get_sprite_list("enemy_back").append(enemy)

        # Move the player
        self.player.update()
        cam_loc = pyglet.math.Vec2(self.player.center_x - SCREEN_WIDTH / 2,
                                   self.player.center_y - SCREEN_HEIGHT / 2)
        self.camera.move(cam_loc)

        self.physics_engine.step()


    def on_key_press(self, key, modifiers):
        # If the player presses a key, update the speed

        vec_vel = [-1, -1]
        if key == arcade.key.ESCAPE:
            pause_view = EscView(self, go_back_to_menu)
            self.window.show_view(pause_view)

        if key == arcade.key.UP or key == arcade.key.W:
            vec_vel[1] = MOVEMENT_SPEED

        elif key == arcade.key.DOWN or key == arcade.key.S:
            vec_vel[1] = -MOVEMENT_SPEED

        if key == arcade.key.LEFT or key == arcade.key.A:
            vec_vel[0] = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            vec_vel[0] = MOVEMENT_SPEED

        if vec_vel[0] != -1 or vec_vel[1] != -1:
            updated_vel = self.player.update_velocity(vec_vel)
            self.physics_engine.set_velocity(self.player, updated_vel)

    def on_key_release(self, key, modifiers):

        """Called when the user releases a key. """

        # If a player releases a key, zero out the speed.

        # This doesn't work well if multiple keys are pressed.

        # Use 'better move by keyboard' example if you need to

        # handle this.

        if key == arcade.key.UP or key == arcade.key.DOWN or key == arcade.key.W or key == arcade.key.S or  key == arcade.key.LEFT or key == arcade.key.RIGHT or key == arcade.key.A or key == arcade.key.D:
            updated_vel = self.player.update_velocity([0,0])
            self.physics_engine.set_velocity(self.player, updated_vel)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        self.player.is_attacking = True
        self.player.player_give_damage(enemy_list=self.enemy_list)

def start_game():
    # Create 'Game' window
    game_view = Game()
    game_view.setup()
    arcade.get_window().show_view(game_view)

def show_guide():
    # Show the guide view with and go back button
    guide_view = GuideView(go_back_to_menu)
    arcade.get_window().show_view(guide_view)

def exit_game():
    # Close the game
    arcade.close_window()

def go_back_to_menu():
    # Go back to main menu
    menu_view = MenuView(start_game, show_guide, exit_game, SCREEN_WIDTH, SCREEN_HEIGHT)
    arcade.get_window().show_view(menu_view)

def main():
    # Create 'Main Menu' window
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Main Menu")

    # Call MenuView from menu.py with a callback method to start the game when user presses play
    menu_view = MenuView(start_game, show_guide, exit_game, SCREEN_WIDTH, SCREEN_HEIGHT)
    window.show_view(menu_view)
    arcade.run()

if __name__ == "__main__":
    main()