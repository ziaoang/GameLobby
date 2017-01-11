import socket
import threading
from datetime import datetime

ip, port = '127.0.0.1', 8888
server_address = (ip, port)
max_byte_count = 1024

# start socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(server_address)

def send():
    while True:
        try:
            request = raw_input()
            client_socket.send(request)
        except Exception, ex:
            print ex
            break
    try:
        client_socket.close()
    except:
        pass

def receive():
    while True:
        try:
            data = client_socket.recv(max_byte_count)
            if not data: break
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ' + data
        except Exception, ex:
            print ex
            break
    try:
        client_socket.close()
    except:
        pass

t1 = threading.Thread(target = send, args = ())
t2 = threading.Thread(target = receive, args = ())
t1.start()
t2.start()


print '''--------------------
### order list
login username password
register username password
chat word1 word2 ...
chat_to username word1 word2 ...
create_room room
enter_room room
exit_room
21game answer
sudo
exit
--------------------'''
