from world_objects import WorldObject

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
IMAGE_NAME = 'punch.png'
COLORKEY = RED
START_VX = 0
START_VY = 0
SIZE_X = 50
SIZE_Y = 50
GRAVITY = False

# Constants for punch
POWER_PUSH_X = 8
POWER_PUSH_Y = 5


class Punch(WorldObject):  # Punch class

    def __init__(self, x, y, object_id, user_id):
        super().__init__(IMAGE_NAME, COLORKEY, x, y, SIZE_X, SIZE_Y, START_VX, START_VY, GRAVITY, object_id)
        self.facing_right = True  # Right = True
        self.rect_facing_right = True  # Right = True
        self.user_id = user_id
        self.show_num = 0  # Indicates if the punch is needed to be shown
        self.can_hurt = True  # Indicates if the punch can hurt
        self.power_push_x = POWER_PUSH_X
        self.power_push_y = POWER_PUSH_Y
        # End __init__
