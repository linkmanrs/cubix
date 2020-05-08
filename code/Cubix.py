__author__ = 'Roy'

import random
import time
import pygame
import threading
import socket
import msgpack
import sqlite3
import hashlib
import binascii
import os
from client_player import ClientPlayer
from cuby import Player
from cuby_angel import PlayerGhost
from platform import Block
from star_particle import Star
from power_punch import Punch
from global_var import GlobalVariable

# Constants
WINDOWS_WIDTH = 1100
WINDOWS_HEIGHT = 700
REFRESH_RATE = 60
MAXIMUM_CLIENTS = 2
MINIMUM_PLAYERS = 1
FINISHED_LOGGING = 4
SPRITE_FOLDER_ROUTE = '../sprites/'
MUSIC_AND_SOUNDTRACK_ROUTE = '../ost/'
MAIN_THEME_NAME = 'forsaken dreams by edgy.mpeg'
DATABASE_FOLDER_ROUTE = '../database/'
DATABASE_NAME = 'cubix_database.db'

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# maps
MAP0 = [[0, 600], [100, 600], [200, 600], [300, 600], [400, 600], [500, 600], [600, 600], [700, 600], [800, 600]]
MAP1 = [[0, 600], [100, 600], [200, 600], [300, 600], [400, 600], [500, 600], [600, 600], [700, 600], [800, 600], [900, 600], [1000, 600]]
MAP2 = [[300, 600], [400, 600], [500, 600], [600, 600], [700, 600], [0, 400], [1000, 400]]
MAP3 = [[0, 600], [100, 600], [200, 600], [300, 600], [400, 600], [500, 600], [600, 600], [700, 600], [800, 600], [900, 600], [1000, 600], [0, 400], [100, 400], [900, 400], [1000, 400], [400, 200], [500, 200], [600, 200]]
MAPS = [MAP0, MAP1, MAP2, MAP3]

# spawn points
SPAWN_POINT0 = [[0, 0], [150, 0], [300, 0], [450, 0]]
SPAWN_POINT1 = [[0, 0], [350, 0], [650, 0], [1000, 0]]
SPAWN_POINT2 = [[0, 0], [350, 0], [650, 0], [1000, 0]]
SPAWN_POINT3 = [[400, 0], [600, 0], [350, 200], [650, 200]]
SPAWN_POINTS = [SPAWN_POINT0, SPAWN_POINT1, SPAWN_POINT2, SPAWN_POINT3]


def main_physical_game(clock, client_list):  # Main physical game
    for client in client_list:
        event = receive_message(client.client_socket)
        send_status([], client)
    global_var = GlobalVariable()

    map_num = random.randint(0, len(MAPS) - 1)

    make_players(global_var, client_list, map_num)

    floor(global_var, map_num)

    # Main loop
    finish = False
    while not finish:
        for client in client_list:
            event = receive_event(client)
            manage_event(global_var, event, client, client_list)

        # Main game
        if global_var.star_cooldown == 20:
            create_star(global_var)
            global_var.star_cooldown = 0
        else:
            global_var.star_cooldown += 1

        manage_power(global_var)
        update_players(global_var)
        update_particles(global_var)

        # Clock tick
        clock.tick(REFRESH_RATE)
        for client in client_list:
            send_status(global_var.status_list, client)
        global_var.status_list.clear()

        if len(global_var.player_list) == MINIMUM_PLAYERS:  # Ends the game if all the players left
            finish = True
            for client in client_list:
                send_status([['quit']], client)
        # End of main loop
    return global_var.player_list[0]
    # End main_physical_game


def receive_event(client):  # receives the events from the client
    length = b""
    break_loop = False
    while not break_loop:
        current_byte = client.client_socket.recv(1)
        if current_byte == b"":
            raise socket.error()
        if current_byte == b"|":
            break_loop = True
        if not break_loop:
            length += current_byte
    event_bytes = client.client_socket.recv(int(length))
    event_tuple = msgpack.unpackb(event_bytes, use_list=True, raw=False)
    event = pygame.event.Event(*event_tuple)
    return event
    # End receive_event


