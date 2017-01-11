import db
import time
import config
import socket
import threading
from User import User
from datetime import datetime

# build server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(config.server_address)
server_socket.listen(config.max_connect_count)

# session information
username_dict = {}
room_dict = {config.default_room : set()}

# 21game information
is_running = False
room_answer = {}
room_number_list = {}
username_answered = set()

def tcplink(client_socket, client_address):
    print 'LOG: accept new connection from %s:%s...' % client_address

    _username, _room, _login_time = None, None, None

    while True:
        try:
            data = client_socket.recv(config.max_byte_count)
            data = config.clean(data)
            if not data: continue
            t = data.split(' ')

            if t[0] == 'exit': ######################################################## exit
                if len(t) != 1: client_socket.send(config.format_error_info); continue

                break

            elif t[0] == 'login': ##################################################### login username password
                if len(t) != 3: client_socket.send(config.format_error_info); continue

                username, password = t[1], t[2]
                if db.is_exist(username, password):
                    if username in username_dict:
                        client_socket.send('[system] already login')
                    else:
                        _username, _room, _login_time = username, config.default_room, datetime.now()
                        room_dict[_room].add(_username)
                        username_dict[_username] = [client_socket, _room, _login_time]
                        client_socket.send('[system] login successfully')
                else:
                    client_socket.send('[system] wrong username or password')

            elif t[0] == 'register': ################################################## register username password
                if len(t) != 3: client_socket.send(config.format_error_info); continue

                username, password = t[1], t[2]
                if db.is_exist(username, password):
                    client_socket.send('[system] username exists')
                else:
                    db.add(username, password)
                    client_socket.send('[system] register successfully')

            elif t[0] == 'chat': ##################################################### chat word1 word2 ...
                if len(t) < 2: client_socket.send(config.format_error_info); continue
                if _username == None: client_socket.send(config.not_login_error_info); continue

                sentence = ' '.join(t[1:])
                for username in room_dict[_room]:
                    if username != _username:
                        username_dict[username][0].send(_username + ': ' + sentence)

            elif t[0] == 'chat_to': ################################################## chat_to username word1 word2 ... 
                if len(t) < 3: client_socket.send(config.format_error_info); continue
                if _username == None: client_socket.send(config.not_login_error_info); continue

                username = t[1]
                sentence = ' '.join(t[2:])
                username_dict[username][0].send(_username + ': ' + sentence)

            elif t[0] == 'create_room': ############################################## create_room room
                if len(t) != 2: client_socket.send(config.format_error_info); continue
                if _username == None: client_socket.send(config.not_login_error_info); continue

                room = t[1]
                if room in room_dict:
                    client_socket.send('[system] room exists')
                else:
                    # leave previous room
                    room_dict[_room].remove(_username)
                    if _room != config.default_room and len(room_dict[_room]) == 0:
                        del room_dict[_room]
                    # enter new room
                    room_dict[room] = set([_username])
                    _room = room
                    username_dict[_username][1] = _room
                    client_socket.send('[system] create successfully')

            elif t[0] == 'enter_room': ############################################### enter_room room
                if len(t) != 2: client_socket.send(config.format_error_info); continue
                if _username == None: client_socket.send(config.not_login_error_info); continue

                room = t[1]
                if room not in room_dict:
                    client_socket.send('[system] room not exists')
                else:
                    if room == _room: continue
                    # leave previous room
                    room_dict[_room].remove(_username)
                    if _room != config.default_room and len(room_dict[_room]) == 0:
                        del room_dict[_room]
                    # enter new room
                    room_dict[room].add(_username)
                    _room = room
                    username_dict[_username][1] = _room
                    client_socket.send('[system] enter successfully')

            elif t[0] == 'exit_room': ############################################### exit_room
                if len(t) != 1: client_socket.send(config.format_error_info); continue
                if _username == None: client_socket.send(config.not_login_error_info); continue

                if _room == config.default_room:
                    client_socket.send('[system] not in a room')
                else:
                    # leave previous room
                    room_dict[_room].remove(_username)
                    if len(room_dict[_room]) == 0:
                        del room_dict[_room]
                    # enter lobby
                    _room = config.default_room
                    room_dict[_room].add(_username)
                    username_dict[_username][1] = _room
                    client_socket.send('[system] exit successfully')

            elif t[0] == '21game': ################################################## exit room
                if len(t) != 2: client_socket.send(config.format_error_info); continue
                if _username == None: client_socket.send(config.not_login_error_info); continue

                global is_running
                if is_running == True:
                    if _username in username_answered:
                        client_socket.send('[game] you have answered')
                    else:
                        if _room not in room_number_list:
                            client_socket.send('[system] not in game time in this room')
                        else:
                            value = config.get_value(t[1], room_number_list[_room])
                            if value == None:
                                client_socket.send('[game] equation format error')
                            elif value > 21:
                                client_socket.send('[game] your answer > 21')
                            else:
                                username_answered.add(_username)
                                if _room not in room_answer: room_answer[_room] = []
                                room_answer[_room].append([_username, value])
                                client_socket.send('[game] your score is %f' % value)
                else:
                    client_socket.send('[system] not in game time')

            elif t[0] == 'sudo': #################################################### sudo
                if len(t) != 1: client_socket.send(config.format_error_info); continue

                response = '\n' + '-' * 20 + '\n'
                response += '### room_dict:\n'
                for room in room_dict:
                    response += str(room) + ': ' + ', '.join(list(room_dict[room])) + '\n'
                response += '### username_dict:\n'
                for key in username_dict:
                    room = username_dict[key][1]
                    login_time = username_dict[key][2].strftime('%Y-%m-%d %H:%M:%S')
                    response += key + ': ' + room + ', ' + login_time + '\n'
                response += '### db:\n' + db.show()
                response += '-' * 20
                client_socket.send(response)

            else: ################################################################### default
                client_socket.send('[system] unknown request')
        
        except Exception, ex:
            print ex
            break

    # save online time
    online_time = (datetime.now() - _login_time).seconds
    db.update(_username, online_time)

    del username_dict[_username]
    room_dict[_room].remove(_username)
    if len(room_dict[_room]) == 0:
        del room_dict[_room]

    client_socket.close()

    print 'LOG: connection from %s:%s closed.' % client_address



def game_processor():
    while True:
        now = datetime.now()
        minute, second = now.minute, now.second
        if ( (minute == 0 or minute == 30) and (second == 0 or second == 1) ) or \
           ( (minute == 29 or minute == 59) and second == 59 ):
        # if second == 59 or second == 0 or second == 1: # for test
            # init game
            global is_running
            is_running = True
            for room in room_dict:
                if room == config.default_room: continue
                room_number_list[room] = config.get_number_list()
                for username in room_dict[room]:
                    username_dict[username][0].send('[game] %s' % ' '.join(room_number_list[room]))
            
            # game time
            time.sleep(15)

            # evaluate game
            for room in room_answer:
                room_answer[room].sort(key=lambda x: 21 - x[1])
                info = None
                if len(room_answer[room]) == 0:
                    info = '[game] no one wins 21game'
                else:
                    info = '[game] %s wins 21game, his score is %f' % (room_answer[room][0][0], room_answer[room][0][1])
                for username in room_dict[room]:
                    username_dict[username][0].send(info)

            # clean game
            is_running = False
            room_answer.clear()
            room_number_list.clear()
            username_answered.clear()

        time.sleep(1)


t = threading.Thread(target = game_processor, args = ())
t.start()

# main loop
while True:
    client_socket, client_address = server_socket.accept()
    t = threading.Thread(target = tcplink, args = (client_socket, client_address))
    t.start()


# close database
conn.close()






