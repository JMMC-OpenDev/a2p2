#!/usr/bin/env python

__all__ = ['A2p2Client']

from a2p2.facility import FacilityManager
from a2p2.gui import MainWindow
from a2p2.samp import A2p2SampClient
from a2p2.ob import OB
from a2p2 import __version__
import sys
import time
import traceback

class A2p2Client():
    """Transmit your Aspro2 observation to remote Observatory scheduling database.

       with A2p2Client() as a2p2:
           a2p2.run()
           ..."""
    def __init__(self, fakeAPI=False):
        """Create the A2p2 client."""
        
        self.username = None
        self.apiName = ""
        if fakeAPI:
            self.apiName = "fakeAPI"

        self.ui = MainWindow(self)
        # Instantiate the samp client and connect to the hub later
        self.a2p2SampClient = A2p2SampClient()       
        self.facilityManager = FacilityManager(self)        
            

        pass

    def __enter__(self):
        """Handle starting the 'with' statements."""
        
        self.ui.addToLog("Welcome in the A2P2 V" + __version__)
        
        return self

    def __del__(self):
        """Handle deleting the object."""
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        """Handle closing the 'with' statement."""
        del self.a2p2SampClient
        del self.ui
        # TODO close the connection to the obs database ?

        # WARNING do not return self only. Else exceptions are hidden
        # return self

    def __str__(self):
        instruments     = "\n- ".join(["Supported instruments:", "TBD"])
        apis       = "\n- ".join(["Supported APIs:", "TBD"])
        return """a2p2 client\n%s\n%s\n""" % (instruments, apis)

    def changeSampStatus(self, connected_flag):
        self.sampConnected = connected_flag

    def setUsername(self, username):
        self.username = username

    def getUsername(self):
        if not self.username:
            import getpass
            self.username = getpass.getuser()
        return self.username

    def setProgress(self, perc, actionName=None):
        if actionName:
            print ("%s action progress is  %s" % (actionName, perc))
        else:
            print ("progress is  %s %%" % (perc))
        
    def run(self):
        # bool of status change
        flag = [0]

        # We now run the loop to wait for the message in a try/finally block so that if
        # the program is interrupted e.g. by control-C, the client terminates
        # gracefully.

        # We test every 1s to see if the hub has sent a message
        delay = 0.1
        each = 10
        loop_cnt = 0
        warnForAspro=True

        while loop_cnt >= 0:
            try:
                loop_cnt += 1
                time.sleep(delay)

                self.ui.loop()

                if not self.a2p2SampClient.is_connected() and loop_cnt % each == 0:                    
                    try:
                        self.a2p2SampClient.connect()
                        self.ui.setSampId(self.a2p2SampClient.get_public_id())                        
                    except:
                        self.ui.setSampId(None)
                        if warnForAspro:
                            warnForAspro=False
                            self.ui.addToLog("\nPlease launch Aspro2 to submit your OBs.")
                        pass # TODO test for other exception than SAMPHubError(u'Unable to find a running SAMP Hub.',)

                if self.a2p2SampClient.has_message():                    
                    try:                        
                        ob = OB(self.a2p2SampClient.get_ob_url())
                        self.facilityManager.processOB(ob)
                    except:                        
                        self.ui.addToLog("Exception during ob creation: "+traceback.format_exc(), False)
                        self.ui.addToLog("Can't process last OB")
                    
                    
                    # always clear previous received message
                    self.a2p2SampClient.clear_message()
                    
                if self.ui.requestAbort:
                    loop_cnt = -1
            except KeyboardInterrupt:
                loop_cnt = -1

