__author__ = 'Roy'

import sqlite3
import socket
import msgpack
import hashlib
import binascii
import os

DATABASE_FOLDER_ROUTE = '../database/'
DATABASE_NAME = 'cubix_database.db'


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


def choose_command_at_enterence(cursor, client):  # Let the user pick the action he wants to do
    command = receive_message(client)
    action = {
        'sign up': register_user,
        'log in': sign_in
    }
    if not action.get(command) is None:
        return action.get(command)(cursor, client)
    else:
        return False, None
    # End choose_action


def register_user(cubix_cursor, client):  # Registers a user to the database
    new_user_id = cubix_cursor.execute('SELECT max(ID) FROM users').fetchone()[0] + 1
    chose_name = False
    username_list = cubix_cursor.execute('SELECT username FROM users').fetchall()
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
    send_message('please write your password', client)
    password = receive_message(client)
    hash_db, salt = hash_password(password)
    data = [new_user_id, username, hash_db, salt]
    cubix_cursor.execute('INSERT INTO users VALUES(?,?,?,?,0,0)', data)
    send_message('user registered and logged in', client)
    return True, new_user_id
    # End register_user


def sign_in(cubix_cursor, client):  # lets the user try to sign in
    selected_name = False
    username_list = cubix_cursor.execute('SELECT username FROM users').fetchall()
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


def choose_command_after_logged(cursor, client, user_id, command):  # Let the user pick the action he wants to do
    action = {
        'get status': collect_status,
        'play game': play_game
    }
    if not action.get(command) is None:
        return action.get(command)(user_id, cursor, client)
    else:
        return False, None
    # End choose_action


def collect_status(user_id, cubix_cursor, client):  # sends the status of the player
    numgames = cubix_cursor.execute('SELECT numgames FROM users WHERE ID=?', [user_id]).fetchone()[0]
    wins = cubix_cursor.execute('SELECT wins FROM users WHERE ID=?', [user_id]).fetchone()[0]
    status = 'you played {} games and won {} games'.format(numgames, wins)
    send_message(status, client)
    # End send_status


def play_game():  # Lunches the game
    print()
    # End play_game


def main():
    cubix_database = sqlite3.connect(DATABASE_FOLDER_ROUTE + DATABASE_NAME)

    cubix_cursor = cubix_database.cursor()

    cubix_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cubix_server.bind(('0.0.0.0', 6565))

    cubix_server.listen(1)
    (client_socket, client_address) = cubix_server.accept()

    command_list = ['log in', 'sign up']
    send_message(command_list, client_socket)

    logged_in, user_id = choose_command_at_enterence(cubix_cursor, client_socket)
    if logged_in:
        command_list = ['get status', 'play game']
        send_message(command_list, client_socket)
        command = receive_message(client_socket)
        choose_command_after_logged(cubix_cursor, client_socket, user_id, command)

    cubix_database.commit()

    cubix_database.close()
    client_socket.close()
    cubix_server.close()


if __name__ == '__main__':
    main()
