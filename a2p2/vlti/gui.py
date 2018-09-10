#!/usr/bin/env python

__all__ = []

import sys
import traceback

from a2p2.gui import FacilityUI

if sys.version_info[0] == 2:
   from Tkinter import *
   from tkMessageBox import *
   import ttk
else:
   from tkinter import *
   from tkinter.messagebox import *
   import tkinter.ttk as ttk

class VltiUI(FacilityUI):

    def __init__(self, a2p2client):
        FacilityUI.__init__(self, a2p2client)
                
        self.container = Frame(self, bd=3, relief=SUNKEN)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.loginFrame=LoginFrame(self)
        self.loginFrame.grid(row=0, column=0, sticky="nsew")        
        
        self.treeFrame=TreeFrame(self)
        self.treeFrame.grid(row=0, column=0, sticky="nsew")
        self.tree = self.treeFrame.tree
               
        self.container.pack(fill=BOTH, expand=True)        
                 
    def showLoginFrame(self, ob):
        self.ob=ob
        self.addToLog("Sorry, your %s OB can't be submitted, please log in first, select container and send OB again from Aspro2."%(ob.instrumentConfiguration.name))
        self.loginFrame.tkraise()
    
    def showTreeFrame(self, ob):
        self.addToLog("Please select a runId in ESO P2 database to process %s OB"%(ob.instrumentConfiguration.name))
        self.treeFrame.tkraise()
        
    def fillTree(self, runs):        
        if len(runs) == 0:
            self.ShowErrorMessage("No Runs defined, impossible to program ESO's P2 interface.")
            return

        for i in range(len(runs)):
            if  self.facility.hasSupportedInsname(runs[i]['instrument']):
                runName=runs[i]['progId']
                instrument=runs[i]['instrument']
                rid=runs[i]['runId']
                cid=runs[i]['containerId']
                self.tree.insert('','end',cid,text=runName,values=(instrument, cid),tags=('run',rid))
                # if folders, add them recursively
                folders=getFolders(self.facility.api,cid)
                if len(folders) > 0 :
                    try:
                        self.folder_explore(folders,cid,instrument,rid)
                    except:
                        pass
                    
    def folder_added(self,name,pid,cid):
        ret=self.tree.item(pid)
        curinst=ret['values'][0]
        tag=ret['tags']
        rid=tag[1]
        self.tree.insert(pid,'end',cid,text=name,values=(curinst,cid),tags=('folder',rid))

    def folder_explore(self,folders,contid,instrument,rid):
        for j in range(len(folders)):
            name=folders[j]['name']
            contid2=folders[j]['containerId']
            self.tree.insert(contid,'end',contid2,text=name,values=(instrument,contid2),tags=('folder',rid))
            folders2=getFolders(self.facility.api,contid2)
            if len(folders2) > 0 :
                try:
                    self.folder_explore(folders2,contid2,instrument,rid)
                except:
                    pass

    def on_tree_selection_changed(self, selection):
        curItem = self.tree.focus()
        ret=self.tree.item(curItem)
        if len(ret['values'])>0:
            curinst=ret['values'][0]
            cid=ret['values'][1]
            curname=ret['text']
            tag=ret['tags']
            rid=tag[1]
            entryType=tag[0]
            # self.flag[0]=1
            # TODO can we remove previous line ?
            if ( entryType == 'folder' ) : #we have a folder
                   new_containerId_same_run=cid
                   folderName = curname
                   self.facility.containerInfo.store_containerId(new_containerId_same_run)
            else:
                instru=curinst
                run, _ = self.facility.api.getRun(rid)
                containerId = run["containerId"]
                self.facility.containerInfo.store(rid, instru, containerId)
    
   
    def isBusy(self):
        self.tree.configure(selectmode='browse')

    def isIdle(self):
        self.tree.configure(selectmode='none') 

class TreeFrame(Frame):
    def __init__(self, vltiUI):                        
        Frame.__init__(self, vltiUI.container)
        self.vltiUI=vltiUI
        
        subframe = Frame(self)
        
        self.tree = ttk.Treeview( subframe,columns=('Project Id'))#, 'instrument'))#, 'folder Id'))
        ysb = ttk.Scrollbar( subframe, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar( subframe, orient='horizontal', command=self.tree.xview)
        
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.heading('#0', text='Project Id', anchor='w')
        self.tree.heading('#1', text='Instrument', anchor='w')
        self.tree.heading('#2', text='folder Id', anchor='w')
        self.tree.bind('<ButtonRelease-1>', self.vltiUI.on_tree_selection_changed)

        # grid layout does not expand and fill all area then move to pack
#       self.tree.grid(row=0, column=0, sticky='nsew')
#       ysb.grid(row=0, column=1, sticky='ns')
#       xsb.grid(row=1, column=0, sticky='ew')
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        ysb.pack(side=RIGHT, fill="y")
        #xsb.pack(side=BOTTOM, fill="y") # will probably require to add another 2 frames
       
        subframe.pack(side=TOP, fill=BOTH, expand=True)
                
class LoginFrame(Frame):
    def __init__(self, vltiUI):                        
        Frame.__init__(self, vltiUI.container)
        self.vltiUI=vltiUI
        
        # TODO Would be better to move such config up
        username = '52052'
        password = 'tutorial'
        self.login = [username, password]        
        
        self.loginframe  = LabelFrame(self, text="login (ESO USER PORTAL or demo account)")

        self.username_label = Label(self.loginframe, text="USERNAME")
        self.username_label.pack()
        self.username = StringVar()
        self.username.set(self.login[0])
        self.username_entry = Entry(self.loginframe,textvariable=self.username)
        self.username_entry.pack()

        self.password_label = Label(self.loginframe, text="PASSWORD")
        self.password_label.pack()
        self.password = StringVar()
        self.password.set(self.login[1])
        self.password_entry = Entry(self.loginframe,textvariable=self.password)
        self.password_entry.pack()
        
        self.loginbutton = Button(self.loginframe,text="LOG IN",command=self.on_loginbutton_clicked)
        self.loginbutton.pack()
        
        self.loginframe.pack()
        self.pack(side=TOP, fill=BOTH,expand=True)
        
                        
    def on_loginbutton_clicked(self):
        self.vltiUI.facility.connectAPI(self.username.get(),  self.password.get(), self.vltiUI.ob)
       
       

# TODO move into a common part
def getFolders(p2api, containerId):
    folders = []
    itemList, _ = p2api.getItems(containerId)
    for i in range(len(itemList)):
        if itemList[i]['itemType'] == 'Folder':
            folders.append(itemList[i])
    return folders