def receive_message(client):  # receives the events from the client
    length = b""
    break_loop = False
    while not break_loop:
        current_byte = client.recv(1)
        if current_byte == b"":
            raise socket.error()
        if current_byte == b"|":
            break_loop = True
        if not break_loop:
            length += current_byte
    message_bytes = client.recv(int(length))
    message = msgpack.unpackb(message_bytes, use_list=True, raw=False)
    return message
    # End receive_event


def send_status(status_list, client):  # sends the status list to the client
    packed_status = msgpack.packb(status_list, use_bin_type=True)
    client.client_socket.send(str(len(packed_status)).encode() + b"|" + packed_status)
    # End send_status


def send_message(message, client):  # sends the status list to the client
    packed_message = msgpack.packb(message, use_bin_type=True)
    client.send(str(len(packed_message)).encode() + b"|" + packed_message)
    # End send_status


def new_status(status, sprite, global_var):  # creates a new status and adds it to the status list
    if status == 'new':
        new_status_list = ['new', sprite.sprite_name, sprite.colorkey, sprite.get_pos()[0], sprite.get_pos()[1],
                           sprite.object_id, sprite.is_particle, sprite.facing_right]
        global_var.status_list.append(new_status_list)
    elif status == 'update':
        new_status_list = ['update', sprite.object_id, sprite.get_pos()[0], sprite.get_pos()[1], sprite.facing_right,
                           sprite.state]
        global_var.status_list.append(new_status_list)
    elif status == 'dead':
        new_status_list = ['dead', sprite.object_id]
        global_var.status_list.append(new_status_list)
    # End new_status


def new_quit_status(global_var):  # Creates a new quit status for the clients
    new_status_list = ['quit']
    global_var.status_list.append(new_status_list)
    # End new_quit_status


def player_left(global_var, player, client, client_list):  # Making the player quit and killing his character
    if player is not None:
        death(player, global_var)
    send_status([['quit']], client)
    client_list.remove(client)
    client.client_socket.close()
    # End player_left


def make_players(global_var, client_list, spawn_num):  # Create players
    spawn = SPAWN_POINTS[spawn_num]
    i = 0
    for client in client_list:
        player = Player(spawn[i][0], spawn[i][1], global_var.object_id, client.chosen_character, client.user_name)
        client.add_player_id(global_var.object_id)
        global_var.object_id += 1
        new_status('new', player, global_var)
        global_var.player_list.append(player)
        i += 1
    # End make_players


def floor(global_var, map_num):  # Creates a floor with blocks
    game_map = MAPS[map_num]
    for coordinates in game_map:
        block = Block(coordinates[0], coordinates[1], global_var.object_id)
        global_var.object_id += 1
        new_status('new', block, global_var)
        global_var.block_list.append(block)
    # End floor


def manage_event(global_var, event, client, client_list):  # Manages the events that are received
    if len(global_var.player_list) != 0:
        for player in global_var.player_list:
            if player.object_id == client.player_id:
                if event.type == pygame.QUIT:
                    player_left(global_var, player, client, client_list)
                else:
                    manage_pressed_buttons(player, event, global_var)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        player_left(global_var, player, client, client_list)
            else:
                if event.type == pygame.QUIT:
                    player_left(global_var, None, client, client_list)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        player_left(global_var, None, client, client_list)
    else:
        if event.type == pygame.QUIT:
            player_left(global_var, None, client, client_list)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                player_left(global_var, None, client, client_list)
    # End manage_event


def manage_pressed_buttons(player, event, global_var):  # Manages the list of pressed buttons
    if event.type == pygame.KEYDOWN:
        player.pressed_buttons.append(event.key)
    if player.can_move:
        for key in player.pressed_buttons:
            control_movement(player, key, global_var)
    if event.type == pygame.KEYUP:
        if event.key in player.pressed_buttons:
            player.pressed_buttons.remove(event.key)
        if player.can_move:
            control_stop_movement(player, event.key)
    # End manage_pressed_buttons


def control_movement(player, player_input, global_var):  # Making the player move according to the input
    action = {
        pygame.K_a: player.move_left,
        pygame.K_LEFT: player.move_left,
        pygame.K_d: player.move_right,
        pygame.K_RIGHT: player.move_right,
        pygame.K_SPACE: create_power,
        pygame.K_UP: player.jump,
        pygame.K_w: player.jump,
    }
    if not action.get(player_input) is None:
        if action.get(player_input) is create_power:
            create_power(player, global_var)
        else:
            action.get(player_input)()
    # End control_movement


