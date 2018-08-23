#!/usr/bin/env python

__all__ = []

from a2p2.apis import Facility
from a2p2.vlti.gui import VltiUI

HELPTEXT="""
ESO's P2 repository for Observing Blocks (OBs):

Login:
You must log in to the ESO User Portal using your identifiers to access the P2 repository. Please check on the ESO website in case of doubt.

Select Run ID:
After successful login, you are presented with the Runs compatible with Aspro's known instruments. Select the Run, and eventually the subfolder of this Run, where you want to create the OB. Each Run corresponds to a specific instrument. This instrument must be the same as the one selected in ASPRO.

Send configuration from Aspro:
- In ASPRO, have an object, or an object selected, and check that all important informations (magnitudes, but also Instrument and Fringe Tracker Modes, eventually hour angles), are correctly set.
- In menu "Interop" select "Send Obs. blocks to A2p2"
- Block(s) are created and put in the P2 repository.
- If the source had one or more calibrators, blocks are created for them too.
- For each block submitted, a report is produced. Warnings are usually not significant.
- For more than 1 object sent, a <b>folder</b> containing the two or more blocks is created. In the absence of availability of grouping OBs (like for CAL-SCI-CAL) provided by ESO, this is the closets we can do.
- All the new OBs and folders will be available on p2web at https://eso.org/p2 
"""

class VltiFacility(Facility):

    def __init__(self, a2p2client):
        Facility.__init__(self, a2p2client, "VLTI", HELPTEXT)
        self.vltiUI = VltiUI(self)
        
        # TODO complete list and make it more object oriented
        self.registerInstrument("GRAVITY")
        # self.supportedInstrumentsByAspro = ['GRAVITY', 'MATISSE', 'AMBER', 'PIONIER']
        
        self.connected = False
        self.containerInfo = P2Container(self)        
        
        # will store later : name for status info, api 
        self.username = None
        self.api = None   
        
    def processOB(self, ob):
        # show ob dict for debug
        self.vltiUI.addToLog(str(ob), False)
        
        # performs operation
        self.consumeOB(ob)
        
        # give focus on last updated UI
        self.a2p2client.ui.showFacilityUI(self.vltiUI)
        
        
    def consumeOB(self, ob):
        if not self.isConnected():
            self.vltiUI.showLoginFrame(ob)
        elif not self.isReadyToSubmit():
             #self.a2p2client.ui.addToLog("Receive OB for '"+ob.instrumentConfiguration.name+"'")
            self.vltiUI.addToLog("Please select a Project Id or Folder in the above list. OBs are not shown")
        else:
            self.vltiUI.addToLog("everything ready! TODO process OB for selected container")
        
#        if not self.ui.is_connected():
#            logging.debug("samp message received and api not connected")
#            self.ui.ShowErrorMessage('a2p2 is not currently connected with ESO P2 database.')
#        elif not self.ui.is_ready_to_submit():
#            self.ui.ShowErrorMessage('Please select a runId ESO P2 database.')
#            logging.debug("samp message received and api not ready to transmit")
#        else:
#            self.ui.addToLog('Sending request to API ...')
#            logging.debug("samp message received and api ready to transmit")
#            
#            parseXmlMessage(self, ob_url, self.ui.get_containerInfo())

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
        self.api = p2api.ApiConnection(type, username, password)
        # TODO test that api is ok and handle error if any...
        
        runs, _ = self.api.getRuns()
        self.vltiUI.fillTree(runs)

        self.setConnected(True)
        self.username=username
        self.vltiUI.showTreeFrame(ob)
        pass

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
        self.facility.vltiUI.addToLog("*** Working with %s ***" % self)

    def isOk(self):
        return (self.projectId != None)

    def __str__(self):
#        return """projectId:'%s', instrument:'%s', containerId:'%s'""" % (self.projectId, self.instrument, self.containerId)
        return """instrument:'%s', containerId:'%s'""" % (self.instrument, self.containerId)
