#!/usr/bin/env python

__all__ = []

from a2p2.chara.gui import CharaUI
from a2p2.facility import Facility
import requests
import logging
import traceback

HELPTEXT = "TODO update this HELP message in a2p2/chara/facility.py"

logger = logging.getLogger(__name__)

class CharaFacility(Facility):

    def __init__(self, a2p2client):
        Facility.__init__(self, a2p2client, "CHARA", HELPTEXT)
        self.charaUI = CharaUI(self)
        self.connected2OB2 = False

    def processOB(self, ob):
        if not ob:
            return

        self.a2p2client.ui.addToLog(
            "OB received for '" + self.facilityName + "' interferometer")
        # show ob dict for debug
        self.a2p2client.ui.addToLog(str(ob), False)

        # performs operation
        self.consumeOB(ob)

        # give focus on last updated UI
        self.a2p2client.ui.showFacilityUI(self.charaUI)

    def consumeOB(self, ob):
        # forward message if a server is present in the preferences
        charaServer=self.a2p2client.preferences.getCharaQueueServer()
        if charaServer :
            try:
                r = requests.post(charaServer, json=ob.as_dict())
                msg = ""
                if not self.connected2OB2:
                    try:
                        c=requests.get(charaServer)
                        msg += f"Connection succeeded on OB2 server : {c.json()}\n"
                    except:
                        msg += f"Connection succeded on a non identified OB2 server\n"
                msg+=f"OB sent to remote server queue : {r}"
                self.connected2OB2 = True
            except:
                print(traceback.format_exc())
                msg=f"Can't send OB to remote server queue, please check access to server {charaServer}"
                self.connected2OB2 = False

            self.a2p2client.ui.addToLog(msg)
            self.charaUI.display(msg)

        # display OB
        self.charaUI.displayOB(ob)


