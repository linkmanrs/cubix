__author__ = 'Roy'

import random
import pygame
import socket
import msgpack
import sqlite3
import select
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


def main_physical_game(clock, client_list):  # Main physical game
    global_var = GlobalVariable()

    make_players(global_var, client_list)

    floor(global_var)

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

        if len(client_list) == 0:  # Ends the game if all the players left
            finish = True

        # End of main loop
    print('game ended')
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
        new_status_list = ['update', sprite.object_id, sprite.get_pos()[0], sprite.get_pos()[1], sprite.facing_right]
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


def make_players(global_var, client_list):  # Create players
    i = 0
    for client in client_list:
        player = Player(i, 0, global_var.object_id, client.chosen_character, client.user_name)
        client.add_player_id(global_var.object_id)
        global_var.object_id += 1
        new_status('new', player, global_var)
        global_var.player_list.append(player)
        i += 150
    # End make_players


def floor(global_var):  # Creates a floor with blocks
    for i in range(9):
        block = Block(100 * i, WINDOWS_HEIGHT - 100, global_var.object_id)
        global_var.object_id += 1
        new_status('new', block, global_var)
        global_var.block_list.append(block)
    # End floor


def manage_event(global_var, event, client, client_list):  # Manages the events that are received
    if len(global_var.player_list) != 0:
        for player in global_var.player_list:
            if player.object_id == client.player_id:
                if event.type == pygame.QUIT:
                    # new_quit_status(global_var)
                    player_left(global_var, player, client, client_list)
                else:
                    manage_pressed_buttons(player, event, global_var)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # new_quit_status(global_var)
                        player_left(global_var, player, client, client_list)
            else:
                if event.type == pygame.QUIT:
                    # new_quit_status(global_var)
                    player_left(global_var, None, client, client_list)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # new_quit_status(global_var)
                        player_left(global_var, None, client, client_list)
    else:
        if event.type == pygame.QUIT:
            # new_quit_status(global_var)
            player_left(global_var, None, client, client_list)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # new_quit_status(global_var)
                player_left(global_var, None, client, client_list)
    # End manage_event


def manage_pressed_buttons(player, event, global_var):  # Manages the list of pressed buttons
    if event.type == pygame.KEYDOWN:
        player.pressed_buttons.append(event.key)
    if player.can_move:
        for key in player.pressed_buttons:
            control_movement(player, key, global_var)
    if event.type == pygame.KEYUP:
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

        player.check_facing()

        player.update_loc()
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


def manage_collision(player, global_var):  # Manages the collision protocol
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


def choose_command_at_enterence(cursor, client, username_list):  # Let the user pick the action he wants to do
    command = receive_message(client)
    action = {
        'sign up': register_user,
        'log in': sign_in
    }
    if not action.get(command) is None:
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
    hash_db, salt = hash_password(password)
    data = [new_user_id, username, hash_db, salt]
    cubix_cursor.execute('INSERT INTO users VALUES(?,?,?,?,0,0)', data)
    send_message('user registered and logged in', client)
    return True, new_user_id
    # End register_user


def sign_in(cubix_cursor, client, username_list):  # lets the user try to sign in
    selected_name = False
    username = ''
    while not selected_name:
        username = receive_message(client)
        exist = False
        for name in username_list:  # Checks if the username already exists in the database
            if name[0] == username:
                exist = True
        if exist:
            send_message('username accepted', client)
            selected_name = True
        else:
            send_message('username doesnt exist', client)

    tries = 3
    accepted = False
    user_hash = cubix_cursor.execute('SELECT hash FROM users WHERE username=?', [username]).fetchone()[0]
    user_salt = cubix_cursor.execute('SELECT salt FROM users WHERE username=?', [username]).fetchone()[0]
    while tries > 0 and not accepted:
        password = receive_message(client)
        if verify_password(user_hash, user_salt, password):
            send_message('password accepted', client)
            accepted = True
        else:
            tries -= 1
            if tries > 0:
                send_message('that the wrong password!', client)
            else:
                send_message('DENIED!, too many tries were used', client)
    user_id = None
    if accepted:
        user_id = cubix_cursor.execute('SELECT ID FROM users WHERE username=?', [username]).fetchone()[0]
        send_message('you are now logged in', client)
    else:
        send_message('try to remember the password next time', client)
    return accepted, user_id
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


def confirmation_count(client_list):
    con_count = 0
    for client in client_list:
        if client.accepted is not None:
            con_count += 1
    return con_count
    # End confirmation_count


def collect_clients(cubix_server, cubix_cursor):  # Collects between 2-4 clients to play the game
    client_list = []

    '''input_received = False
    players_expected = ''
    while not input_received:
        players_expected = input("how many players expected? (a number between 1 - 4)")
        if players_expected.isdecimal():
            players_expected = int(players_expected)
            if 1 <= players_expected <= 4:
                input_received = True
            else:
                print('incorrect input')
        else:
            print('incorrect input')'''

    cubix_server.listen(4)
    read_list = [cubix_server]
    client_id = 0
    username_list = cubix_cursor.execute('SELECT username FROM users').fetchall()
    while not confirmation_count(client_list) == 2:
        readable, writable, errored = select.select(read_list, [], [])
        for soc in readable:
            if soc is cubix_server:
                (client_socket, client_address) = cubix_server.accept()
                new_client = ClientPlayer(client_id, client_socket, client_address)
                client_list.append(new_client)
                print("player found")
                client_id += 1
                read_list.append(client_socket)
            else:
                accepted, user_id = choose_command_at_enterence(cubix_cursor, soc, username_list)
                for client in client_list:
                    if client.client_socket is soc:
                        client.accepted = accepted
                        client.user_id = user_id
                '''data = socket.recv(1024)
                if data:
                    socket.send(data)
                else:
                    socket.close()
                    read_list.remove(socket)'''

    for client in client_list:
        if not client.accepted:
            client_list.remove(client)
            client.client_socket.close()

    '''while client_id != players_expected:  # Collecting the players
        print("waiting for more players")'''

    print("all players are present")

    character_list = ['cuby', 'sphery', 'triangly', 'penty']
    for client in client_list:
        send_status(character_list, client)
        character = receive_message(client.client_socket)
        client.chosen_character = character
        character_list.remove(character)
    print('characters are chosen and the game is ready!')

    return client_list
    # End collect_clients


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


def main():
    cubix_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cubix_server.bind(('0.0.0.0', 6565))

    cubix_database = sqlite3.connect(DATABASE_FOLDER_ROUTE + DATABASE_NAME)

    cubix_cursor = cubix_database.cursor()

    client_list = collect_clients(cubix_server, cubix_cursor)

    if len(client_list) >= 2:
        for client in client_list:
            send_message('The game is ready', client.client_socket)
        # Adding clock
        clock = pygame.time.Clock()

        main_physical_game(clock, client_list)
    else:
        for client in client_list:
            send_message('Not enough players are present', client.client_socket)

    for client in client_list:
        client.client_socket.close()
    cubix_server.close()


if __name__ == '__main__':
    main()
