#!/usr/bin/env python

__all__ = ['A2p2Client']


import cgi
import numpy as np
import p2api
import pygtk
import re
pygtk.require('2.0')
import gtk
import xml.etree.ElementTree

from utils import parseXmlMessage


#help text in Pango Markup syntax https://developer.gnome.org/pango/stable/PangoMarkupFormat.html
HELPTEXT = """
This applet provides the link between ASPRO (that you should have started) and ESO's P2 repository for Observing Blocks (OBs).

<span foreground="blue" size="x-large"> <b>Login:</b></span>
You must log in to the ESO User Portal using your identifiers to access the P2 repository. Please check on the ESO website in case of doubt.

<span foreground="blue" size="x-large"> <b>Select Run ID:</b> </span>
After successful login, you are presented with the Runs compatible with Aspro's known instruments. Select the Run, and eventually the subfolder of this Run, where you want to create the OB. Each Run corresponds to a specific instrument. This instrument must be the same as the one selected in ASPRO.

<span foreground="blue" size="x-large"> <b>Send configuration from Aspro:</b></span>
- In ASPRO, have an object, or an object selected, and check that all important informations (magnitudes, but also Instrument and Fringe Tracker Modes, eventually hour angles), are correctly set.
- In menu "Interop" select "<b>Send Obs. blocks to A2p2</b>"
- Block(s) are created and put in the P2 repository.
- If the source had one or more calibrators, blocks are created for them too.
- For each block submitted, a report is produced. Warnings are usually not significant.
- For more than 1 object sent, a <b>folder</b> containing the two or more blocks <b>is created</b>. In the absence of availability of grouping OBs (like for CAL-SCI-CAL) provided by ESO, this is the closets we can do.
- All the new OBs and folders will be available on <span foreground="blue" > <a href=\"https://eso.org/p2\">p2web</a> </span>
log"""

class P2Container:
    def __init__(self):
        self.projectId = None
        self.instrument = None
        self.containerId = None

    def store (self, projectId, instrument, containerId):
        self.projectId = projectId
        self.instrument = instrument
        self.containerId = containerId
        print ("*** Working with %s ***" % self)

    def store_containerId (self, containerId):
        self.containerId = containerId
        print ("*** Working with %s ***" % self)

    def is_ok(self):
        return (self.projectId != None)

    def __str__(self):
        return """projectId:'%s', instrument:'%s', containerId:'%s'""" % (self.projectId, self.instrument, self.containerId)

