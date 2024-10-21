# Base code from: https://api.arcade.academy/en/latest/examples/sprite_move_keyboard.html#sprite-move-keyboard
import arcade
import pyglet
from world import World
from player import Player
from enemy import Enemy
from menu import MenuView, GuideView

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "Game"
MOVEMENT_SPEED = 5
ENEMY_SPAWN_INTERVAL = 5
SPRITE_SCALING = 0.5

COLOR = arcade.color.AMAZON


class Game(arcade.Window):
    def __init__(self, width, height, title):
        # Call the parent class initializer
        super().__init__(width, height, title)

        self.background = arcade.load_texture("grass.jfif")

        # Keeps track of enemy spawns
        self.enemy_list = arcade.SpriteList()
        self.time_since_last_spawn = 0
        self.spawn_time = ENEMY_SPAWN_INTERVAL

        # Keeps track of world
        self.world = World(COLOR)
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.scene = arcade.Scene()
        self.wall_list = arcade.SpriteList()

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

        wall = arcade.Sprite("wall.png", SPRITE_SCALING, center_x=SCREEN_WIDTH / 2, center_y = SCREEN_HEIGHT / 2 + 30, hit_box_algorithm=None)
        self.wall_list.append(wall)
        self.scene.add_sprite_list_after("wall", "enemy_mid_b", False, self.wall_list)

        # Set up the player
        self.player_sprite = Player(5, 5, SPRITE_SCALING, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = SCREEN_HEIGHT / 2
        # self.player_list.append(self.player_sprite)

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

        self.scene.draw()

    def on_update(self, delta_time):
        # Move the player and keep the camera centered
        self.player_sprite.update()
        cam_loc = pyglet.math.Vec2(self.player_sprite.center_x - SCREEN_WIDTH / 2, self.player_sprite.center_y - SCREEN_HEIGHT / 2)
        self.camera.move(cam_loc)

        self.enemy_list.update()
        self.time_since_last_spawn += delta_time
        # If an enemy hasn't spawned in x amount of time, spawn another
        if self.time_since_last_spawn > self.spawn_time:
            # Create a new enemy to spawn
            enemy = Enemy(self.player_sprite, self.enemy_list, SPRITE_SCALING, SCREEN_WIDTH, SCREEN_HEIGHT)
            self.enemy_list.append(enemy)
            self.time_since_last_spawn = 0

        # TODO: Add code to spawn boss after time interval or after x amount of enemies killed

        # Update enemies
        self.enemy_list.update()

        # Get the closest wall to the player
        p_wall = arcade.get_closest_sprite(self.player_sprite, self.wall_list)

        # Check if the players y-index is above or below the closest wall's y
        if self.player_sprite.center_y - self.player_sprite.height / 2 < p_wall[0].center_y - p_wall[
            0].height / 2 and self.player_sprite not in self.scene.get_sprite_list("player_fore"):
            self.scene.get_sprite_list("player_fore").append(self.player_sprite)

            if self.player_sprite in self.scene.get_sprite_list("player_back"):
                self.scene.get_sprite_list("player_back").remove(self.player_sprite)

        elif self.player_sprite.center_y - self.player_sprite.height / 2 > p_wall[0].center_y - p_wall[
            0].height / 2 and self.player_sprite not in self.scene.get_sprite_list("player_back"):
            self.scene.get_sprite_list("player_back").append(self.player_sprite)

            if self.player_sprite in self.scene.get_sprite_list("player_fore"):
                self.scene.get_sprite_list("player_fore").remove(self.player_sprite)

        # Update enemies z-index:
        for enemy in self.enemy_list:
            # Get closest wall to the enemy
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
                if enem_bottom > self.player_sprite.center_y - self.player_sprite.height / 2:
                    self.scene.get_sprite_list("enemy_mid_f").append(enemy)
                else:
                    self.scene.get_sprite_list("enemy_fore").append(enemy)

            elif enem_bottom > e_wall_bottom:
                if enem_bottom < self.player_sprite.center_y - self.player_sprite.height / 2:
                    self.scene.get_sprite_list("enemy_mid_b").append(enemy)
                else:
                    self.scene.get_sprite_list("enemy_back").append(enemy)

    def on_key_press(self, key, modifiers):
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
        if key == arcade.key.UP or key == arcade.key.DOWN or key == arcade.key.W or key == arcade.key.S:
            self.player_sprite.change_y = 0

        elif key == arcade.key.LEFT or key == arcade.key.RIGHT or key == arcade.key.A or key == arcade.key.D:
            self.player_sprite.change_x = 0

def start_game():
    # Close 'Main Menu' window
    arcade.close_window()

    # Create 'Game' window
    window = Game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()

def show_guide():
    # Show the guide view with and go back button
    guide_view = GuideView(go_back_to_menu)
    arcade.get_window().show_view(guide_view)

def exit_game():
    # Close the game
    arcade.close_window()

def go_back_to_menu():
    # Go back to main menu
    menu_view = MenuView(start_game, show_guide, exit_game)
    arcade.get_window().show_view(menu_view)

def main():
    # Create 'Main Menu' window
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Main Menu")

    # Call MenuView from menu.py with a callback method to start the game when user presses play
    menu_view = MenuView(start_game, show_guide, exit_game)
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()