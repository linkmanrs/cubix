from particle_object import Particle

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Constants
SPRITE_FOLDER_ROUTE = '../sprites/'

# Constants for WorldObject class
COLORKEY = RED
START_VX = 0
START_VY = 0
SIZE_X = 50
SIZE_Y = 50
GRAVITY = True


class Star(Particle):  # Star particle that falls from the sky for beauty

    def __init__(self, x, y, object_id):
        super().__init__('star', COLORKEY, x, y, SIZE_X, SIZE_Y, START_VX, START_VY, GRAVITY, object_id)
        # End __init__