class LoginWindow:
    def __init__(self):
        username = '52052'
        password = 'tutorial'

        self.login = [username, password]
        self.containerInfo = P2Container()

        self.requestAbort = False

        self.api = None

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Connect with ESO DATABASE")
        self.window.set_size_request(300, 300)

        self.timeout_id = None

        vbox = gtk.VBox(False, 0)
        self.window.add(vbox)

        self.username_hbox = gtk.HBox(spacing=3)
        vbox.pack_start(self.username_hbox, False, False, 0)
        label = gtk.Label("USERNAME")
        self.username_hbox.pack_start(label, True, True, 0)
        self.username = gtk.Entry()
        self.username.set_text(self.login[0])
        self.username_hbox.pack_start(self.username, True, True, 0)

        self.password_hbox = gtk.HBox(spacing=6)
        vbox.pack_start(self.password_hbox, False, False, 0)
        label = gtk.Label("PASSWORD")
        self.password_hbox.pack_start(label, True, True, 0)
        self.password = gtk.Entry()
        self.password.set_visibility(False)
        self.password.set_text(self.login[1])
        self.password_hbox.pack_start(self.password, True, True, 0)

        self.tempolabel = gtk.Label("Please Log In ESO USER PORTAL ")
        vbox.pack_start(self.tempolabel, False, False, 0)


        self.scrollable = gtk.ScrolledWindow()
        # self.scrollable.set_vexpand(True)
        vbox.pack_start(self.scrollable, True, True, 0)

        self.progressbar = gtk.ProgressBar()
        vbox.pack_start(self.progressbar, False, True, 0)

        self.log = gtk.Label()
        self.log.set_line_wrap(True)
        vbox.pack_start(self.log, False, True, 0)

        hbox = gtk.HBox(spacing=6)
        vbox.pack_start(hbox, False, False, 0)

        self.buttonok = gtk.Button(label="LOG IN")
        self.buttonok.connect("clicked", self.on_buttonok_clicked)
        hbox.pack_start(self.buttonok, False, True, 0)

        self.buttonabort = gtk.Button(label="ABORT")
        self.buttonabort.connect("clicked", self.on_buttonabort_clicked)
        hbox.pack_start(self.buttonabort, False, True, 0)

        self.buttonhelp = gtk.Button(label="HELP")
        self.buttonhelp.connect("clicked", self.on_buttonhelp_clicked)
        hbox.pack_start(self.buttonhelp, False, True, 0)


        self.buttonfake = gtk.Button(label="FAKE READY")
        self.buttonfake.connect("clicked", self.on_buttonfake_clicked)
        hbox.pack_start(self.buttonfake, False, True, 0)

        self.window.connect("delete-event", gtk.main_quit)
        self.window.show_all()

    def __del__(self):
        if not self.window.emit("delete-event", gtk.gdk.Event(gtk.gdk.DELETE)):
            self.window.destroy()



    def addToLog(self, text):
        self.log.set_label(text)

    def is_connected(self):
        # return None other the api connected
        return self.api

    def is_ready_to_submit(self):
        print ("%s" % self.containerInfo)
        return self.api and self.containerInfo.is_ok()


    def load_ob(self, url):
        xml_ob = xml.etree.ElementTree.parse(url)
        parseXmlMessage(self, xml_ob, self.api, self.containerInfo)

    def on_buttonfake_clicked(self, widget):
        self.containerInfo.store("a", "GRAVITY", "c")
        toto.titi()
        self.api = "fake"


    def on_buttonok_clicked(self, widget):
        self.login[0] = (self.username.get_text())
        self.login[1] = (self.password.get_text())

        if self.login[0] == '52052':
            type = 'demo'
        else:
            type = 'production'
        self.api = p2api.ApiConnection(type, self.login[0], self.login[1])
        api = self.api
        runs, _ = self.api.getRuns()
        if len(runs) == 0:
            self.ShowErrorMessage("No Runs defined, impossible to program ESO's P2 interface.")
            self.requestAbort = True
            return

        self.buttonok.destroy()
        self.password_hbox.destroy()
        self.username_hbox.destroy()
        self.buttonabort.set_label("EXIT")
        self.tempolabel.set_text("Select the Project Id in the list:")

        self.store = gtk.TreeStore(str, str, int)
        self.runName = []
        self.instrument = []
        self.containerId = []
        self.treeiter = []
        #one could probably limit the treeView with the instrument supported by ASPRO!!!!
        supportedInstruments = ['GRAVITY', 'MATISSE', 'AMBER', 'PIONIER']

        for i in range(len(runs)):
            if supportedInstruments.count(runs[i]['instrument']) == 1:
                runName = runs[i]['progId']
                self.runName.append(runName)
                instrument = runs[i]['instrument']
                self.instrument.append(instrument)
                runId = runs[i]['runId']
                self.containerId.append(runId)
                entry_run = self.store.append(None, [runName, instrument, runId])
                self.treeiter.append(entry_run)
                # if folders, add them
                containerId = runs[i]['containerId']
                # FIXME: make it recursive!
                folders = getFolders(api, containerId)
                for j in range(len(folders)):
                    name = folders[j]['name']
                    contid = folders[j]['containerId']
                    entry_folder = self.store.append(entry_run, ['Folder:', name, contid])
                    folders2 = getFolders(api, contid)
                    for k in range(len(folders2)):
                        name2 = folders2[k]['name']
                        contid2 = folders2[k]['containerId']
                        entry_subfolder = self.store.append(entry_folder, ['Folder:', name2, contid2])
        self.treeview = gtk.TreeView(self.store)
        # create a CellRendererText to render the data
        renderer = gtk.CellRendererText()
        for i, column_title in enumerate(["Project ID", "Instrument", "Run ID"]):
            renderer = gtk.CellRendererText()
            column = gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)
        self.scrollable.add(self.treeview)
        self.treeselect = self.treeview.get_selection()
        self.treeselect.connect("changed", self.on_tree_selection_changed)
        self.treeview.connect("row-expanded", self.on_row_expanded)
        self.window.show_all()

    def on_row_expanded(self, view, treeiter, path):
        index = path[0]
        id = self.runName[index]
        if  id != 'Folder:': #get instrument
            instru = self.instrument[index]
            runId = self.containerId[index]
            run, _ = self.api.getRun(runId)
            containerId = run["containerId"]
            self.containerInfo.store(id, instru, containerId)

    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter != None:
            # self.flag[0] = 1
            # TODO can we remove previous line ?
            id = model[treeiter][0]
            if id == 'Folder:': #we have a folder
                new_containerId_same_run = model[treeiter][2]
                folderName = model[treeiter][1]
                print "*** Working in Folder %s, containerId: %i ***" % (folderName, new_containerId_same_run)
                self.addToLog('Folder: ' + folderName)
                self.containerInfo.store_containerId(new_containerId_same_run)
            else:
                instru = model[treeiter][1]
                if instru != self.containerInfo.instrument:
                    self.treeview.collapse_all() #otherwise problems! # TODO look at this case!!
                runId = model[treeiter][2]
                run, _ = self.api.getRun(runId)
                containerId = run["containerId"]
                self.addToLog('Run: ' + id)
                self.containerInfo.store(id, instru, containerId)

    def on_buttonabort_clicked(self, widget):
        self.requestAbort = True


    def language_filter_func(self, model, iter, data):
        """Tests if the language in the row is the one in the filter"""
        if self.current_filter_language is None or self.current_filter_language == "None":
            return True
        else:
            return model[iter][2] == self.current_filter_language
    def get_api(self):
        return self.api

    def ShowErrorMessage(self, text):
        dialog = gtk.MessageDialog(type=gtk.MESSAGE_ERROR,
                                   buttons=gtk.BUTTONS_OK)
        dialog.set_markup(text)
        dialog.run()
        dialog.destroy()

    def ShowWarningMessage(self, text):
        dialog = gtk.MessageDialog(type=gtk.MESSAGE_WARNING,
                                   buttons=gtk.BUTTONS_OK)
        dialog.set_markup(text)
        dialog.run()
        dialog.destroy()

    def ShowInfoMessage(self, text):
        dialog = gtk.MessageDialog(type=gtk.MESSAGE_INFO,
                                   buttons=gtk.BUTTONS_OK)
        dialog.set_markup(text)
        dialog.run()
        dialog.destroy()

    def on_buttonhelp_clicked(self, widget):
        dialog = gtk.MessageDialog(type=gtk.MESSAGE_INFO,
                                   buttons=gtk.BUTTONS_OK)
        dialog.set_markup(HELPTEXT)
        dialog.run()
        dialog.destroy()


    def setProgress(self, perc):
        self.progressbar.set_fraction(perc)
        while (gtk.events_pending ()):
            gtk.main_iteration ()

# TODO move into a common part
def getFolders(p2api, containerId):
    folders = []
    itemList, _ = p2api.getItems(containerId)
    for i in range(len(itemList)):
        if itemList[i]['itemType'] == 'Folder':
            folders.append(itemList[i])
    return folders
