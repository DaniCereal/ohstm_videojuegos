import arcade

from constants import RIGHT_FACING, LEFT_FACING


class Character(arcade.Sprite):

    def __init__(self):

        super().__init__()

        self.facing_direction = RIGHT_FACING
        self.cur_texture = 0