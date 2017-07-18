import string
import gtk
import gtk.glade
import os
import gobject
import sys
import tempfile
import selinux
from threading import Thread 

INSTALLPATH = '/usr/share/system-config-selinux'
sys.path.append(INSTALLPATH)

try:
    from subprocess import getstatusoutput
except ImportError:
    from commands import getstatusoutput

ENFORCING = 1
PERMISSIVE = 0
DISABLED = -1
modearray = ("disabled", "permissive", "enforcing")

SELINUXDIR = "/etc/selinux/"
RELABELFILE = "/.autorelabel"

##
## I18N
##
PROGNAME = "policycoreutils"
try:
    import gettext
    kwargs = {}
    if sys.version_info < (3,):
        kwargs['unicode'] = True
    gettext.install(PROGNAME,
                    localedir="/usr/share/locale",
                    codeset='utf-8',
                    **kwargs)
except:
    try:
        import builtins
        builtins.__dict__['_'] = str
    except ImportError:
        import __builtin__
        __builtin__.__dict__['_'] = unicode

gobject.threads_init()
class alertPage:
    def __init__(self, xml):
    
        self.xml = xml
        self.processStateLabel = xml.get_widget("processState")
        self.image = xml.get_widget("processStateImage")
                               

    def get_description(self):
        return _("Alert page")

    def server_thread(self):
        HOST = 'localhost'
        PORT = 8001

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen(5)

        print 'Server start at: %s:%s' %(HOST, PORT)
        print 'wait for connection...'

        clientPid = -1
        data = None

        while clientPid == -1:
            conn, addr = s.accept()
            print 'Connected by ', addr

            while True:
                data = conn.recv(1024)
                if(data != None):
                    if(data.split(' ')[0] == 'pid'):
                        clientPid = data.split(' ')[1]
                        processStateLabel.set_label("process alive")
                        break
                 
                conn.close()

        processPath = '/proc/{}'.format(clientPid)
        
        while os.path.exists(processPath):
            time.sleep(1)
            print('detect')

        processStateLabel.set_label("proess dead")
        print '{} dead'.format(processPath)

        
