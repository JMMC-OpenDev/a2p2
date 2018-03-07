#!/usr/bin/env python

__all__ = ['A2p2Client']


from a2p2.apis import APIManager
from a2p2.gui import GtkWindow
from a2p2.gui import TextWindow
from a2p2.samp import A2p2SampClient
from a2p2.utils import parseXmlMessage
import logging
import sys
import time

logLevel = logging.ERROR

class A2p2Client():
    """Transmit your Aspro2 observation to remote Observatory scheduling database.

       with A2p2Client() as a2p2:
           a2p2.run()
           ..."""
    def __init__(self, fakeAPI=False):
        """Create the A2p2 client."""
        logger = logging.getLogger()
        logger.setLevel(logLevel)
    #        logging.basicConfig(level=logging.DEBUG,
    #                            format=('%(filename)s: '
    #                            '%(levelname)s: '
    #                            '%(funcName)s(): '
    #                            '%(lineno)d:\t'
    #                            '%(message)s')
    #                            )

        # finish logging

        self.username = None
        self.apiName = None
        if fakeAPI:
            self.apiName = "fakeAPI"

        pass

    def __enter__(self):
        """Handle starting the 'with' statements."""
        # Instantiate the samp client and connect to the hub later
        self.a2p2SampClient = A2p2SampClient()

        # Instantiate a UI
        try:
            self.ui = GtkWindow(self)
        except:
            self.ui = TextWindow(self)

        self.apiManager = APIManager(self.apiName, self.ui)

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
        if isinstance(self.ui, TextWindow):
            each = 1
        else:
            each = 10
        loop_cnt = 0

        while loop_cnt >= 0:
            try:
                loop_cnt += 1
                time.sleep(delay)

                self.ui.loop()

                if not self.a2p2SampClient.is_connected() and loop_cnt % each == 0:
                    loop_cnt = 0
                    try:
                        self.a2p2SampClient.connect()
                    except:
                        logging.debug("except %s", sys.exc_info())
                        pass # TODO raise other exception excepted

                if self.a2p2SampClient.has_message(): # TODO implement a stack for received messages
                    if not self.ui.is_connected():
                        logging.debug("samp message received and api not connected")
                        self.ui.ShowErrorMessage('a2p2 is not currently connected with ESO P2 database.')
                    elif not self.ui.is_ready_to_submit():
                        self.ui.ShowErrorMessage('Please select a runId ESO P2 database.')
                        logging.debug("samp message received and api not ready to transmit")
                    else:
                        self.ui.addToLog('Sending request to API ...')
                        logging.debug("samp message received and api ready to transmit")
                        ob_url = self.a2p2SampClient.get_ob_url()
                        parseXmlMessage(self, ob_url, self.ui.get_containerInfo())
                    # always clear previous received message
                    self.a2p2SampClient.clear_message()

                if self.ui.requestAbort:
                    loop_cnt = -1
            except KeyboardInterrupt:
                loop_cnt = -1

