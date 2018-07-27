#!/usr/bin/env python

__all__ = []

import sys

if sys.version_info[0] == 2:
   from Tkinter import *
   from tkMessageBox import *
   import ttk
else:
   from tkinter import *
   from tkinter.messagebox import *
   import tkinter.ttk as ttk

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
TODO: Please update documentation. 

OLD doc: 
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

        
class MainWindow():    
    def __init__(self, a2p2client):
                
        self.a2p2client = a2p2client

        self.requestAbort = False
        
        self.window=Tk()        
        self.window.title("Title TBD")

        self.notebook = ttk.Notebook(self.window)

        self.logFrame = Frame(self.notebook)
        
        self.logtext = Text(self.logFrame, width=120)
        scroll = Scrollbar(self.logFrame, command=self.logtext.yview)
        self.logtext.configure(yscrollcommand=scroll.set)
        scroll.pack(side=RIGHT, fill=Y)
        self.logtext.pack(fill=BOTH)
        self.logFrame.pack()
        
        self.helpFrame = Frame(self.notebook)
        
        self.helptext = Text(self.helpFrame, width=120)
        self.helptext.insert(END,HELPTEXT)
        helpscroll = Scrollbar(self.helpFrame, command=self.helptext.yview)
        self.helptext.configure(yscrollcommand=helpscroll.set)
        helpscroll.pack(side=RIGHT, fill=Y)
        self.helptext.pack(fill=BOTH)
        self.helpFrame.pack()
        
        # add tab and store index for later use in showFacilityUI
        self.tabIdx={}
        self.registerTab("LOG", self.logFrame)
        self.registerTab("HELP", self.helpFrame)
        self.notebook.select(self.tabIdx["LOG"])
        
        
        self.notebook.pack(side=TOP, fill=BOTH, expand=True)

        self.log_string = StringVar()
        self.log_string.set("log...")
        self.log = Label(self.window,textvariable=self.log_string)
        self.log.pack()

#
        buttonsFrame = Frame(self.window)
        buttonsFrame.columnconfigure(3, weight=1)
        buttonsFrame.rowconfigure(0, weight=1)
#
        self.buttonabort_strval=StringVar()
        self.buttonabort_strval.set("ABORT")
        self.buttonabort = Button(buttonsFrame,textvariable=self.buttonabort_strval,command=self.on_buttonabort_clicked)
        self.buttonabort.grid(row=0,column=2)
#        
        self.buttonhelp = Button(buttonsFrame,text="HELP",command=self.on_buttonhelp_clicked)
        self.buttonhelp.grid(row=0,column=3)
        buttonsFrame.pack(anchor=S)
        
        self.status_bar = StatusBar(self.window)
        self.status_bar.pack(side=BOTTOM,  fill=X)
        self.progress_value=self.status_bar.progress_value
        
    
    def __del__(self):
      self.window.destroy()

    def registerTab(self, text, widget):
        self.notebook.add(widget, text=text)
        self.tabIdx[text]=len(self.tabIdx)

    def showFacilityUI(self, facilityUI):
        if not facilityUI.facility.facilityName in self.tabIdx.keys():
            self.registerTab(facilityUI.facility.facilityName, facilityUI)
        self.notebook.select(self.tabIdx[facilityUI.facility.facilityName])

    def quitAfterRunOnce(self):
      self.window.quit()

    def loop(self):
        self.window.after(50, self.quitAfterRunOnce)
        self.window.mainloop();
        self.update_status_bar()

    def innerloop(self):
        self.window.after(50, self.quitAfterRunOnce)
        self.window.mainloop();
        
    def on_buttonabort_clicked(self):
        self.requestAbort = True
        
    def update_status_bar(self):
        self.status_bar.set_label("SAMP","SAMP: %s" % self.a2p2client.a2p2SampClient.get_status())
        self.status_bar.set_label("API","API: %s" % self.a2p2client.apiManager.get_status())

    def get_api(self):
        return self.api

    def addToLog(self,text, displayString=True):
        if displayString:
            self.log_string.set(text)
        self.logtext.insert(END, "\n"+text)
  
    def ShowErrorMessage(self,text):
        dialog = showerror("Error",text)

    def ShowWarningMessage(self,text):
        dialog = showwarning("Warning",text)

    def ShowInfoMessage(self,text):
        dialog = showinfo("Info",text)

    def on_buttonhelp_clicked(self):
         self.ShowInfoMessage(HELPTEXT)

    def setProgress(self,perc):
      self.progress_value.set(perc)
      if ( perc <= 0 ) or ( perc > 0.99 ):
        self.isIdle();
      else:
        self.isBusy();
      self.innerloop()

class StatusBar(Frame):
    def __init__(self, root, **kw):
        Frame.__init__(self,root,**kw)
        self.labels = {}
        
        self.progress_value = DoubleVar()
        self.progress_value.set(0.0)
        self.progressbar = ttk.Progressbar(self, orient='horizontal',length=200,maximum=1,variable=self.progress_value,mode='determinate')#, from_=0, to=1, resolution=0.01,showvalue=0,takefocus=0)
        self.progressbar.pack(side=LEFT)
            
    def set_label(self, name, text='', side=RIGHT, width=0):
        if name not in self.labels:
            label = Label(self)
            label.pack(side=side, pady=0, padx=4, anchor=E)
            self.labels[name] = label
        else:
            label = self.labels[name]
        if width != 0:
            label.config(width=width)
        label.config(text=text)      
      
      
class FacilityUI(Frame):
    def __init__(self, facility):    
        Frame.__init__(self, facility.a2p2client.ui.notebook)
        #self.pack(fill=BOTH)
        self.facility=facility
        self.a2p2client=facility.a2p2client
        