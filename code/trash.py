def load_character():  # create a character object and draws it
    player_image = pygame.image.load(SPRITE_FOLDER_ROUTE + 'cuby.png').convert()
    player_image.set_colorkey(RED)
    screen.blit(player_image, [0, 0])
    # End load_character


def draw_line():  # Draw lines
    pygame.draw.line(screen, BLACK, [260, 360], [460, 360], 4)
    pygame.display.flip()
    # End draw_line


def circle_line():  # Exercise circle line
    start_point = [350, 250]

    for i in range(100):
        end_point_x = 350 * (math.sin(i) + 1)
        end_point_y = 250 * (math.cos(i) + 1)
        end_point = [end_point_x, end_point_y]
        pygame.draw.line(screen, BLACK, start_point, end_point, 4)
    pygame.display.flip()
    # End circle_line


def draw_ball():  # Draw ball
    radius = 15
    ball_x_pos = 0
    ball_y_pos = 0
    pygame.draw.circle(screen, BLACK, [ball_x_pos, ball_y_pos], radius)
    # End draw_ball


'''def move_ball(ball_x_pos, ball_y_pos, radius):  # update ball's position
    # Ball position variables
    x_positive = True
    y_positive = True
    if x_positive:
        if ball_x_pos < 700:
            ball_x_pos += 1
        else:
            x_positive = False
            ball_x_pos -= 1
    else:
        if ball_x_pos > 0:
            ball_x_pos -= 1
        else:
            x_positive = True
            ball_x_pos += 1

    if y_positive:
        if ball_y_pos < 500:
            ball_y_pos += 1
        else:
            y_positive = False
            ball_y_pos -= 1
    else:
        if ball_y_pos > 0:
            ball_y_pos -= 1
        else:
            y_positive = True
            ball_y_pos += 1

    pygame.draw.circle(screen, BLACK, [ball_x_pos, ball_y_pos], radius)
    # End move_ball'''


def correct_v(object_list):  # corrects the speeds of all the objects in the list
    for Object in object_list:
        Object.correct_v()
    # End correct_v


def update_loc_objects(object_list):  # Updates the locations of all the object s in the list
    for Object in object_list:
        Object.update_loc()
    # End update_loc_objects


def update_loc_particles(particle_list):  # Updates the locations of all the particles in the list
    for particle in particle_list:
        particle.update_loc()
    # End update_loc_particles


def check_delete_ghosts(particle_list):  # Deletes the ghosts that should be deleted
    for particle in particle_list:
        particle.check_delete_ghost()
    # End check_delete_ghosts


def paint_particles(particle_list):  # paints all the particles in the list on the screen
    for particle in particle_list:
        screen.blit(particle.visual.image, particle.get_pos())
    # End paint_particle


code = msgpack.packb([1, 2, 3], use_bin_type=True)

print(msgpack.unpackb(code, use_list=True, raw=False))


def check_delete_ghost(self):  # Deletes the ghost if its off screen
    if self.y + self.size_y <= 0:
        self.kill()
        print('dead for good')

    # End check_delete_ghost

    def check_facing(self):  # Check which side the player is facing
        movement = self.get_v()
        if movement[0] > 0:
            self.facing_right = True
        elif movement[0] < 0:
            self.facing_right = False
        # End check_facing


def correct_facing(self):  # Function for correcting the side that the player is looking
    if not self.facing_right:
        if self.rect_facing_right:
            self.visual.image = pygame.transform.flip(self.visual.image, True, False)
            self.rect_facing_right = False
    elif self.facing_right:
        if not self.rect_facing_right:
            self.visual.image = pygame.transform.flip(self.visual.image, True, False)
            self.rect_facing_right = True
    # End correct_facing


def paint_objects(screen, object_list):  # paints all the objects in the list on the screen
    for Object in object_list:
        screen.blit(Object.visual.image, Object.get_pos())
    # End paint_objects


def main_game(screen, clock):  # Main game
    # id variable
    object_id = 0

    # Status list that will be sent to the client
    status_list = []

    # Lists of the game objects
    object_list = []  # [0]
    particle_list = []  # [1]
    block_list = []  # [2]
    player_list = []  # [3]
    list_of_lists = [object_list, particle_list, block_list, player_list]

    # Create player and platform
    player = Player(0, 0, object_id)
    object_id += 1
    player_list.append(player)
    object_id = floor(block_list, object_id, status_list)

    # Main loop
    finish = False
    while not finish:
        if pygame.key.get_focused():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    finish = True
                elif event.type == pygame.KEYDOWN:
                    player.control_movement(player.input(event))
                elif event.type == pygame.KEYUP:
                    player.control_stop_movement(player.input(event))

        # Paints background
        screen.fill(WHITE)

        # Main game
        object_id = update_players(player_list, list_of_lists, object_id, status_list)
        update_particles(particle_list, status_list)

        # Layers
        paint_objects(screen, particle_list)
        paint_objects(screen, player_list)
        paint_objects(screen, object_list)
        paint_objects(screen, block_list)

        # Refresh the screen
        pygame.display.flip()

        # Clock tick
        clock.tick(REFRESH_RATE)

        # End of main loop

    pygame.quit()
    # End main_game


# screen = create_screen(WINDOWS_WIDTH, WINDOWS_HEIGHT)
# starting_screen(screen)
# play_theme()
# main_game(screen, clock)

'''code = client_socket.recv(1024)

    event_list = msgpack.unpackb(code, use_list=True, raw=False)'''

'''for event in event_list:
        if event.type == pygame.QUIT:
            finish = True
        elif event.type == pygame.KEYDOWN:
            player.control_movement(player.input(event))
        elif event.type == pygame.KEYUP:
            player.control_stop_movement(player.input(event))'''


def starting_screen(screen):  # Makes a starting screen
    screen.fill(WHITE)
    font = pygame.font.Font('freesansbold.ttf', 32)
    start_message = font.render('Press any key to start', True, BLACK)
    screen.blit(start_message, [200, 300])
    pygame.display.flip()
    start = False
    while not start:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                start = True
    # End starting_screen

player.correct_facing()

(client_socket, client_address) = collect_clients(cubix_server)

def paint_lists(screen, status_list):  # Calls paint_objects for every list in list_of_lists
    # Layers
    paint_objects(screen, status_list[1])
    paint_objects(screen, status_list[3])
    paint_objects(screen, status_list[0])
    paint_objects(screen, status_list[2])
    # End paint_lists

def player_input(event):  # Returns the key that was pushed down
    return event.key
    # End input