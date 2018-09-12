#!/usr/bin/env python

__all__ = []

import os
from a2p2.facility import Facility
from a2p2.instrument import Instrument

from a2p2.vlti.gui import VltiUI

import traceback


# TODO handle a period subdirectory
CONFDIR="conf"

# Look for configuration files in the same level directory as this module/conf/
try:
    _confdir = os.path.join(os.path.dirname(__file__), CONFDIR)
except NameError:
    _confdir = CONFDIR
if os.path.isdir(_confdir):
    CONFDIR = _confdir
elif not os.path.isdir(CONFDIR):
    raise RuntimeError ( "can't find conf directory (%r)" % (CONFDIR,))

HELPTEXT="""
ESO's P2 repository for Observing Blocks (OBs):


Send configuration from Aspro:
- In ASPRO, have an object, or an object selected, and check that all important informations (magnitudes, but also Instrument and Fringe Tracker Modes, eventually hour angles), are correctly set.
- In menu "Interop" select "Send Obs. blocks to A2p2"
- Block(s) are created and put in the P2 repository.
- If the source had one or more calibrators, blocks are created for them too.
- For each block submitted, a report is produced. Warnings are usually not significant.
- For more than 1 object sent, a <b>folder</b> containing the two or more blocks is created. In the absence of availability of grouping OBs (like for CAL-SCI-CAL) provided by ESO, this is the closets we can do.
- All the new OBs and folders will be available on p2web at https://www.eso.org/p2 

On your first valid VLTI's OB, A2p2 will ask for your ESO User Portal credentials to interact with P2 using it's API. You can follow actions and organize more in details your OB on https://www.eso.org/p2 . Please use prefilled values of the login panel for testing purpose and follow ESO database from https://www.eso.org/p2demo/
"""
HELPTEXT+="Config files loaded from "+CONFDIR

class VltiFacility(Facility):

    def __init__(self, a2p2client):
        Facility.__init__(self, a2p2client, "VLTI", HELPTEXT)
        self.ui = VltiUI(self)
        
        # Instanciate instruments
        # TODO complete list and make it more object oriented
        from a2p2.vlti.gravity import Gravity
        gravity = Gravity(self)
        # self.supportedInstrumentsByAspro = ['GRAVITY', 'MATISSE', 'AMBER', 'PIONIER']
        
        # complete help 
        for i in self.getSupportedInstruments():
            self.facilityHelp += "\n"+i.getHelp()
        
        self.connected = False
        self.containerInfo = P2Container(self)        
        
        # will store later : name for status info, api 
        self.username = None
        self.api = None   
        
    def processOB(self, ob):
        # give focus on last updated UI
        self.a2p2client.ui.showFacilityUI(self.ui)
        # show ob dict for debug
        self.ui.addToLog(str(ob), False)
        
        # OB is checked and submitted by instrument             
        instrument = self.getInstrument(ob.instrumentConfiguration.name)
        try:            
            # run checkOB which may raise some error before connection request
            instrument.checkOB(ob, self.containerInfo)            

            # performs operation
            if not self.isConnected():
                self.ui.showLoginFrame(ob)
            elif not self.isReadyToSubmit():
                 #self.a2p2client.ui.addToLog("Receive OB for '"+ob.instrumentConfiguration.name+"'")
                self.ui.addToLog("Please select a Project Id or Folder in the above list. OBs are not shown")
            else:
                self.ui.addToLog("everything ready! process OB for selected container")            
                instrument.submitOB(ob,self.containerInfo)
                
        # TODO add P2Error handling P2Error(r.status_code, method, url, r.json()['error'])
        except ValueError as e:
            traceback.print_exc()
            trace = traceback.format_exc(limit=1)
#            ui.ShowErrorMessage("Value error :\n %s \n%s\n\n%s" % (e, trace, "Aborting submission to P2. Look at the whole traceback in the log."))
            self.ui.ShowErrorMessage("Value error :\n %s \n\n%s" % (e, "Aborting submission to P2. Please check LOG and fix before new submission."))
            trace = traceback.format_exc()
            self.ui.addToLog(trace, False)
            self.ui.setProgress(0)
        except Exception as e:
            traceback.print_exc()
            trace = traceback.format_exc(limit=1) # limit = 2 should raise errors in our codes 
            self.ui.ShowErrorMessage("General error or Absent Parameter in template!\n Missing magnitude or OB not set ?\n\nError :\n %s \n Please check LOG and fix before new submission." % (trace))
            trace = traceback.format_exc()
            self.ui.addToLog(trace, False)
            self.ui.setProgress(0)
        
    def isReadyToSubmit(self):
        return self.api and self.containerInfo.isOk()

    def isConnected(self):
        return self.connected
    
    def setConnected(self, flag):
        self.connected=flag

    def getStatus(self):
        if self.isConnected():
            return " P2API connected with "+self.username
        
    def connectAPI(self, username, password, ob):
        import p2api
        if username == '52052':
            type = 'demo'
        else:
            type = 'production'
        try:
            self.api = p2api.ApiConnection(type, username, password)
            # TODO test that api is ok and handle error if any...

            runs, _ = self.api.getRuns()
            self.ui.fillTree(runs)

            self.setConnected(True)
            self.username=username
            self.ui.showTreeFrame(ob)
        except:
            self.ui.addToLog("Can't connect to P2 (see LOG).")
            trace = traceback.format_exc()
            self.ui.addToLog(trace, False)
            
    def getAPI(self):
        return self.api
    
    def getConfDir(self):
        """ 
        returns the configuration directory with instrument's json files 
        """
        return CONFDIR
        
# TODO Move code out of this class        
class P2Container:
    # TODO add runName field so we can show information instead of numeric projectId
    def __init__(self, facility):
        self.facility = facility
        self.projectId = None
        # TODO check projectId because it is not used ?
        self.instrument = None
        self.containerId = None

    def store (self, projectId, instrument, containerId):
        self.projectId = projectId
        self.instrument = instrument
        self.containerId = containerId
        self.log()

    def store_containerId (self, containerId):
        self.containerId = containerId
        self.log()
    
    def log(self):
        self.facility.ui.addToLog("*** Working with %s ***" % self)

    def isOk(self):
        return (self.projectId != None)

    def __str__(self):
#        return """projectId:'%s', instrument:'%s', containerId:'%s'""" % (self.projectId, self.instrument, self.containerId)
        return """instrument:'%s', containerId:'%s'""" % (self.instrument, self.containerId)
