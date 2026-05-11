import arcade

from constants import RIGHT_FACING, LEFT_FACING


class Character(arcade.Sprite):

    def __init__(self, name_folder, name_file):
        super().__init__()

        self.facing_direction = RIGHT_FACING
        self.cur_texture = 0

        main_path = (
            f":resources:images/animated_characters/"
            f"{name_folder}/{name_file}"
        )

        idle_texture = arcade.load_texture(
            f"{main_path}_idle.png"
        )

        jump_texture = arcade.load_texture(
            f"{main_path}_jump.png"
        )

        fall_texture = arcade.load_texture(
            f"{main_path}_fall.png"
        )

        self.idle_texture_pair = (
            idle_texture,
            idle_texture.flip_left_right()
        )

        self.jump_texture_pair = (
            jump_texture,
            jump_texture.flip_left_right()
        )

        self.fall_texture_pair = (
            fall_texture,
            fall_texture.flip_left_right()
        )

        self.walk_textures = []

        for i in range(8):

            texture = arcade.load_texture(
                f"{main_path}_walk{i}.png"
            )

            self.walk_textures.append(
                (
                    texture,
                    texture.flip_left_right()
                )
            )

        self.climbing_textures = (
            arcade.load_texture(
                f"{main_path}_climb0.png"
            ),
            arcade.load_texture(
                f"{main_path}_climb1.png"
            )
        )

        self.texture = self.idle_texture_pair[0]