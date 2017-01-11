import os
import config
import sqlite3

def init_db():
    # delete if exists
    if os.path.isfile(config.db_name):
        os.system('rm %s' % (config.db_name))
        print 'database deleted successfully'

    # create database
    conn = sqlite3.connect(config.db_name)
    print 'database created successfully'

    # create table
    conn.execute('''CREATE TABLE user (
        username CHAR(128) PRIMARY KEY NOT NULL,
        password CHAR(128) NOT NULL,
        online_time INT NOT NULL);''')
    print 'table created successfully'

    # init records
    conn.execute('INSERT INTO user (username, password, online_time) VALUES ("netease1", "%s", 0)' % config.md5('123'));
    conn.execute('INSERT INTO user (username, password, online_time) VALUES ("netease2", "%s", 0)' % config.md5('123'));
    conn.execute('INSERT INTO user (username, password, online_time) VALUES ("netease3", "%s", 0)' % config.md5('123'));
    conn.execute('INSERT INTO user (username, password, online_time) VALUES ("netease4", "%s", 0)' % config.md5('123'));
    conn.commit()
    print 'records created successfully'

    # test
    cursor = conn.execute('SELECT username, password, online_time from user')
    for row in cursor:
        print row[0], row[1], row[2]

    # close database connection
    conn.close()
    print 'database closed successfully'

def is_exist(username, password):
    conn = sqlite3.connect(config.db_name)
    cursor = conn.execute('SELECT count(*) from user WHERE username = "%s" and password = "%s"' % (username, config.md5(password)))
    row = cursor.fetchone()
    res = True if row[0] == 1 else False
    conn.close()
    return res

def update(username, online_time):
    conn = sqlite3.connect(config.db_name)
    conn.execute('UPDATE user SET online_time = online_time + %d WHERE username = "%s"' % (online_time, username))
    conn.commit()
    conn.close()

def add(username, password):
    conn = sqlite3.connect(config.db_name)
    conn.execute('INSERT INTO user (username, password, online_time) VALUES ("%s", "%s", 0)' % (username, config.md5(password)));
    conn.commit()
    conn.close()

def show():
    out = ''
    conn = sqlite3.connect(config.db_name)
    cursor = conn.execute('SELECT username, online_time from user')
    for row in cursor:
        out += row[0] + ': ' + str(row[1]) + '\n'
    conn.close()
    return out

if __name__ == '__main__':
    init_db()
    # print show()





