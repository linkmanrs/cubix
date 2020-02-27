__author__ = 'Roy'

import socket
import msgpack

DATABASE_FOLDER_ROUTE = '../database/'
DATABASE_NAME = 'cubix_database.db'
SERVER_IP = '127.0.0.1'
PORT = 6565


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


def send_message(message, client):  # sends the status list to the client
    packed_message = msgpack.packb(message, use_bin_type=True)
    client.send(str(len(packed_message)).encode() + b"|" + packed_message)
    # End send_status


def choose_command_at_enterence(client):  # Let the user pick the action he wants to do
    print('please choose one of these actions:')
    command_list = ['log in', 'sign up']
    command = input(command_list)
    send_message(command, client)
    action = {
        'sign up': sign_up,
        'log in': try_log
    }
    if not action.get(command) is None:
        return action.get(command)(client)
    else:
        return False
    # End choose_action


def sign_up(client):  # Registers a user to the database
    chose_name = False
    while not chose_name:
        user_name = input('please enter your username')
        if user_name != '':
            send_message(str(user_name), client)
            response = receive_message(client)
            print(response)
            if response == 'username accepted':
                chose_name = True
        else:
            print('invalid user name')

    chose_pass = False
    while not chose_pass:
        password = input('please enter your password')
        if password != '':
            send_message(str(password), client)
            chose_pass = True
        else:
            print('invalid password')
    print(receive_message(client))
    return True
    # End register_user


def try_log(client):  # Trying to log in to the server
    selected_name = False
    while not selected_name:
        user_name = input('please enter your username')
        if user_name != '':
            send_message(str(user_name), client)
            response = receive_message(client)
            print(response)
            if response == 'username accepted':
                selected_name = True
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
        print(receive_message(client))
    return accepted
    # End try_log


def choose_command_after_logged(client, command):  # Let the user pick the action he wants to do
    action = {
        'get status': get_status,
        'play game': play_game
    }
    if not action.get(command) is None:
        action.get(command)(client)
    # End choose_action


def get_status(client):  # Gets the users status from the server
    print(receive_message(client))
    # End get_status


def play_game(client):  # Plays the game
    print()
    # End play_game


def main():
    cubix_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cubix_client.connect((SERVER_IP, PORT))

    print('please choose one of these actions:')
    command_list = receive_message(cubix_client)
    command = input(command_list)
    send_message(command, cubix_client)
    logged_in = choose_command_at_enterence(cubix_client, command)
    if logged_in:
        print('please choose one of these actions:')
        command_list = receive_message(cubix_client)
        command = input(command_list)
        send_message(command, cubix_client)
        choose_command_after_logged(cubix_client, command)

    cubix_client.close()


if __name__ == '__main__':
    main()