def control_stop_movement(player, player_input):  # Making the player stop moving according to the input
    action = {
        pygame.K_a: player.stop_moving_x,
        pygame.K_LEFT: player.stop_moving_x,
        pygame.K_d: player.stop_moving_x,
        pygame.K_RIGHT: player.stop_moving_x
    }
    if not action.get(player_input) is None:
        action.get(player_input)()
    # End control_stop_movement


def update_players(global_var):  # Function that contains all the necessary updates for the player list
    for player in global_var.player_list:
        manage_cooldown(player)
        pos = player.get_pos()
        player.check_death_zone()
        if check_alive(player):
            death(player, global_var)
        player.hard_fall()
        player.correct_a()
        player.correct_v()

        manage_collision(player, global_var)

        player.correct_state()
        player.check_facing()

        player.sync_test_rect()
        if pos != player.get_pos():
            new_status('update', player, global_var)
    # End update_player


def check_alive(player):  # Check if the player is alive and returns the answer
    return player.health <= 0
    # End check_alive


def death(player, global_var):  # Makes the player die and creates a ghost particle of the player
    print('zzz')
    pos = player.get_pos()
    ghost = PlayerGhost(pos[0] - 93, pos[1] - 53, global_var.object_id, player.character)
    global_var.object_id += 1
    if not player.facing_right:
        ghost.facing_right = False
    global_var.particle_list.append(ghost)
    new_status('new', ghost, global_var)
    kill_object(player, global_var.player_list, global_var)
    # End death


def manage_cooldown(player):  # Manages the cooldown parameter
    if not player.can_move:
        if player.can_move_cooldown >= 30:
            player.can_move = True
            player.can_move_cooldown = 0
        else:
            player.can_move_cooldown += 1
    if player.cooldown > 0:
        player.cooldown -= 1
    # End manage_cooldown


def manage_collision(player, global_var):  # Manages the collision protocol and updates the location
    for i in range(5):
        if i != 1 and i != 4:  # Only checks the lists that are needed to be checked
            if player.get_v()[0] > 0:
                for sprite in global_var.list_of_lists[i]:
                    if sprite is not player:
                        v = player.prevent_overlap_x(sprite)
                        if v < player.get_v()[0]:
                            player.update_vx(v)
            elif player.get_v()[0] < 0:
                for sprite in global_var.list_of_lists[i]:
                    if sprite is not player:
                        v = player.prevent_overlap_x(sprite)
                        if v > player.get_v()[0]:
                            player.update_vx(v)
    player.update_loc_x()

    for i in range(5):
        if i != 1 and i != 4:  # Only checks the lists that are needed to be checked
            if player.get_v()[1] > 0:
                for sprite in global_var.list_of_lists[i]:
                    if sprite is not player:
                        v = player.prevent_overlap_y(sprite)
                        if v < player.get_v()[1]:
                            player.update_vy(v)
            elif player.get_v()[1] < 0:
                for sprite in global_var.list_of_lists[i]:
                    if sprite is not player:
                        v = player.prevent_overlap_y(sprite)
                        if v > player.get_v()[1]:
                            player.update_vy(v)
    player.update_loc_y()
    # End manage_collision


def create_star(global_var):  # Creates a star particle to rain from the sky
    random_pos_x = random.randint(0, WINDOWS_WIDTH)
    star = Star(random_pos_x, -50, global_var.object_id)
    global_var.object_id += 1
    global_var.particle_list.append(star)
    new_status('new', star, global_var)
    # End create_star


def update_particles(global_var):  # Function that contains all the necessary updates for the particle list
    for particle in global_var.particle_list:
        pos = particle.get_pos()
        particle.correct_v()
        particle.update_loc()
        if pos != particle.get_pos():
            new_status('update', particle, global_var)
        if particle.get_v()[1] < 0:
            check_delete_ghost(particle, global_var)
        elif particle.get_v()[1] > 0:
            check_delete_star(particle, global_var)

    # End update_particles


def check_delete_ghost(ghost, global_var):  # Deletes the ghost if its off screen
    if ghost.y + ghost.size_y <= 0:
        kill_object(ghost, global_var.particle_list, global_var)
        print('dead for good')
    # End check_delete_ghost


