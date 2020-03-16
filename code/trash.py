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

'''def confirmation_count(client_list):
    con_count = 0
    for client in client_list:
        if client.accepted is not None:
            con_count += 1
    return con_count
    # End confirmation_count'''

'''if message != 'you are the game ruler! decide how many rounds you will play':
            rounds = receive_message(client)'''

    '''if message == 'you are the game ruler! decide how many rounds you will play':
        rounds = -1
        while rounds <= 0:
            rounds = int(input(message))
            if rounds > 0:
                send_message(rounds, client)
            else:
                print('invalid number try again')
    else:
        print(message)'''

'''still_playing = input('do you still want to play the game? (yes or no)')
        if still_playing == 'yes':
            send_message(True, client)
            return True
        elif still_playing == 'no':
            send_message(False, client)
            return False
        else:
            print('invalid answer, exiting program')
            send_message(False, client)
            return False'''

'''accepted = False
    while not accepted:
        user_name = input('please enter your username')
        if user_name != '':
            send_message(str(user_name), client)
            response = receive_message(client)
            print(response)
            if response == 'username accepted':
                accepted = True
        else:
            print('invalid user name')

    accepted = False
    blocked = False
    while not accepted and not blocked:
        password = input('please enter your password')
        if password != '':
            send_message(str(password), client)
            response = receive_message(client)
            print(response)
            if response == 'password accepted':
                accepted = True
            elif response == 'DENIED!, too many tries were used':
                blocked = True
        else:
            send_message('invalid password', client)

    if accepted:
        print(receive_message(client))'''

'''chose_pass = False
    while not chose_pass:
        password = input('please enter your password')
        if password != '':
            send_message(str(password), client)
            chose_pass = True
        else:
            print('invalid password')
    print(receive_message(client))'''

'''chose_name = False
    while not chose_name:
        user_name = input('please enter your username')
        if user_name != '':
            send_message(str(user_name), client)
            response = receive_message(client)
            print(response)
            if response == 'username accepted':
                chose_name = True
        else:
            print('invalid user name')'''

'''print('please choose one of these actions:')
    command_list = ['log in', 'sign up']
    command = input(command_list)'''

'''chose_character = False
    character = ''
    character_list = receive_status(cubix_client)
    while not chose_character:
        print('choose your character:')
        character = input(character_list)
        if character in character_list:
            send_message(character, cubix_client)
            chose_character = True
        elif character == 'aa':
            send_message(character_list[0], cubix_client)
            chose_character = True
        else:
            print('invalid character name')
    print('character chosen: ' + str(character))'''

'''print('please choose one of these actions:')
    command_list = ['get status', 'play game']
    command = input(command_list)'''

'''while tries > 0 and not password_accepted:
        password = receive_message(client)
        if verify_password(user_hash, user_salt, password):
            send_message('password accepted', client)
            password_accepted = True
        else:
            tries -= 1
            if tries > 0:
                send_message('that the wrong password!', client)
            else:
                send_message('DENIED!, too many tries were used', client)'''

