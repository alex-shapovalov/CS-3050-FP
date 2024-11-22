import arcade
import os


class MenuView(arcade.View):
    """ Class that creates the Main menu view with Start, Guide, Exit, and Reset highscore options """
    def __init__(self, start_game, show_guide, exit_game, width, height):
        super().__init__()
        self.start_game = start_game
        self.show_guide = show_guide
        self.exit_game = exit_game

        self.width = width
        self.height = height

        # Button positions and dimensions
        self.button_width = 200
        self.button_height = 50
        self.play_button_y = self.window.height / 2 + 50
        self.guide_button_y = self.window.height / 2 - 30
        self.exit_button_y = self.window.height / 2 - 110
        self.highscore_button_y = self.window.height / 2 - 350

    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)
        arcade.set_viewport(0, self.width, 0, self.height)

    def draw_buttons(self):
        # Play button
        arcade.draw_text("Play", self.window.width / 2, self.play_button_y, arcade.color.DARK_RED, font_size=30, anchor_x="center", font_name="Kenney Future")

        # Guide button
        arcade.draw_text("Guide", self.window.width / 2, self.guide_button_y, arcade.color.DARK_RED, font_size=30, anchor_x="center", font_name="Kenney Future")

        # Exit button
        arcade.draw_text("Exit", self.window.width / 2, self.exit_button_y, arcade.color.DARK_RED, font_size=30, anchor_x="center", font_name="Kenney Future")

        # High score reset button
        arcade.draw_text("Reset highscore", self.window.width / 2, self.highscore_button_y, arcade.color.DARK_RED, font_size=30, anchor_x="center", font_name="Kenney Future")

    def draw_background(self):
        # Load background texture
        background_texture = arcade.load_texture("sprites/menu/mm.jpg")
        arcade.draw_lrwh_rectangle_textured(0, 0, self.window.width, self.window.height, background_texture)

    def on_draw(self):
        self.clear()

        # Call background function
        self.draw_background()

        # Draw the menu title
        arcade.draw_text("Haunted Castle", self.window.width / 2, self.window.height - 100, arcade.color.DARK_RED, font_size=50, anchor_x="center", font_name="Kenney Future")

        # Draw buttons
        self.draw_buttons()

    def on_mouse_press(self, x, y, button, modifiers):
        # Play button click
        if self.window.width / 2 - self.button_width / 2 < x < self.window.width / 2 + self.button_width / 2 and self.play_button_y - self.button_height / 2 < y < self.play_button_y + self.button_height / 2:
            self.start_game()

        # Guide button click
        elif self.window.width / 2 - self.button_width / 2 < x < self.window.width / 2 + self.button_width / 2 and self.guide_button_y - self.button_height / 2 < y < self.guide_button_y + self.button_height / 2:
            self.show_guide()

        # Exit button click
        elif self.window.width / 2 - self.button_width / 2 < x < self.window.width / 2 + self.button_width / 2 and self.exit_button_y - self.button_height / 2 < y < self.exit_button_y + self.button_height / 2:
            self.exit_game()

        # Highscore button click
        elif self.window.width / 2 - self.button_width / 2 < x < self.window.width / 2 + self.button_width / 2 and self.highscore_button_y - self.button_height / 2 < y < self.highscore_button_y + self.button_height / 2:
            os.remove("highscore.txt")

class GuideView(arcade.View):
    """ Class that creates the Guide view for information about the game """
    def __init__(self, go_back):
        super().__init__()
        self.go_back = go_back

    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)

    def draw_background(self):
        # Load background texture
        background_texture = arcade.load_texture("sprites/menu/mm.jpg")
        arcade.draw_lrwh_rectangle_textured(0, 0, self.window.width, self.window.height, background_texture)

    def on_draw(self):
        self.clear()

        # Call background function
        self.draw_background()

        # Draw the menu title
        arcade.draw_text("Game Guide", self.window.width / 2, self.window.height - 100, arcade.color.DARK_RED, font_size=50, anchor_x="center", font_name="Kenney Future")

        # Write out guide for the game
        arcade.draw_text("In this game, you must defend yourself against a horde of enemies. "
                         "Will you protect the land or just perish with the rest? "
                         "Use W, A, S, D to move and H to attack. ", self.window.width / 2, self.window.height / 2, arcade.color.BLACK, font_size=20, anchor_x="center", anchor_y="center", width=600, align="center")

        # Draw "Go Back" button
        arcade.draw_text("Go Back", self.window.width / 2, 100, arcade.color.DARK_RED, font_size=30, anchor_x="center", font_name="Kenney Future")

    def on_mouse_press(self, x, y, button, modifiers):
        # Go Back button click
        if self.window.width / 2 - 100 < x < self.window.width / 2 + 100 and 100 - 20 < y < 100 + 20:
            self.go_back()