def check_delete_star(star, global_var):  # # Deletes the star if its off screen
    if star.y >= WINDOWS_HEIGHT:
        kill_object(star, global_var.particle_list, global_var)
    # End check_delete_star


def kill_object(sprite, sprite_list, global_var):  # Removing the object from the corresponding
    sprite_list.remove(sprite)
    new_status('dead', sprite, global_var)
    # End kill_object


def create_power(player, global_var):  # Activates the players power
    power = {
        'punch': create_punch
    }
    if not power.get(player.power) is None:
        power.get(player.power)(player, global_var)
    # End use_power


def create_punch(player, global_var):  # Activates punch power
    if player.cooldown <= 0:
        if player.facing_right:
            punch = Punch(player.rect.x + player.size_x, player.rect.y + 27, global_var.object_id, player.object_id)
        else:
            punch = Punch(player.rect.x - 50, player.rect.y + 27, global_var.object_id, player.object_id)
            punch.facing_right = False
        global_var.object_id += 1
        global_var.power_list.append(punch)
        new_status('new', punch, global_var)
        player.cooldown = player.max_cooldown
    # End activate_punch


def manage_power(global_var):  # Manages the power list
    for power in global_var.power_list:
        if power.show_num <= 7:
            if power.can_hurt:
                for player in global_var.player_list:
                    if player.rect.colliderect(power.rect):  # punishing the hurt player
                        player.can_move = False
                        player.health -= 1
                        if power.facing_right:
                            player.update_vx(power.power_push_x)
                            player.update_vy(-power.power_push_y)
                        else:
                            player.update_vx(-power.power_push_x)
                            player.update_vy(-power.power_push_y)
                power.can_hurt = False
            pos = power.get_pos()
            for player in global_var.player_list:
                if player.object_id == power.user_id:
                    if player.facing_right is power.facing_right:  # Keeping the punch
                        # glued to the player unless he turns
                        if power.facing_right:
                            power.x = player.rect.x + player.size_x
                            power.y = player.rect.y + 27
                        else:
                            power.x = player.rect.x - 50
                            power.y = player.rect.y + 27
                    else:
                        power.show_num = 10
            if power.get_pos() != pos:
                new_status('update', power, global_var)
            power.show_num += 1
        else:
            kill_object(power, global_var.power_list, global_var)
    # End manage_power


def except_client(client, username_list, _, soc):
    cubix_database = sqlite3.connect(DATABASE_FOLDER_ROUTE + DATABASE_NAME)
    cubix_cursor = cubix_database.cursor()

    accepted, user_id = choose_command_at_enterence(cubix_cursor, soc, username_list)
    if accepted:
        playing = choose_command_after_logged(cubix_cursor, soc, user_id)
        client.user_id = user_id
        client.user_name = cubix_cursor.execute('SELECT username FROM users WHERE ID=?', [user_id]).fetchone()[0]
        client.playing = playing
        client.accepted = playing
    # End except_client


def choose_command_at_enterence(cursor, client, username_list):  # Let the user pick the action he wants to do
    command = receive_message(client)
    action = {
        'sign up': register_user,
        'log in': sign_in,
        'exit': False
    }
    if not action.get(command) is None:
        if action.get(command) is False:
            return False, None
        else:
            return action.get(command)(cursor, client, username_list)
    else:
        return False, None
    # End choose_action


def register_user(cubix_cursor, client, username_list):  # Registers a user to the database
    new_user_id = cubix_cursor.execute('SELECT max(ID) FROM users').fetchone()[0] + 1
    chose_name = False
    username = ''
    while not chose_name:
        username = receive_message(client)
        if username == 'exit':
            return False, None
        exist = False
        for name in username_list:  # Checks if the username already exists in the database
            if name[0] == username:
                exist = True
        if exist:
            send_message('username already exists, choose another', client)
        else:
            send_message('username accepted', client)
            chose_name = True
    password = receive_message(client)
    if password == 'exit':
        return False, None
    hash_db, salt = hash_password(password)
    data = [new_user_id, username, hash_db, salt]
    cubix_cursor.execute('INSERT INTO users VALUES(?,?,?,?,0,0)', data)
    return True, new_user_id
    # End register_user


