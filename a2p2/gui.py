#!/usr/bin/env python

__all__ = []

try:
    import pygtk
    pygtk.require('2.0')
    import gtk
except ImportError:
    pass # We should switch to NO-GUI mode

import time

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c, c) for c in text)

#help text in Pango Markup syntax https://developer.gnome.org/pango/stable/PangoMarkupFormat.html
HELPTEXT = """
This application provides the link between ASPRO (that you should have started) and ESO's P2 repository for Observing Blocks (OBs).

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
        # TODO check projectId because it is not used ?
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
    #    return """projectId:'%s', instrument:'%s', containerId:'%s'""" % (self.projectId, self.instrument, self.containerId)
        return """instrument:'%s', containerId:'%s'""" % (self.instrument, self.containerId)

class LoginWindow:
    def __init__(self, a2p2client):

        self.a2p2client = a2p2client
        self.api = None

        username = '52052'
        password = 'tutorial'
        self.login = [username, password]

        self.containerInfo = P2Container()

        self.requestAbort = False

        #one could probably limit the treeView with the instrument supported by ASPRO!!!!
        self.supportedInstrumentsByAspro = ['GRAVITY', 'MATISSE', 'AMBER', 'PIONIER']

    def get_api(self):
        return self.api

    def is_connected(self):
        # return None other the api connected
        return self.api

    def is_ready_to_submit(self):
        return self.api and self.containerInfo.is_ok()

    def get_containerInfo(self):
        return self.containerInfo




    # store runs in a list of tuples
    # TODO move this code into the api module
    def get_runs(self):

        runs, _ = self.api.getRuns()
        valid_runs = {}
        try:
            for run in runs:
                if run['instrument'] in self.supportedInstrumentsByAspro:
                    itemLabel = "%s - %s" % (run['progId'], run['instrument'])
                    valid_runs[itemLabel] = self.get_items(run)

            res = []
            pos = 0
            for label, item in valid_runs.items():
                if "containerId" in item.keys():
                    e = "%s / %s" % (label, item['containerId'])
                else:
                    e = " TBD for %s / %s" % (label, item)
                pos += 1
                res.append ([pos, e, item])

        except Exception as e:
            import time
            self.ShowErrorMessage('%s' % str(e))
            return

        return res


    def get_items(self, run):
        return run
        containerId = run['containerId']
        # TODO take advantage of itemType ?OB Group / Concatenation
        items = getFolders(self.api, containerId)
        if len(items) == 0:
            return run
        else:
            children = {}
            for item in items:
                itemLabel = "%s - %s" % (item['containerId'], item['name'])
                children[item] = get_items(item)
            return children


class TextWindow(LoginWindow):
    def __init__(self, a2p2client):
        LoginWindow.__init__(self, a2p2client)
        print("Welcome in the text UI of A2P2")
        import curses
        self.stdscr = curses.initscr()
        self.stdscr.keypad(True)
        self.stdscr.clear()
        curses.halfdelay(10)

    def __del__(self):
        import curses
        curses.endwin()
        print("closing the text UI")

    def loop(self):
        # force to react to every typed key
        import curses
        curses.cbreak()
        curses.halfdelay(10)

        selectedOB = self.get_containerInfo().projectId
        if not selectedOB:
            selectedOB = " -- "
        banner = "- Welcome in the text UI of A2P2 - / SAMP %s / API %s [%s] : username:%s" % (self.a2p2client.a2p2SampClient.get_status(), self.a2p2client.apiManager.get_status(), selectedOB, self.login[0])
        self.stdscr.addstr(0, 0, banner)
        menu = "( c/onnect - q/uit - r/efresh screen - u/ser credential)"
        if self.a2p2client.apiManager.is_connected():
            menu = "( s/elect run - q/uit - r/efresh screen - u/ser credential)"
        self.stdscr.addstr(1, 30, menu)

        # TODO dequeu last logs
        lastLogs = []
        #q = self.a2p2client.getLoggingQueue()
        s = 0
        #while not q.empty() and len(lastLogs) < 5:
            #lastLogs.append(q.get())
        self.ShowLogs(lastLogs)

        # Clean and place cursor
        self.stdscr.addstr(2, 0, "?    ")
        self.stdscr.addstr(2, 0, "? ")

        self.stdscr.refresh()
        try:
            key = self.stdscr.getkey()
            self.handle(key)
        except: # todo filter execption
            pass


    def handle(self, key):
        if key == "r":
            self.stdscr.clear()
        if key == "p":
            self.progress(50)
        if key == "q":
            self.requestAbort = True
            return
        elif key == "c":
            self.ShowInfoMessage("Trying to connect on API")
            self.api = self.a2p2client.apiManager.connect(self.login[0], self.login[1])
            self.ShowInfoMessage("Connected on API")
            runs, _ = self.api.getRuns()
            if len(runs) == 0:
                self.ShowErrorMessage("No Runs defined, impossible to program ESO's P2 interface. Quit or try again.")
                #self.requestAbort = True
                return
        elif key == "s":
            id2run = {}
            id2label = {}
            runs = self.get_runs()
            summary = ["%i runs retrieved for supported instruments" % (len(runs))]
            run_choices = []
            for pos, label, run in runs:
                run_choices.append("%i) %s " % (pos, label))
                id2run[pos] = run
                id2label[pos] = label
            self.ShowMessages("..", summary + run_choices)
            self.stdscr.addstr(3, 0, "Select destination container :")
            s = self.stdscr.getstr(15)
            self.stdscr.clear()
            try:
                i = int(s)
                run = id2run[i]
                id = id2label[i]
                instru = run['instrument']
                containerId = run['containerId']
                self.containerInfo.store(id, instru, containerId)
                self.ShowInfoMessage("selected container : '%s'" % (self.containerInfo))
            except Exception as e:
                self.ShowInfoMessage("invalid user input : '%s' %s" % (str(s), str(e)))
        elif key == "u":
            self.stdscr.addstr(3, 0, "1/2 - set API username :")
            s = self.stdscr.getstr(15)
            self.login[0] = s.decode('utf-8')
            self.stdscr.clear()

            self.stdscr.addstr(3, 0, "2/2 - set API password :")
            s = self.stdscr.getstr(15)
            self.login[1] = s.decode('utf-8')
            self.stdscr.clear()



    def setProgress(self, perc):
        self.stdscr.addstr(2, 50, "Progress: [{1:10}] {0}%".format(perc * 10, "#"))
        self.stdscr.refresh()

    def ShowMessages(self, level, msgs):
        eraser = "                                          "
        i = 0
        for msg in msgs:
            self.stdscr.addstr(4 + i, 1, "%s: %s%s" % (level, msg, eraser))
            i += 1
        self.stdscr.refresh()

    def ShowMessage(self, level, msg):
        self.ShowMessages(level, [msg])

    def ShowErrorMessage(self, msg):
        self.ShowMessage("  ERROR", msg)
        #time.sleep(1)

    def ShowWarningMessage(self, msg):
        self.ShowMessage("WARNING", msg)
        #time.sleep(1)

    def ShowInfoMessage(self, msg):
        self.ShowMessage("   INFO", msg)

    def addToLog(self, text):
        self.stdscr.addstr(20, 0, "LOG: %s" % (text))

    def ShowLogs(self, logs):
        for i in range(0, len(logs)):
            self.stdscr.addstr(20 + i, 0, "LOG: %s" % (logs[i]))


class GtkWindow(LoginWindow):
    def __init__(self, a2p2client):
        LoginWindow.__init__(self, a2p2client)

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

        self.window.connect("delete-event", gtk.main_quit)
        self.window.show_all()

    def __del__(self):
        if not self.window.emit("delete-event", gtk.gdk.Event(gtk.gdk.DELETE)):
            self.window.destroy()

    def loop(self):
        while (gtk.events_pending ()):
            gtk.main_iteration()


    def addToLog(self, text):
        self.log.set_label(text)

    def on_buttonok_clicked(self, widget):
        self.api = self.a2p2client.apiManager.connect(self.username.get_text(), self.password.get_text())
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

        for i in range(len(runs)):
            if runs[i]['instrument'] in self.supportedInstrumentsByAspro:
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
                folders = getFolders(self.api, containerId)
                for j in range(len(folders)):
                    name = folders[j]['name']
                    contid = folders[j]['containerId']
                    entry_folder = self.store.append(entry_run, ['Folder:', name, contid])
                    folders2 = getFolders(self.api, contid)
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
                print ("*** Working in Folder %s, containerId: %i ***" % (folderName, new_containerId_same_run))
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

    def ShowErrorMessage(self, text):
        dialog = gtk.MessageDialog(type=gtk.MESSAGE_ERROR,
                                   buttons=gtk.BUTTONS_OK)
        dialog.set_markup(html_escape(text))
        dialog.run()
        dialog.destroy()

    def ShowWarningMessage(self, text):
        dialog = gtk.MessageDialog(type=gtk.MESSAGE_WARNING,
                                   buttons=gtk.BUTTONS_OK)
        dialog.set_markup(html_escape(text))
        dialog.run()
        dialog.destroy()

    def ShowInfoMessage(self, text):
        dialog = gtk.MessageDialog(type=gtk.MESSAGE_INFO,
                                   buttons=gtk.BUTTONS_OK)
        dialog.set_markup(html_escape(text))
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
