#!/usr/bin/env python

__all__ = []

import sys
from a2p2 import __version__

if sys.version_info[0] == 2:
   from Tkinter import *
   from tkMessageBox import *
   import ttk
else:
   from tkinter import *
   from tkinter.messagebox import *
   import tkinter.ttk as ttk

import time
      
HELPTEXT = """This application provides the link between ASPRO (that you should have started) and interferometers facilities.

"""

class MainWindow():    
    def __init__(self, a2p2client):
                
        self.a2p2client = a2p2client

        self.requestAbort = False
        
        self.window=Tk()        
        self.window.title("A2P2 v"+ __version__)

        self.notebook = ttk.Notebook(self.window)

        self.logFrame = Frame(self.notebook)
        
        self.logtext = Text(self.logFrame, width=120)
        scroll = Scrollbar(self.logFrame, command=self.logtext.yview)
        self.logtext.configure(yscrollcommand=scroll.set)
        scroll.pack(side=RIGHT, fill=Y)
        self.logtext.pack(side=LEFT, fill=BOTH)
        self.logFrame.pack(fill=BOTH)
        
        self.helpFrame = Frame(self.notebook)        
        self.helptabs = ttk.Notebook(self.helpFrame)        
        self.helptabs.pack(side=TOP,fill=BOTH, expand=True)                
        self.helpFrame.pack(fill=BOTH, expand=True)              
        self.addHelp("A2P2", HELPTEXT)
        
        # add tab and store index for later use in showFacilityUI
        self.tabIdx={}
        self.registerTab("LOG", self.logFrame)
        self.registerTab("HELP", self.helpFrame)
        self.notebook.select(self.tabIdx["LOG"])
        
        
        self.notebook.pack(side=TOP, fill=BOTH, expand=True)

        self.log_string = StringVar()
        self.log_string.set("log...")
        self.log = Label(self.window, textvariable=self.log_string)
        self.log.pack()
        
        self.status_bar = StatusBar(self.window)
        self.status_bar.pack(side=BOTTOM,  fill=X)
        self.progress_value=self.status_bar.progress_value
    
    def __del__(self):
      self.window.destroy()
    
    def addHelp(self, tabname, txt):
        frame = Frame(self.helptabs)
        widget = Text(frame, width=120)        
        helpscroll = Scrollbar(frame, command=widget.yview)
        widget.configure(yscrollcommand=helpscroll.set)
        helpscroll.pack(side=RIGHT, fill=Y)
        widget.pack(side=LEFT, fill=BOTH)
        frame.pack(fill=BOTH)
        self.helptabs.add(frame,text=tabname)                
        widget.insert(END,txt)  

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
             
    def update_status_bar(self):
        self.status_bar.set_label("SAMP","SAMP: %s" % self.a2p2client.a2p2SampClient.get_status())
        self.status_bar.set_label("API","API: %s" % self.a2p2client.apiManager.get_status())

    def get_api(self):
        return self.api

    def addToLog(self,text, displayString=True):
        if displayString:
            self.log_string.set(text)
        self.logtext.insert(END, "\n"+text)
        self.showFrameToFront()
  
    def ShowErrorMessage(self,text):
        dialog = showerror("Error",text)

    def ShowWarningMessage(self,text):
        dialog = showwarning("Warning",text)

    def ShowInfoMessage(self,text):
        dialog = showinfo("Info",text)

    def on_buttonhelp_clicked(self):
         self.ShowInfoMessage(self.helptext.get("1.0",END))

    def setProgress(self,perc):
      self.progress_value.set(perc)
      if ( perc <= 0 ) or ( perc > 0.99 ):
        self.isIdle();
      else:
        self.isBusy();
      self.innerloop()
      self.showFrameToFront()
      
    def showFrameToFront(self):
        self.window.attributes('-topmost', 1)
        self.window.attributes('-topmost', 0)

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
        