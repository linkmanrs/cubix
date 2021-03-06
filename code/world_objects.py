import pygame

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
GRAVITY_CONSTANT_DOWN = 15.0  # Gravity constant for when the object goes down or not moving
GRAVITY_CONSTANT_UP = 12.0  # Gravity constant for when the object goes up
FRICTION_CONSTANT_X = 1.0
T = 1 / 60  # Time constant (Uses 60 times in one second)


class WorldObject(object):  # Class for every physical object in the game

    def __init__(self, sprite_name, colorkey, x, y, size_x, size_y, vx, vy, gravity, object_id):
        super().__init__()
        self.object_id = object_id
        self.is_particle = False
        self.x = float(x)
        self.y = float(y)
        self.size_x = size_x
        self.size_y = size_y
        self.__vx = float(vx)
        self.__vy = float(vy)
        self.__ax = 0
        self.gravity = gravity
        if self.gravity:  # Applies gravity effect
            self.__ay = GRAVITY_CONSTANT_DOWN
        else:
            self.__ay = 0
        self.state = ''  # A variable for the state of the player (for the animation)
        self.facing_right = True  # Right = True
        self.rect = pygame.Rect(int(x), int(y), size_x, size_y)

        self.sprite_name = sprite_name
        self.colorkey = colorkey
        # End __init__

    def update_loc_x(self):  # Function for updating location on the x axis according to speed
        self.x += self.__vx
        if self.x + self.size_x > WINDOWS_WIDTH - 1:  # Prevent object from going off screen
            self.x = WINDOWS_WIDTH - self.size_x
            self.__vx = 0
        elif self.x < 0:
            self.x = 0
            self.__vx = 0
        # End update_loc_x

    def update_loc_y(self):  # Function for updating location on the y axis according to speed
        self.y += self.__vy
        # End update_loc_y

    def update_vx(self, vx):  # Function for updating speed
        self.__vx = vx
        # End update_vx

    def update_vy(self, vy):  # Function for updating speed
        self.__vy = vy
        # End update_vy

    def update_ax(self, ax):  # Function for updating acceleration
        self.__ax = ax
        # End update_ax

    def update_ay(self, ay):  # Function for updating acceleration
        self.__ay = ay
        if self.gravity:  # Applies gravity effect
            if self.get_v()[1] < 0:
                self.__ay += GRAVITY_CONSTANT_UP
            else:
                self.__ay += GRAVITY_CONSTANT_DOWN
        # End update_at

    def get_pos(self):  # Returns the position of the object
        return int(self.x), int(self.y)
        # End get_pos

    def get_v(self):  # Returns the speed of the object
        return self.__vx, self.__vy
        # End get_v

    def get_a(self):  # Returns the acceleration of the object
        return self.__ax, self.__ay
        # End get_a

    def correct_v(self):  # Function for correcting the speed according to acceleration
        if self.__vx > self.__ax:
            self.__vx -= float(FRICTION_CONSTANT_X * T)
        elif self.__vx < self.__ax:
            self.__vx += float(FRICTION_CONSTANT_X * T)
        self.__vy += float(self.__ay * T)
        # End correct_v

    def correct_a(self):  # Function for correcting the acceleration according to speed and gravity
        if self.gravity:  # Applies gravity effect
            if self.get_v()[1] < 0:
                self.__ay = GRAVITY_CONSTANT_UP
            else:
                self.__ay = GRAVITY_CONSTANT_DOWN
        # End correct_a

    def copy_object(self):  # copies and returns the given object
        new_object = WorldObject(self.sprite_name, self.colorkey, self.x, self.y, self.size_x,
                                 self.size_y,
                                 self.__vx, self.__vy,
                                 self.gravity, self.object_id)
        return new_object
        # End copy_object

    def sync_test_rect(self):  # Synchronizes the test rect with the x an y
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        # End sync_test_rect

    def is_moving_x(self):  # Returns true if the object is moving on the x axis
        return self.get_v()[0] != 0
        # End is_moving_x

    def is_moving_y(self):  # Returns true if the object is moving on the y axis
        return self.get_v()[1] != 0
        # End is_moving_y

    def check_facing(self):  # Check which side the player is facing
        movement = self.get_v()
        if movement[0] > 0:
            self.facing_right = True
        elif movement[0] < 0:
            self.facing_right = False
        # End check_facing

    def hard_fall(self):  # Makes the object fall not in a floaty way
        v = self.get_v()[1]
        if -1 <= v < 3:
            self.update_vy(3)
        # End hard_fall

    def prevent_overlap_x(self, sprite):  # function for x axis in prevent_overlap
        main_object = self.copy_object()
        main_object.sync_test_rect()
        other_object = sprite.copy_object()
        other_object.sync_test_rect()

        if main_object.__vx > 0:  # Moving with positive speed
            main_object.rect.x += 1
            if main_object.rect.colliderect(other_object.rect):
                return 0
            main_object.sync_test_rect()

            if other_object.__vx == 0:  # Colliding with a static object
                main_object.rect.x += main_object.__vx
                if main_object.rect.colliderect(other_object.rect):
                    main_object.rect.x -= main_object.__vx
                    return other_object.rect.x - (main_object.rect.x + main_object.size_x) - 1
                main_object.sync_test_rect()
            elif other_object.__vx < 0:  # colliding with an object that is moving towards the main object
                main_object.rect.x += main_object.__vx
                other_object.rect.x += other_object.__vx
                if main_object.rect.colliderect(other_object.rect):
                    main_object.rect.x -= main_object.__vx
                    other_object.rect.x -= other_object.__vx
                    if (other_object.rect.x - (main_object.rect.x + main_object.size_x)) % 2 == 0:
                        sprite.update_vx((other_object.rect.x - (main_object.rect.x + main_object.size_x)) * -1)
                        return (other_object.rect.x - (main_object.rect.x + main_object.size_x)) // 2 - 1
                    else:
                        sprite.update_vx((other_object.rect.x - (main_object.rect.x + main_object.size_x)) * -1)
                        return (other_object.rect.x - (main_object.rect.x + main_object.size_x)) // 2
                main_object.sync_test_rect()
                other_object.sync_test_rect()
            else:  # colliding with an object that is moving away from the main object
                main_object.rect.x += main_object.__vx
                other_object.rect.x += other_object.__vx
                if main_object.rect.colliderect(other_object.rect):
                    main_object.rect.x -= main_object.__vx
                    other_object.rect.x -= other_object.__vx
                    if other_object.rect.x > main_object.rect.x:
                        return other_object.rect.x - (main_object.rect.x + main_object.size_x) - 1
                    else:
                        sprite.update_vx(main_object.rect.x - (other_object.rect.x + other_object.size_x) - 1)
                        return self.__vx
                main_object.sync_test_rect()
                other_object.sync_test_rect()

        if main_object.__vx < 0:  # Moving with negative speed
            main_object.rect.x -= 1
            if main_object.rect.colliderect(other_object.rect):
                return 0
            main_object.sync_test_rect()

            if other_object.__vx == 0:  # Colliding with a static object
                main_object.rect.x += main_object.__vx
                if main_object.rect.colliderect(other_object.rect):
                    main_object.rect.x -= main_object.__vx
                    return (main_object.rect.x - (other_object.rect.x + other_object.size_x) + 1) * -1
                main_object.sync_test_rect()
            elif other_object.__vx > 0:  # colliding with an object that is moving towards the main object
                main_object.rect.x += main_object.__vx
                other_object.rect.x += other_object.__vx
                if main_object.rect.colliderect(other_object.rect):
                    main_object.rect.x -= main_object.__vx
                    other_object.rect.x -= other_object.__vx
                    if (main_object.rect.x - (other_object.rect.x + other_object.size_x)) % 2 == 0:
                        sprite.update_vx((main_object.rect.x - (other_object.rect.x + other_object.size_x)))
                        return ((main_object.rect.x - (other_object.rect.x + other_object.size_x)) // 2 + 1) * -1
                    else:
                        sprite.update_vx((main_object.rect.x - (other_object.rect.x + other_object.size_x)))
                        return ((main_object.rect.x - (other_object.rect.x + other_object.size_x)) // 2) * -1
                main_object.sync_test_rect()
                other_object.sync_test_rect()
            else:  # colliding with an object that is moving away from the main object
                main_object.rect.x += main_object.__vx
                other_object.rect.x += other_object.__vx
                if main_object.rect.colliderect(other_object.rect):
                    main_object.rect.x -= main_object.__vx
                    other_object.rect.x -= other_object.__vx
                    if other_object.rect.x < main_object.rect.x:
                        return (main_object.rect.x - (other_object.rect.x + other_object.size_x) - 1) * -1
                    else:
                        sprite.update_vx((other_object.rect.x - (main_object.rect.x + main_object.size_x) - 1) * -1)
                        return self.__vx
                main_object.sync_test_rect()
                other_object.sync_test_rect()

        return self.__vx
        # End prevent_overlap_x

    def prevent_overlap_y(self, sprite):  # function for y axis in prevent_overlap
        main_object = self.copy_object()
        main_object.sync_test_rect()
        other_object = sprite.copy_object()
        other_object.sync_test_rect()

        if main_object.__vy > 0:  # Moving with positive speed
            main_object.rect.y += 1
            if main_object.rect.colliderect(other_object.rect):
                return 0
            main_object.sync_test_rect()

            if other_object.__vy == 0:  # Colliding with a static object
                main_object.rect.y += main_object.__vy
                if main_object.rect.colliderect(other_object.rect):
                    main_object.rect.y -= main_object.__vy
                    return other_object.rect.y - (main_object.rect.y + main_object.size_y) - 1
                main_object.sync_test_rect()
            elif other_object.__vy < 0:  # colliding with an object that is moving towards the main object
                main_object.rect.y += main_object.__vy
                other_object.rect.y += other_object.__vy
                if main_object.rect.colliderect(other_object.rect):
                    main_object.rect.y -= main_object.__vy
                    other_object.rect.y -= other_object.__vy
                    if (other_object.rect.y - (main_object.rect.y + main_object.size_y)) % 2 == 0:
                        sprite.update_vy((other_object.rect.y - (main_object.rect.y + main_object.size_y)) * -1)
                        return (other_object.rect.y - (main_object.rect.y + main_object.size_y)) // 2 - 1
                    else:
                        sprite.update_vy((other_object.rect.y - (main_object.rect.y + main_object.size_y)) * -1)
                        return (other_object.rect.y - (main_object.rect.y + main_object.size_y)) // 2
                main_object.sync_test_rect()
                other_object.sync_test_rect()
            else:  # colliding with an object that is moving away from the main object
                main_object.rect.y += main_object.__vy
                other_object.rect.y += other_object.__vy
                if main_object.rect.colliderect(other_object.rect):
                    main_object.rect.y -= main_object.__vy
                    other_object.rect.y -= other_object.__vy
                    if other_object.rect.y > main_object.rect.y:
                        return other_object.rect.y - (main_object.rect.y + main_object.size_y) - 1
                    else:
                        sprite.update_vy(main_object.rect.y - (other_object.rect.y + other_object.size_y) - 1)
                        return self.__vy
                main_object.sync_test_rect()
                other_object.sync_test_rect()

        if main_object.__vy < 0:  # Moving with negative speed
            main_object.rect.y -= 1
            if main_object.rect.colliderect(other_object.rect):
                return 0
            main_object.sync_test_rect()

            if other_object.__vy == 0:  # Colliding with a static object
                main_object.rect.y += main_object.__vy
                if main_object.rect.colliderect(other_object.rect):
                    main_object.rect.y -= main_object.__vy
                    return (main_object.rect.y - (other_object.rect.y + other_object.size_y) + 1) * -1
                main_object.sync_test_rect()
            elif other_object.__vy > 0:  # colliding with an object that is moving towards the main object
                main_object.rect.y += main_object.__vy
                other_object.rect.y += other_object.__vy
                if main_object.rect.colliderect(other_object.rect):
                    main_object.rect.y -= main_object.__vy
                    other_object.rect.y -= other_object.__vy
                    if (main_object.rect.y - (other_object.rect.y + other_object.size_y)) % 2 == 0:
                        sprite.update_vy((main_object.rect.y - (other_object.rect.y + other_object.size_y)))
                        return ((main_object.rect.y - (other_object.rect.y + other_object.size_y)) // 2 + 1) * -1
                    else:
                        sprite.update_vy((main_object.rect.y - (other_object.rect.y + other_object.size_y)))
                        return ((main_object.rect.y - (other_object.rect.y + other_object.size_y)) // 2) * -1
                main_object.sync_test_rect()
                other_object.sync_test_rect()
            else:  # colliding with an object that is moving away from the main object
                main_object.rect.y += main_object.__vy
                other_object.rect.y += other_object.__vy
                if main_object.rect.colliderect(other_object.rect):
                    main_object.rect.y -= main_object.__vy
                    other_object.rect.y -= other_object.__vy
                    if other_object.rect.y < main_object.rect.y:
                        return (main_object.rect.y - (other_object.rect.y + other_object.size_y) - 1) * -1
                    else:
                        sprite.update_vy((other_object.rect.y - (main_object.rect.y + main_object.size_y) - 1) * -1)
                        return self.__vy
                main_object.sync_test_rect()
                other_object.sync_test_rect()

        return self.__vy
        # End prevent_overlap_y