def sign_in(cubix_cursor, client, username_list):  # lets the user try to sign in
    tries = 3
    username_accepted = False
    password_accepted = False
    username = ''
    while tries > 0 and (not password_accepted or not username_accepted):
        username = receive_message(client)
        if username == 'exit':
            return False, None
        password = receive_message(client)
        if password == 'exit':
            return False, None
        exist = False
        for name in username_list:  # Checks if the username already exists in the database
            if name[0] == username:
                exist = True
        if exist:
            username_accepted = True
            user_hash = cubix_cursor.execute('SELECT hash FROM users WHERE username=?', [username]).fetchone()[0]
            user_salt = cubix_cursor.execute('SELECT salt FROM users WHERE username=?', [username]).fetchone()[0]
            if verify_password(user_hash, user_salt, password):
                send_message('user accepted', client)
                password_accepted = True
            else:
                username_accepted = False
                tries -= 1
                if tries == 0:
                    send_message('DENIED!, too many tries were used', client)
                else:
                    send_message('username or password are incorrect', client)
        else:
            tries -= 1
            if tries == 0:
                send_message('DENIED!, too many tries were used', client)
            else:
                send_message('username or password are incorrect', client)

    user_id = None
    if password_accepted and username_accepted:
        user_id = cubix_cursor.execute('SELECT ID FROM users WHERE username=?', [username]).fetchone()[0]
    return password_accepted and username_accepted, user_id
    # End sign_in


def hash_password(password):  # hashing the password and creating a salt (returning both)
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    password_hash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    password_hash = binascii.hexlify(password_hash)
    password_hash = password_hash.decode('ascii')
    salt = salt.decode('ascii')
    return password_hash, salt
    # End hash_password


def verify_password(stored_password, salt, provided_password):  # checking if the given password is correct
    password_hash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000)
    password_hash = binascii.hexlify(password_hash).decode('ascii')
    return password_hash == stored_password
    # End verify_password


def choose_command_after_logged(cursor, client, user_id):  # Let the user pick the action he wants to do
    command = receive_message(client)
    action = {
        'get status': collect_status,
        'play game': True,
        'exit': False
    }
    if not action.get(command) is None:
        if action.get(command) is False:
            return False
        elif action.get(command) is True:
            return True
        else:
            return action.get(command)(user_id, cursor, client)
    else:
        return False
    # End choose_action


def collect_status(user_id, cubix_cursor, client):  # sends the status of the player
    numgames = cubix_cursor.execute('SELECT numgames FROM users WHERE ID=?', [user_id]).fetchone()[0]
    wins = cubix_cursor.execute('SELECT wins FROM users WHERE ID=?', [user_id]).fetchone()[0]
    status = 'you played {} games and won {} games'.format(numgames, wins)
    send_message(status, client)
    still_playing = receive_message(client)
    return still_playing
    # End send_status


def collect_clients(cubix_server, cubix_cursor):  # Collects between 2-4 clients to play the game
    client_list = []
    thread_list = []

    cubix_server.listen(4)
    client_id = 0
    confirmation_count = 0
    username_list = cubix_cursor.execute('SELECT username FROM users').fetchall()
    while confirmation_count < MAXIMUM_CLIENTS:
        (client_socket, client_address) = cubix_server.accept()
        new_client = ClientPlayer(client_id, client_socket, client_address)
        client_list.append(new_client)
        client_id += 1
        new_thread = threading.Thread(target=except_client,
                                      args=(new_client, username_list, cubix_cursor, client_socket))
        new_thread.start()
        thread_list.append(new_thread)
        confirmation_count += 1

    for thread in thread_list:
        thread.join()

    for client in client_list[:]:
        if not client.accepted:
            client_list.remove(client)
            client.client_socket.close()

    for client in client_list[:]:
        send_message('done', client.client_socket)

    num_rounds = 0
    if len(client_list) != 0:
        client_list[0].is_game_ruler = True  # Sets the first client as the game ruler

        num_rounds = choose_rounds(client_list)

        choose_character(client_list)

    return client_list, num_rounds
    # End collect_clients


