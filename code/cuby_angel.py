from particle_object import Particle

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Constants
WINDOWS_WIDTH = 1100
WINDOWS_HEIGHT = 700
SPRITE_FOLDER_ROUTE = '../sprites/'

# Constants for WorldObject class
COLORKEY = RED
START_VX = 0
START_VY = -2
SIZE_X = 291
SIZE_Y = 154
GRAVITY = False


class PlayerGhost(Particle):  # Players angel ghost particle class

    def __init__(self, x, y, object_id, character):
        super().__init__(character + '_angel.png', COLORKEY, x, y, SIZE_X, SIZE_Y, START_VX, START_VY, GRAVITY, object_id)
        self.character = character
        # End __init__
