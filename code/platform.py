from world_objects import WorldObject

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Constants
SPRITE_FOLDER_ROUTE = '../sprites/'

# Constants for WorldObject class
IMAGE_NAME = 'block'
COLORKEY = RED
START_VX = 0
START_VY = 0
SIZE_X = 100
SIZE_Y = 100
GRAVITY = False


class Block(WorldObject):  # A platform class

    def __init__(self, x, y, object_id):
        super().__init__(IMAGE_NAME, COLORKEY, x, y, SIZE_X, SIZE_Y, START_VX, START_VY, GRAVITY, object_id)
        # End __init__
