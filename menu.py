# Base code from: https://api.arcade.academy/en/latest/examples/view_screens_minimal.html
import arcade
import time

class MenuView(arcade.View):
    def __init__(self, start_game, show_guide, exit_game):
        super().__init__()
        self.start_game = start_game
        self.show_guide = show_guide
        self.exit_game = exit_game

        # Button positions and dimensions
        self.button_width = 200
        self.button_height = 50
        self.play_button_y = self.window.height / 2 + 50
        self.guide_button_y = self.window.height / 2 - 30
        self.exit_button_y = self.window.height / 2 - 110

    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)

    def draw_buttons(self):
        # Play button
        arcade.draw_text("Play", self.window.width / 2, self.play_button_y, arcade.color.DARK_RED, font_size=30, anchor_x="center", font_name="Kenney Future")

        # Guide button
        arcade.draw_text("Guide", self.window.width / 2, self.guide_button_y, arcade.color.DARK_RED, font_size=30, anchor_x="center", font_name="Kenney Future")

        # Exit button
        arcade.draw_text("Exit", self.window.width / 2, self.exit_button_y, arcade.color.DARK_RED, font_size=30, anchor_x="center", font_name="Kenney Future")

    def draw_background(self):
        # Load background texture
        background_texture = arcade.load_texture("mm.jpg")
        arcade.draw_lrwh_rectangle_textured(0, 0, self.window.width, self.window.height, background_texture)

    def on_draw(self):
        self.clear()

        # Call background function
        self.draw_background()

        # Draw the menu title
        arcade.draw_text("Main Menu", self.window.width / 2, self.window.height - 100, arcade.color.DARK_RED, font_size=50, anchor_x="center", font_name="Kenney Future")

        # Draw buttons
        self.draw_buttons()

    def on_mouse_press(self, x, y, button, modifiers):
        # Play button click
        if self.window.width / 2 - self.button_width / 2 < x < self.window.width / 2 + self.button_width / 2 and self.play_button_y - self.button_height / 2 < y < self.play_button_y + self.button_height / 2:
            time.sleep(1)
            self.start_game()

        # Guide button click
        elif self.window.width / 2 - self.button_width / 2 < x < self.window.width / 2 + self.button_width / 2 and self.guide_button_y - self.button_height / 2 < y < self.guide_button_y + self.button_height / 2:
            self.show_guide()

        # Exit button click
        elif self.window.width / 2 - self.button_width / 2 < x < self.window.width / 2 + self.button_width / 2 and self.exit_button_y - self.button_height / 2 < y < self.exit_button_y + self.button_height / 2:
            self.exit_game()

class GuideView(arcade.View):
    def __init__(self, go_back):
        super().__init__()
        self.go_back = go_back

    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)

    def draw_background(self):
        # Load background texture
        background_texture = arcade.load_texture("mm.jpg")
        arcade.draw_lrwh_rectangle_textured(0, 0, self.window.width, self.window.height, background_texture)

    def on_draw(self):
        self.clear()

        # Call background function
        self.draw_background()

        # Draw the menu title
        arcade.draw_text("Game Guide", self.window.width / 2, self.window.height - 100, arcade.color.DARK_RED, font_size=50, anchor_x="center", font_name="Kenney Future")

        # Write out guide for the game
        arcade.draw_text("In this game, you are a knight defending the kingdom.\n"
                         "Your task is to defeat the enemies and protect your land.\n"
                         "Use W, A, S, D to move and the arrow keys to attack.", self.window.width / 2, self.window.height / 2, arcade.color.BLACK, font_size=20, anchor_x="center", anchor_y="center", width=600, align="center")

        # Draw "Go Back" button
        arcade.draw_text("Go Back", self.window.width / 2, 100, arcade.color.DARK_RED, font_size=30, anchor_x="center", font_name="Kenney Future")

    def on_mouse_press(self, x, y, button, modifiers):
        # Go Back button click
        if self.window.width / 2 - 100 < x < self.window.width / 2 + 100 and 100 - 20 < y < 100 + 20:
            self.go_back()