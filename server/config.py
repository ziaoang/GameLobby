import re
import random
import hashlib

def md5(s):
    t = hashlib.md5()
    t.update(s)
    return t.hexdigest()

def clean(data):
    return re.sub(r"\s{2,}", " ", data).strip()

def get_number_list():
    number_list = []
    for i in range(4):
        number_list.append(str(random.randint(1, 10)))
    number_list.sort()
    return number_list

def get_value(s, number_list):
    try:
        for c in s:
            if c not in "+-*/()0123456789":
                return None
        
        s_number_list = re.findall(r'\d+', s)
        s_number_list.sort()
        for i in range(4):
            if s_number_list[i] != number_list[i]:
                return None

        return eval(s)

    except:
        return None

# database config
db_name = 'db.sqlite3'

# socket config
ip, port = '127.0.0.1', 8888
server_address = (ip, port)
max_connect_count = 100
max_room_count = 100
max_byte_count = 1024

# game lobby config
default_room = "-1"
format_error_info = '[system] request format error'
not_login_error_info = '[system] you should login first'