class EscView(arcade.View):
    """ Class that creates view when user presses escape while in the game, can return to Main menu or Desktop """
    def __init__(self, game_view, go_to_menu):
        super().__init__()
        self.game_view = game_view
        self.go_to_menu = go_to_menu

    def on_draw(self):
        self.clear()
        # Keep the game view in the background
        self.game_view.on_draw()

        # Center the camera based on when the camera is, when first implementing this menu, it stayed at spawn...
        cam_x, cam_y = self.game_view.camera.position
        center_x = cam_x + self.window.width / 2
        center_y = cam_y + self.window.height / 2

        # Transparent overlay
        arcade.draw_rectangle_filled(center_x, center_y, self.window.width, self.window.height, arcade.color.BLACK + (200,))

        # Draw buttons
        arcade.draw_text("Pause Menu", center_x, center_y + 150, arcade.color.DARK_RED, font_size=40, anchor_x="center", font_name="Kenney Future")
        arcade.draw_text("Resume", center_x, center_y + 30, arcade.color.DARK_RED, font_size=30, anchor_x="center", font_name="Kenney Future")
        arcade.draw_text("Main Menu", center_x, center_y - 60, arcade.color.DARK_RED, font_size=30, anchor_x="center", font_name="Kenney Future")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.game_view)

    def on_mouse_press(self, x, y, button, modifiers):
        # Also center where the clickable area of the buttons will be...
        cam_x, cam_y = self.game_view.camera.position
        center_x = cam_x + self.window.width / 2
        center_y = cam_y + self.window.height / 2
        adjusted_x = x + cam_x
        adjusted_y = y + cam_y

        # Resume button clicks
        if center_x - 50 < adjusted_x < center_x + 50 and center_y + 15 < adjusted_y < center_y + 45:
            self.window.show_view(self.game_view)

        # Main menu button clicks
        elif center_x - 50 < adjusted_x < center_x + 50 and center_y - 75 < adjusted_y < center_y - 45:
            self.go_to_menu()

class DeathView(arcade.View):
    """ Class that creates menu on player death to allow for main menu return """
    def __init__(self, game_view, go_to_menu):
        super().__init__()
        self.game_view = game_view
        self.go_to_menu = go_to_menu

    def on_draw(self):
        self.clear()
        # Keep the game view in the background
        self.game_view.on_draw()

        # Center the camera based on when the camera is, when first implementing this menu, it stayed at spawn...
        cam_x, cam_y = self.game_view.camera.position
        center_x = cam_x + self.window.width / 2
        center_y = cam_y + self.window.height / 2

        # Transparent overlay
        arcade.draw_rectangle_filled(center_x, center_y, self.window.width, self.window.height, arcade.color.BLACK + (200,))

        # Draw buttons
        arcade.draw_text("You died...", center_x, center_y + 150, arcade.color.DARK_RED, font_size=40, anchor_x="center", font_name="Kenney Future")
        arcade.draw_text("Main Menu", center_x, center_y - 60, arcade.color.DARK_RED, font_size=30, anchor_x="center", font_name="Kenney Future")

    def on_mouse_press(self, x, y, button, modifiers):
        # Also center where the clickable area of the buttons will be...
        cam_x, cam_y = self.game_view.camera.position
        center_x = cam_x + self.window.width / 2
        center_y = cam_y + self.window.height / 2
        adjusted_x = x + cam_x
        adjusted_y = y + cam_y

        # Main menu button clicks
        if center_x - 50 < adjusted_x < center_x + 50 and center_y - 75 < adjusted_y < center_y - 45:
            self.go_to_menu()
