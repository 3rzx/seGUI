# usersPage.py - show selinux mappings
# Copyright (C) 2006,2007,2008 Red Hat, Inc.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# Author: Dan Walsh
import gtk
import gtk.glade
import gobject
import subprocess
import seobject
import pyudev
from semanagePage import *

##
# I18N
##
PROGNAME = "policycoreutils"
import gettext
gettext.bindtextdomain(PROGNAME, "/usr/share/locale")
gettext.textdomain(PROGNAME)
try:
    gettext.install(PROGNAME, localedir="/usr/share/locale", unicode=1)
except IOError:
    import builtins
    builtins.__dict__['_'] = unicode

white_list = [('248a','8566'), ('04f2','0408'),('10c4','ea60')]
hardwarekey = [('10c4','ea60')]

class usbPage(semanagePage):

    def __init__(self, xml):
        semanagePage.__init__(self, xml, "usb", _("Usb Device"))

        self.store = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.view.set_model(self.store)
        self.store.set_sort_column_id(0, gtk.SORT_ASCENDING)

        col = gtk.TreeViewColumn(
            _("Usb Name"), gtk.CellRendererText(), text=0)
        col.set_sort_column_id(0)
        col.set_resizable(True)
        self.view.append_column(col)

        col = gtk.TreeViewColumn(
            _("Location"), gtk.CellRendererText(), text=1)
        col.set_resizable(True)
        self.view.append_column(col)

        col = gtk.TreeViewColumn(
            _("Whitelist"), gtk.CellRendererText(), text=2)
        col.set_resizable(True)
        self.view.append_column(col)

        col = gtk.TreeViewColumn(
            _("Authorization"), gtk.CellRendererText(), text=3)
        col.set_resizable(True)
        self.view.append_column(col)

        self.load()
        self.usbNameEntry = xml.get_widget("usbNameEntry")
        self.authorizationEntry = xml.get_widget("authorizationEntry")
        self.locationEntry = xml.get_widget("locationEntry")
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by('usb')
        observer = pyudev.MonitorObserver(monitor, self.guard)
        observer.start()

    def guard(action, device):
        if device.get('DEVTYPE') != 'usb_device':
            return
        if action == 'add': 
            self.load()
        elif action == 'remove':
            self.load()
        #print("test")
        return

    # loaing data
    def load(self, filt=""):
        self.filter = filt
        self.store.clear()
        context = pyudev.Context()
        for device in context.list_devices(subsystem='usb', DEVTYPE='usb_device'):
            uid = (device.get('ID_VENDOR_ID'), device.get('ID_MODEL_ID'))
            uName = device.get('ID_VENDOR') + ' ' + device.get('ID_MODEL')
            location = device.get('DEVNAME')
            inWhiteList = False
            if uid in white_list:
                nWhiteList = True
            if not (self.match(uName, filt) or self.match(location, filt) or self.match(inWhiteList, filt)):
                continue
            it = self.store.append()
            self.store.set_value(it, 0, uName)
            self.store.set_value(it, 1, location)
            self.store.set_value(it, 2, str(inWhiteList))
            self.store.set_value(it, 3, str(inWhiteList))
        
        self.view.get_selection().select_path((0,))
    
    def dialogInit(self):
        store, it = self.view.get_selection().get_selected()
        print (store)
        self.usbNameEntry.set_text(store.get_value(it, 0))
        self.usbNameEntry.set_sensitive(False)
        self.authorizationEntry.set_text(store.get_value(it, 3))
        self.locationEntry.set_text(store.get_value(it, 1))

    def dialogClear(self):
        self.usbNameEntry.set_text("")
        self.usbNameEntry.set_sensitive(True)
        self.authorizationEntry.set_text("")
        self.locationEntry.set_text("")

    def add(self):
        uName = self.usbNameEntry.get_text()
        author = self.authorizationEntry.get_text()
        location = self.locationEntry.get_text()

        self.wait()
        try:
            #subprocess.check_output("semanage user -a -R '%s' -r %s %s" % (roles, serange, user),
                                    #stderr=subprocess.STDOUT,
                                    #shell=True)
            self.ready()
            it = self.store.append()
            self.store.set_value(it, 0, uName)
            self.store.set_value(it, 1, location)
            self.store.set_value(it, 2, author)
            self.store.set_value(it, 3, author)
        except subprocess.CalledProcessError as e:
            self.error(e.output)
            self.ready()
            return False

    def modify(self):
        uName = self.usbNameEntry.get_text()
        author = self.authorizationEntry.get_text()
        location = self.locationEntry.get_text()

        self.wait()
        #cmd = "semanage user -m -R '%s' -r %s %s" % (roles, serange, user)
        try:
            #subprocess.check_output(cmd,
                                    #stderr=subprocess.STDOUT,
                                    #shell=True)
            self.ready()
            self.load(self.filter)
        except subprocess.CalledProcessError as e:
            self.error(e.output)
            self.ready()
            return False
        return True

    def delete(self):
        store, it = self.view.get_selection().get_selected()
        try:
            uName = store.get_value(it, 0)
            # if user == "root" or user == "user_u":
                #raise ValueError(_("SELinux user '%s' is required") % user)

            self.wait()
            # cmd = "semanage user -d %s" % user
            try:
                #subprocess.check_output(cmd,
                                        #stderr=subprocess.STDOUT,
                                        #shell=True)
                self.ready()
                store.remove(it)
                self.view.get_selection().select_path((0,))
            except subprocess.CalledProcessError as e:
                self.error(e.output)
                self.ready()
                return False
        except ValueError as e:
            self.error(e.args[0])
