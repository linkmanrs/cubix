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
PLAYER_SPEED = 5.0
PLAYER_JUMP_POWER = 10.0

# Constants for WorldObject class
COLORKEY = RED
START_VX = 0
START_VY = 0
SIZE_X = 104
SIZE_Y = 100
GRAVITY = True

# Constants for cuby
MAX_HEALTH = 5
DEFAULT_POWER = 'punch'
POWER_COOLDOWN = 45


class Player(WorldObject):  # Player class

    def __init__(self, x, y, object_id, character, user_name):
        super().__init__(character + '.png', COLORKEY, x, y, SIZE_X, SIZE_Y, START_VX, START_VY, GRAVITY, object_id)
        self.object_id = object_id
        self.user_name = user_name
        self.__max_health = MAX_HEALTH
        self.health = self.__max_health
        self.character = character
        self.power = DEFAULT_POWER
        self.max_cooldown = POWER_COOLDOWN
        self.cooldown = 0
        self.can_move = True
        self.can_move_cooldown = 0
        self.pressed_buttons = []  # A list of all the buttons the player pressed and are still pressed
        # End __init__

    def check_death_zone(self):  # kills the player if he fell from the screen
        if self.y >= WINDOWS_HEIGHT:
            self.health = 0
        # End check_death_zone

    def move_left(self):  # Makes the player move left
        self.update_vx(-PLAYER_SPEED)
        # End move_left

    def move_right(self):  # Makes the player move right
        self.update_vx(PLAYER_SPEED)
        # End move_right

    def stop_moving_x(self):  # Makes the player stop moving on the x axis
        self.update_vx(0)
        # End stop_moving

    def jump(self):  # Makes the player jump
        if not self.is_moving_y():
            self.update_vy(-PLAYER_JUMP_POWER)
        # End jump