def choose_rounds(client_list):  # Letting only the game ruler to choose how many rounds the players will play
    for client in client_list:
        if client.is_game_ruler:
            send_message('you are the game ruler! decide how many rounds you will play', client.client_socket)
        else:
            send_message('you are not the game ruler :( please wait for his decision', client.client_socket)

    num_rounds = 0
    while num_rounds == 0:
        for client in client_list[:]:
            message = receive_message(client.client_socket)
            if message == 'exit':
                client_list.remove(client)
                client.client_socket.close()
            elif message == 'exit ruler':  # If the game ruler quits there will be only one round
                client_list.remove(client)
                client.client_socket.close()
                num_rounds = 1
            elif message != 'waiting':
                num_rounds = message
            else:
                send_message('still waiting', client.client_socket)

    for client in client_list:
        if not client.is_game_ruler:
            send_message('done', client.client_socket)

    for client in client_list:
        if not client.is_game_ruler:
            send_message(num_rounds, client.client_socket)
    return num_rounds
    # End choose_rounds


def choose_character(client_list):  # A function for choosing a character
    character_list = ['cuby', 'sphery', 'triangly', 'penty']
    someone_choosing = False
    everyone_chose = False
    while not everyone_chose:
        for client in client_list:
            if not someone_choosing and client.chosen_character is None:
                send_message(character_list, client.client_socket)
                someone_choosing = True
            else:
                send_message('waiting', client.client_socket)

        for client in client_list[:]:
            character = receive_message(client.client_socket)
            if character == 'exit':
                client_list.remove(client)
                client.client_socket.close()
                someone_choosing = False
            elif character != 'waiting':
                client.chosen_character = character
                character_list.remove(character)
                someone_choosing = False

        everyone_chose = True
        for client in client_list:
            everyone_chose = everyone_chose and client.chosen_character is not None

    for client in client_list:
        send_message('done', client.client_socket)
    # End choose_character


def send_winner(client_list):  # Sends the winner of the game to the clients
    game_winner = ''
    most_wins = 0
    for client in client_list:
        if client.wins > most_wins:
            most_wins = client.wins
            game_winner = client.user_name
        elif client.wins == most_wins:
            game_winner += ' and ' + client.user_name
    for client in client_list:
        send_message(game_winner, client.client_socket)
    # End send_winner


def main():
    cubix_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cubix_server.bind(('0.0.0.0', 6565))

    cubix_database = sqlite3.connect(DATABASE_FOLDER_ROUTE + DATABASE_NAME)

    cubix_cursor = cubix_database.cursor()

    client_list, num_rounds = collect_clients(cubix_server, cubix_cursor)

    game_client_list = client_list.copy()
    if len(client_list) >= MINIMUM_PLAYERS:
        for client in client_list:
            send_message('The game is ready', client.client_socket)
        # Adding clock
        clock = pygame.time.Clock()

        while num_rounds != 0:
            num_rounds -= 1
            if len(game_client_list) >= MINIMUM_PLAYERS:
                new_game_id = cubix_cursor.execute('SELECT max(ID) FROM games').fetchone()[0] + 1
                date = time.asctime()

                winner = main_physical_game(clock, game_client_list)
                client_winner = None
                for client in client_list:
                    if client.user_name == winner.user_name:
                        client_winner = client
                winner = client_winner

                winner.wins += 1
                players = ''
                for client in client_list:
                    players += client.user_name + ', '
                players = players[:-2]

                game_data = [new_game_id, date, players, winner.user_name]
                cubix_cursor.execute('INSERT INTO games VALUES(?,?,?,?)', game_data)

                for client in client_list:  # Updates the users database
                    numgames = \
                        cubix_cursor.execute('SELECT numgames FROM users WHERE ID=?', [client.user_id]).fetchone()[
                            0] + 1
                    wins = cubix_cursor.execute('SELECT wins FROM users WHERE ID=?', [client.user_id]).fetchone()[0]
                    if client is winner:
                        wins += 1
                    cubix_cursor.execute('''UPDATE users
                    SET numgames = ?,
                        wins = ?
                    WHERE ID = ?''', [numgames, wins, client.user_id])
        send_winner(client_list)
    else:
        for client in client_list:
            send_message('Not enough players are present', client.client_socket)

    cubix_database.commit()

    for client in game_client_list:
        client.client_socket.close()
    cubix_server.close()
    cubix_database.close()


if __name__ == '__main__':
    main()
