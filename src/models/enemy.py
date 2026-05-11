from models.character import Character
from constants import RIGHT_FACING, LEFT_FACING

class Enemy(Character):
    def __init__(self, name_folder, name_file):
        super().__init__(name_folder, name_file)

        self.should_update_walk = 0

    def update_animation(self, delta_time):
        # Figure out the direction the character is facing based on the
        # movement and previous direction.
        if self.change_x < 0 and self.facing_direction == RIGHT_FACING:
            self.facing_direction = LEFT_FACING
        elif self.change_x > 0 and self.facing_direction == LEFT_FACING:
            self.facing_direction = RIGHT_FACING

        # Handle idle animations
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.facing_direction]
            return

        # Handle walking
        if self.should_update_walk == 3:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][self.facing_direction]
            self.should_update_walk = 0
            return

        self.should_update_walk += 1


class RobotEnemy(Enemy):
    def __init__(self):
        super().__init__("robot", "robot")
        self.health = 100


class ZombieEnemy(Enemy):
    def __init__(self):
        super().__init__("zombie", "zombie")
        self.health = 50


