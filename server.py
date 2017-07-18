import socket
import os
import time
pageNum = 5
def server_thread(app):
        HOST = 'localhost'
        PORT = 9000

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s.bind((HOST, PORT))
        s.listen(5)

        print 'Server start at: %s:%s' %(HOST, PORT)
        print 'wait for connection...'

        clientPid = -1
        data = None
        app.tabs[pageNum].image.set_from_file("dead.png")

        while clientPid == -1:
            conn, addr = s.accept()
            print 'Connected by ', addr

            while True:
                data = conn.recv(1024)
                if(data != None):
                    if(data.split(' ')[0] == 'pid'):
                        clientPid = data.split(' ')[1]
                        app.tabs[pageNum].processStateLabel.set_label("process alive")
                        app.tabs[pageNum].image.set_from_file("alive.png")
                        break
            conn.close()
                 
                

        processPath = '/proc/{}'.format(clientPid)
        
        while os.path.exists(processPath):
            time.sleep(1)
            print('detect')

        app.tabs[pageNum].processStateLabel.set_label("proess dead")
        app.tabs[pageNum].image.set_from_file("dead.png")

        print '{} dead'.format(processPath)

def loop_server_thread(app):
    while True:
        server_thread(app)
