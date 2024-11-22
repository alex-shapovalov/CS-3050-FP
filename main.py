import arcade
import pymunk
import arcade.key
import pyglet
import time
import os
from world import World
from player import Player
from enemy import Enemy
from menu import MenuView, GuideView, EscView, DeathView

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "Game"
FLOOR_TILE_SIZE = 80
MOVEMENT_SPEED = 350
ENEMY_SPAWN_INTERVAL = 5
SPRITE_SCALING = 0.5
PLAYER_HEALTH = 100
PLAYER_DAMAGE = 50
ENEMY_HEALTH = 100
ENEMY_DAMAGE = 10
MAX_ENEMIES = 15
POTION_PADDING = 25
COLOR = arcade.color.AMAZON


class Game(arcade.View):
    """ Class which runs the entire game including menu switching, GUI, rendering, and enemy spawning """
    def __init__(self):
        super().__init__()

        # Base game vars
        self.player = None
        self.physics_engine = None
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.title = SCREEN_TITLE
        self.keys_pressed = set()
        self.last_attack_time = 0

        # Enemies vars
        self.enemy_list = arcade.SpriteList()
        self.time_since_last_spawn = 0
        self.spawn_time = ENEMY_SPAWN_INTERVAL
        self.spawn_boss = True

        # World vars
        self.world = World(COLOR)
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.scene = arcade.Scene()
        self.wall_cover_list = arcade.SpriteList()
        self.floor_list_indoor = arcade.SpriteList()
        self.floor_list_outdoor = arcade.SpriteList()

    def cleanup(self):
        """ Cleanup class on restart """
        self.enemy_list = None
        self.player = None
        self.physics_engine = None
        self.floor_list_indoor = None
        self.floor_list_outdoor = None
        self.wall_cover_list = None
        self.scene = None
        self.world = None
        self.camera = None

    def setup(self):
        """ Initialization class to setup the game """
        self.world.setup()

        # Set up floors
        self.scene.add_sprite_list("floor_list_indoor")
        self.scene.add_sprite_list("floor_list_outdoor")

        # Setting up scene to handle correct layering of sprites
        self.scene.add_sprite_list("enemy_back")
        self.scene.add_sprite_list("player_back")
        self.scene.add_sprite_list("enemy_mid_b")
        self.scene.add_sprite_list("enemy_mid_f")
        self.scene.add_sprite_list("player_fore")
        self.scene.add_sprite_list("enemy_fore")

        # Moving lists into the scene
        self.scene.add_sprite_list_after("wall", "enemy_mid_b", True, self.world.wall_list)
        self.scene.add_sprite_list_after("wall_front", "enemy_fore", True, self.world.wall_front_list)
        self.scene.add_sprite_list_before("wall_back", "enemy_back", True, self.world.wall_back_list)
        self.scene.add_sprite_list_before("floor_list_indoor", "wall_back", True, self.world.floor_list_indoor)
        self.scene.add_sprite_list_after("floor_list_outdoor", "floor_list_indoor", True, self.world.floor_list_outdoor)
        self.scene.add_sprite_list_after("wall_cover_list", "wall_front", True, self.world.wall_cover_list)

        # Setting up the player
        self.player = Player(PLAYER_HEALTH, PLAYER_DAMAGE, SPRITE_SCALING, self.world, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.scene.add_sprite("player_fore", self.player)
        self.scene.add_sprite("player_fore", self.player.axe)

        # Setting up potions
        self.potion_list = arcade.SpriteList()

        # Player and wall filters
        player_filter = pymunk.ShapeFilter(categories=0b1000, mask=0b0111)
        wall_filter = pymunk.ShapeFilter(categories=0b0100, mask=0b1011)

        # Completing physics setup
        self.physics_engine = arcade.PymunkPhysicsEngine()
        self.physics_engine.add_sprite(self.player,
                                       mass=10,
                                       moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                       collision_type="player")
        self.physics_engine.add_sprite_list(self.world.wall_list, body_type=1, collision_type="wall")
        self.physics_engine.add_sprite_list(self.world.wall_front_list, body_type=1, collision_type="wall")
        self.physics_engine.add_sprite_list(self.world.wall_back_list, body_type=1, collision_type="wall")

        self.physics_engine.get_physics_object(self.player).shape.filter = player_filter
        for wall in self.world.wall_list:
            self.physics_engine.get_physics_object(wall).shape.filter = wall_filter
        for wall in self.world.wall_front_list:
            self.physics_engine.get_physics_object(wall).shape.filter = wall_filter
        for wall in self.world.wall_back_list:
            self.physics_engine.get_physics_object(wall).shape.filter = wall_filter

    def draw_health_bar(self):
        """ Draw the health bar for the player, always relative to the screen """
        bar_width = 400
        bar_height = 40
        rect_width = bar_width / 100

        # Get camera position to ensure consistent placement
        cam_x, cam_y = self.camera.position
        bar_x = cam_x + 20
        bar_y = cam_y + SCREEN_HEIGHT - 50

        # Draw 100 mini rectangles for health out of 100 (default health)
        for i in range(100):
            if i < self.player.health:
                color = arcade.color.RED
            else:
                color = arcade.color.BLACK
            x = bar_x + i * rect_width
            arcade.draw_rectangle_filled(x + rect_width / 2, bar_y, rect_width, bar_height, color, )

        arcade.draw_text(str(self.player.health) + " / 100",
                         bar_x + 200,
                         bar_y - 10,
                         arcade.color.WHITE,
                         font_size=20,
                         anchor_x="center",
                         font_name="Kenney Future")

    def draw_score(self):
        """ Draw the score and highscore of the user """
        cam_x, cam_y = self.camera.position
        score_x = cam_x + SCREEN_WIDTH - 150
        score_y = cam_y + SCREEN_HEIGHT - 50

        if os.path.exists("highscore.txt"):
            with open("highscore.txt", 'r') as file:
                highscore = file.readline()
                if highscore is None:
                    highscore = 0
                elif not highscore.isnumeric():
                    highscore = 0
        else:
            highscore = 0

        if self.player.score >= int(highscore):
            with open("highscore.txt", 'w') as file:
                file.write(str(self.player.score))

        arcade.draw_text("Score: " + str(self.player.score),
                         score_x,
                         score_y - 10,
                         arcade.color.WHITE,
                         font_size=20,
                         anchor_x="center",
                         font_name="Kenney Future")
        arcade.draw_text("Highscore: " + str(highscore),
                         score_x,
                         score_y - 50,
                         arcade.color.WHITE,
                         font_size=20,
                         anchor_x="center",
                         font_name="Kenney Future")

    def on_draw(self):
        """ Render the screen and screen elements """
        self.clear()
        self.camera.use()
        self.scene.draw()
        self.draw_health_bar()
        self.draw_score()

        for enemy in self.enemy_list:
            enemy.draw_hit_box()

        for enemy in self.enemy_list:
            enemy.draw_damage_texts()

        for potion in self.potion_list:
            potion.draw()

        if self.player.damaged:
            if self.player.health <= 0:
                # Player is dead, show the death view and write down high score
                death_view = DeathView(self, go_back_to_menu)
                self.window.show_view(death_view)
                file = open("highscore.txt", "w")
                file.write(str(self.player.score))
                file.close()

    def on_update(self, delta_time):
        """ Movement and game logic """
        self.time_since_last_spawn += delta_time
        # If an enemy hasn't spawned in x amount of time, spawn another
        if self.time_since_last_spawn > self.spawn_time and len(self.enemy_list) < MAX_ENEMIES:
            # If score is divisible by 20, spawn a boss (2x the size, 2x the damage, and 4x the health)
            if self.player.score % 20 == 0 and self.player.score != 0 and self.spawn_boss == True:
                enemy = Enemy(self.player, PLAYER_DAMAGE, self.enemy_list, self.world, SPRITE_SCALING * 2, SCREEN_WIDTH,
                              SCREEN_HEIGHT, ENEMY_HEALTH * 4, ENEMY_DAMAGE * 2)
                self.spawn_boss = False
            # Create a new enemy to spawn
            else:
                enemy = Enemy(self.player, PLAYER_DAMAGE, self.enemy_list, self.world, SPRITE_SCALING, SCREEN_WIDTH,
                              SCREEN_HEIGHT)
                self.spawn_boss = True
            self.enemy_list.append(enemy)
            self.time_since_last_spawn = 0

            if enemy.rand_num != 3:
                enemy_filter = pymunk.ShapeFilter(categories=0b0010, mask=0b1101)
                self.physics_engine.add_sprite(enemy,
                                               mass=1,
                                               moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                               collision_type="enemy")
                self.physics_engine.get_physics_object(enemy).shape.filter = enemy_filter
            else:
                ghost_filter = pymunk.ShapeFilter(categories=0b0001, mask=0b1010)
                self.physics_engine.add_sprite(enemy,
                                               mass=1,
                                               moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                               collision_type="ghost")
                self.physics_engine.get_physics_object(enemy).shape.filter = ghost_filter

            self.scene.add_sprite("enemy_fore", enemy)

        # Update enemies
        enemy: Enemy
        for enemy in self.enemy_list:
            enemy.update(delta_time)

        for enemy in self.enemy_list:
            enemy.update_damage_texts()

        # Get the closest wall to the player
        p_wall = arcade.get_closest_sprite(self.player, self.world.wall_list)

        # Check if the players y-index is above or below the closest wall's y
        if self.player.center_y - self.player.height / 2 < p_wall[0].center_y - p_wall[
            0].height / 2 and self.player not in self.scene.get_sprite_list("player_fore"):
            self.scene.get_sprite_list("player_fore").append(self.player)
            if self.player.axe not in self.scene.get_sprite_list("player_fore"):
                self.scene.get_sprite_list("player_fore").append(self.player.axe)

            if self.player in self.scene.get_sprite_list("player_back"):
                self.scene.get_sprite_list("player_back").remove(self.player)
            if self.player.axe in self.scene.get_sprite_list("player_back"):
                self.scene.get_sprite_list("player_back").remove(self.player.axe)

        elif self.player.center_y - self.player.height / 2 > p_wall[0].center_y - p_wall[
            0].height / 2 and self.player not in self.scene.get_sprite_list("player_back"):
            self.scene.get_sprite_list("player_back").append(self.player)
            if self.player.axe not in self.scene.get_sprite_list("player_back"):
                self.scene.get_sprite_list("player_back").append(self.player.axe)

            if self.player in self.scene.get_sprite_list("player_fore"):
                self.scene.get_sprite_list("player_fore").remove(self.player)
            if self.player.axe in self.scene.get_sprite_list("player_fore"):
                self.scene.get_sprite_list("player_fore").remove(self.player.axe)

        # Update enemies z-index:
        for enemy in self.enemy_list:
            # Get closest wall to enemy
            self.physics_engine.set_velocity(enemy, (enemy.change_x, enemy.change_y))

            e_wall = arcade.get_closest_sprite(enemy, self.world.wall_list)

            # Find bottom point of sprites for later
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
        self.player.on_update(delta_time)
        cam_loc = pyglet.math.Vec2(self.player.center_x - SCREEN_WIDTH / 2, self.player.center_y - SCREEN_HEIGHT / 2)

        self.camera.move(cam_loc)

        self.physics_engine.step()
        self.player.axe.position = self.player.position

        for enemy in self.enemy_list:
            if enemy.health <= 0:
                enemy.drop_potion()
                if enemy.spawn_potion:
                    potion = arcade.Sprite("Potion.png", scale=1)
                    potion.center_x = enemy.center_x
                    potion.center_y = enemy.center_y
                    self.potion_list.append(potion)

                enemy.kill()
                self.player.score += 1

        for potion in self.potion_list:
            if potion.center_x - POTION_PADDING <= self.player.center_x <= potion.center_x + POTION_PADDING:
                if potion.center_y - POTION_PADDING <= self.player.center_y <= potion.center_y + POTION_PADDING:
                    self.player.heal_player()
                    potion.kill()

    def on_key_press(self, key, modifiers):
        """ Controls key presses and input """
        # If the player presses a key, update the speed
        self.keys_pressed.add(key)

        # Check key combinations to determine direction
        self.update_movement()

        # Handle special key (ESC) to pause the game
        if key == arcade.key.ESCAPE:
            pause_view = EscView(self, go_back_to_menu)
            self.window.show_view(pause_view)
        if key == arcade.key.H and time.time() - self.last_attack_time > 0.8:
            self.last_attack_time = time.time()
            self.player.is_attacking = True
            self.player.player_give_damage(self.enemy_list)

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key """
        # Remove that key from our set to update movement
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

        # update movement
        self.update_movement()

    def update_movement(self):
        """ Function that will update users movement """
        vec_vel = [0, 0]

        # Key press checks
        if arcade.key.UP in self.keys_pressed or arcade.key.W in self.keys_pressed:
            vec_vel[1] = MOVEMENT_SPEED
        elif arcade.key.DOWN in self.keys_pressed or arcade.key.S in self.keys_pressed:
            vec_vel[1] = -MOVEMENT_SPEED

        if arcade.key.LEFT in self.keys_pressed or arcade.key.A in self.keys_pressed:
            vec_vel[0] = -MOVEMENT_SPEED
        elif arcade.key.RIGHT in self.keys_pressed or arcade.key.D in self.keys_pressed:
            vec_vel[0] = MOVEMENT_SPEED

        # Update velocity and physics engine
        updated_vel = self.player.update_velocity(vec_vel)
        self.physics_engine.set_velocity(self.player, updated_vel)

def start_game():
    """ Creates the Game window """
    game_view = Game()
    game_view.setup()
    arcade.get_window().show_view(game_view)

def show_guide():
    """ Shows the Guide window """
    guide_view = GuideView(go_back_to_menu)
    arcade.get_window().show_view(guide_view)

def exit_game():
    """ Exits the game """
    arcade.close_window()

def go_back_to_menu():
    """ Returns to Main menu """
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
