#!/usr/bin/env python

__all__ = []

# Constants
_HR="\n---------------------------------------------------------------------------\n"


# TODO rename FacilitiesManager
class APIManager():
    """
    Manage real and fake apis.
    """
    
    def __init__(self, a2p2client):
        self.apiName = a2p2client.apiName
        self.a2p2client = a2p2client

        self.api = None
        
        # define facilities
        self.facilities= {}
        from a2p2.chara.facility import CharaFacility
        self.registerFacility(CharaFacility(self.a2p2client))
        # and default one
        self.defaultFacility = Facility(self.a2p2client, "Dumm-facilit-y")
        
    
    def registerFacility(self, facilityObject ):
        self.facilities[facilityObject.facilityName]=facilityObject        
        
    def connect(self, username=None, password=None):
        """ Return an API to interact with remote observation proposals"""
        # At present time only ESO P2 API is available for real use

        # api is None if fake one has not been requested by option
        # TODO add logging  instead of self.ui.ShowInfoMessage("create API for %s" % self.apiName)
        if self.apiName:
            self.api = FakeAPI(username, password, self.a2p2client.ui)
        else:
            import p2api
            if username == '52052':
                type = 'demo'
            else:
                type = 'production'
            self.api = p2api.ApiConnection(type, username, password)

        return self.api

    def getAPI(self):
        return self.api

    def is_connected(self):
        return self.api != None

    def get_status(self):
        if self.api:
            return self.apiName+" connected"
        else:
            return self.apiName+" not connected"

    def processOB(self, ob): 
        interferometer=ob.interferometerConfiguration.name
        self.a2p2client.ui.addToLog("Received OB for the '"+interferometer+"' interferometer ")                
    
        if interferometer in self.facilities:        
            facility = self.facilities[interferometer]
        else:
            facility = self.defaultFacility
        
        facility.processOB(ob)
        
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



    # TODO move into eso side
    def getSupportedInstruments(self):
        if self.apiName:
            return ["dummy"]
        else:
            return ["GRAVITY"]

class Facility():
    
    def __init__(self, a2p2client, facilityName):
        self.a2p2client=a2p2client
        self.facilityName=facilityName
    
    def processOB(self, ob):
        interferometer =  ob.interferometerConfiguration.name
        self.a2p2client.ui.addToLog("'"+interferometer+"' interferometer not supported by A2P2")

class FakeAPI():
    """
    Fake API dedicated for testing
    """
    def __init__(self, username, password, ui):
        self.username = username
        self.password = password
        self.ui = ui

    def getRuns(self):
        self.ui.addToLog("FakeAPI.getRuns")
        return [[{u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'VLTI', u'title': u'Tutorial run for GRAVITY', u'scheduledPeriod': 60, u'period': 60, u'owned': True, u'ipVersion': 101.07, u'instrument': u'GRAVITY', u'containerId': 1595854, u'observingConstraints': {u'seeing': 2.0}, u'mode': u'SM', u'progId': u'060.A-9252(M)', u'itemCount': 8, u'delegated': False, u'runId': 60925212}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'NTT', u'title': u'P2PP Tutorial', u'scheduledPeriod': 60, u'period': 60, u'owned': True, u'ipVersion': 301.13, u'instrument': u'SUSI2', u'containerId': 1607245, u'observingConstraints': {u'seeing': 1.0}, u'mode': u'SM', u'progId': u'60.A-9252(B)', u'itemCount': 0, u'delegated': False, u'runId': 60925201}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'NTT', u'title': u'P2PP Tutorial', u'scheduledPeriod': 60, u'period': 60, u'owned': True, u'ipVersion': 89.01, u'instrument': u'SOFI', u'containerId': 1596509, u'observingConstraints': {u'seeing': 1.0}, u'mode': u'SM', u'progId': u'60.A-9252(C)', u'itemCount': 0, u'delegated': False, u'runId': 60925202}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'UT1', u'title': u'P2PP Tutorial', u'scheduledPeriod': 60, u'period': 60, u'owned': True, u'ipVersion': 136.88, u'instrument': u'FORS1', u'containerId': 1599843, u'observingConstraints': {u'fli': u'n', u'seeing': 2.0, u'skyTransparency': u'Photometric'}, u'mode': u'SM', u'progId': u'60.A-9252(D)', u'itemCount': 0, u'delegated': False, u'runId': 6092523}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'UT3', u'title': u'P2PP Tutorial', u'scheduledPeriod': 60, u'period': 60, u'owned': True, u'ipVersion': 92.06, u'instrument': u'ISAAC', u'containerId': 1512192, u'observingConstraints': {u'fli': u'n', u'seeing': 2.0, u'skyTransparency': u'Photometric'}, u'mode': u'SM', u'progId': u'60.A-9252(E)', u'itemCount': 8, u'delegated': False, u'runId': 6092524}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'UT1', u'title': u'P2PP Tutorial', u'scheduledPeriod': 60, u'period': 60, u'owned': True, u'ipVersion': 101.04, u'instrument': u'FORS2', u'containerId': 1448455, u'observingConstraints': {u'fli': u'n', u'seeing': 2.0, u'skyTransparency': u'Photometric'}, u'mode': u'SM', u'progId': u'60.A-9252(F)', u'itemCount': 5, u'delegated': False, u'runId': 6092525}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'UT2', u'title': u'P2PP Tutorial', u'scheduledPeriod': 60, u'period': 60, u'owned': True, u'ipVersion': 101.05, u'instrument': u'UVES', u'containerId': 1538878, u'observingConstraints': {u'fli': u'n', u'seeing': 2.0, u'skyTransparency': u'Photometric'}, u'mode': u'SM', u'progId': u'60.A-9252(G)', u'itemCount': 15, u'delegated': False, u'runId': 6092526}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'UT1', u'title': u'P2PP Tutorial', u'scheduledPeriod': 60, u'period': 60, u'owned': True, u'ipVersion': 101.05, u'instrument': u'NACO', u'containerId': 1593348, u'observingConstraints': {u'seeing': 1.0}, u'mode': u'SM', u'progId': u'60.A-9252(H)', u'itemCount': 3, u'delegated': False, u'runId': 60925207}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'UT2', u'title': u'P2PP Tutorial', u'scheduledPeriod': 60, u'period': 60, u'owned': True, u'ipVersion': 101.04, u'instrument': u'FLAMES', u'containerId': 1563314, u'observingConstraints': {u'seeing': 1.0}, u'mode': u'SM', u'progId': u'60.A-9252(I)', u'itemCount': 5, u'delegated': False, u'runId': 60925208}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'UT3', u'title': u'P2PP Tutorial', u'scheduledPeriod': 60, u'period': 60, u'owned': True, u'ipVersion': 100.03, u'instrument': u'VIMOS', u'containerId': 1607844, u'observingConstraints': {u'seeing': 1.0}, u'mode': u'SM', u'progId': u'60.A-9252(J)', u'itemCount': 2, u'delegated': False, u'runId': 60925209}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'2.2', u'title': u'P2PP Tutorial', u'scheduledPeriod': 60, u'period': 60, u'owned': True, u'ipVersion': 89.01, u'instrument': u'WFI', u'containerId': 1587490, u'observingConstraints': {u'seeing': 1.0}, u'mode': u'SM', u'progId': u'60.A-9252(K)', u'itemCount': 0, u'delegated': False, u'runId': 60925210}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'VST', u'title': u'P2PP tutorial account for OmegaCAM', u'scheduledPeriod': 60, u'period': 60, u'owned': True, u'ipVersion': 101.03, u'instrument': u'OMEGACAM', u'containerId': 1455705, u'observingConstraints': {u'seeing': 1.0}, u'mode': u'SM', u'progId': u'60.A-9252(L)', u'itemCount': 4, u'delegated': False, u'runId': 60925211}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'3.6', u'title': u'P2PP Tutorial', u'scheduledPeriod': 60, u'period': None, u'owned': True, u'ipVersion': 203.13, u'instrument': u'CES3.6', u'containerId': 1594176, u'observingConstraints': {u'seeing': 1.0}, u'mode': u'SM', u'progId': u'60.A-9253(A)', u'itemCount': 0, u'delegated': False, u'runId': 60925300}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'3.6', u'title': u'P2PP Tutorial', u'scheduledPeriod': 60, u'period': None, u'owned': True, u'ipVersion': 93.01, u'instrument': u'EFOSC2', u'containerId': 1588827, u'observingConstraints': {u'seeing': 1.0}, u'mode': u'SM', u'progId': u'60.A-9253(B)', u'itemCount': 0, u'delegated': False, u'runId': 60925301}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'3.6', u'title': u'P2PP Tutorial', u'scheduledPeriod': 60, u'period': None, u'owned': True, u'ipVersion': 126.13, u'instrument': u'TIMMI2', u'containerId': 1592142, u'observingConstraints': {u'seeing': 1.0}, u'mode': u'SM', u'progId': u'60.A-9253(C)', u'itemCount': 0, u'delegated': False, u'runId': 60925302}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'3.6', u'title': u'P2PP Tutorial', u'scheduledPeriod': 60, u'period': None, u'owned': True, u'ipVersion': 213.19, u'instrument': u'EMMI', u'containerId': 1605095, u'observingConstraints': {u'seeing': 1.0}, u'mode': u'SM', u'progId': u'60.A-9253(D)', u'itemCount': 0, u'delegated': False, u'runId': 60925303}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'VLTI', u'title': u'P2PP tutorial', u'scheduledPeriod': 60, u'period': None, u'owned': True, u'ipVersion': 94.01, u'instrument': u'MIDI', u'containerId': 1475401, u'observingConstraints': {u'seeing': 2.0}, u'mode': u'SM', u'progId': u'60.A-9253(E)', u'itemCount': 2, u'delegated': False, u'runId': 60925304}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'2.2', u'title': u'P2PP tutorial account', u'scheduledPeriod': 60, u'period': None, u'owned': True, u'ipVersion': 89.01, u'instrument': u'FEROS', u'containerId': 1605754, u'observingConstraints': {u'seeing': 1.0}, u'mode': u'SM', u'progId': u'60.A-9253(F)', u'itemCount': 0, u'delegated': False, u'runId': 60925305}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'3.6', u'title': u'P2PP tutorial account', u'scheduledPeriod': 60, u'period': None, u'owned': True, u'ipVersion': 89.01, u'instrument': u'HARPS', u'containerId': 1603695, u'observingConstraints': {u'seeing': 1.0}, u'mode': u'SM', u'progId': u'60.A-9253(G)', u'itemCount': 0, u'delegated': False, u'runId': 60925306}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'UT4', u'title': u'P2PP tutorial', u'scheduledPeriod': 60, u'period': None, u'owned': True, u'ipVersion': 101.05, u'instrument': u'SINFONI', u'containerId': 1515532, u'observingConstraints': {u'seeing': 1.0}, u'mode': u'SM', u'progId': u'60.A-9253(H)', u'itemCount': 13, u'delegated': False, u'runId': 60925307}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'UT3', u'title': u'P2PP tutorial', u'scheduledPeriod': 60, u'period': None, u'owned': True, u'ipVersion': 101.05, u'instrument': u'VISIR', u'containerId': 1469770, u'observingConstraints': {u'seeing': 1.0}, u'mode': u'SM', u'progId': u'60.A-9253(I)', u'itemCount': 4, u'delegated': False, u'runId': 60925308}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'VLTI', u'title': u'P2PP tutorial', u'scheduledPeriod': 60, u'period': None, u'owned': True, u'ipVersion': 101.04, u'instrument': u'AMBER', u'containerId': 1607251, u'observingConstraints': {u'seeing': 1.0}, u'mode': u'SM', u'progId': u'60.A-9253(J)', u'itemCount': 0, u'delegated': False, u'runId': 60925309}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'UT1', u'title': u'P2PP tutorial', u'scheduledPeriod': 60, u'period': None, u'owned': True, u'ipVersion': 93.01, u'instrument': u'CRIRES', u'containerId': 1608672, u'observingConstraints': {u'seeing': 1.0}, u'mode': u'SM', u'progId': u'60.A-9253(K)', u'itemCount': 0, u'delegated': False, u'runId': 60925310}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'UT4', u'title': u'P2PP tutorial', u'scheduledPeriod': 60, u'period': 60, u'owned': True, u'ipVersion': 101.06, u'instrument': u'HAWKI', u'containerId': 1602325, u'observingConstraints': {u'seeing': 2.0}, u'mode': u'SM', u'progId': u'60.A-9253(L)', u'itemCount': 1, u'delegated': False, u'runId': 60925311}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'2.2', u'title': u'P2PP tutorial account', u'scheduledPeriod': 60, u'period': 60, u'owned': True, u'ipVersion': 102.0, u'instrument': u'GROND', u'containerId': 1590788, u'observingConstraints': {u'seeing': 2.0}, u'mode': u'SM', u'progId': u'60.A-9253(M)', u'itemCount': 1, u'delegated': False, u'runId': 60925312}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'VISTA', u'title': u'P2PP Tutorial', u'scheduledPeriod': 60, u'period': 60, u'owned': True, u'ipVersion': 101.03, u'instrument': u'VIRCAM', u'containerId': 1546825, u'observingConstraints': {u'seeing': 1.0}, u'mode': u'SM', u'progId': u'60.A-9253(N)', u'itemCount': 3, u'delegated': False, u'runId': 60925313}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'UT2', u'title': u'P2PP tutorial account for XSHOOTER', u'scheduledPeriod': 60, u'period': 60, u'owned': True, u'ipVersion': 101.02, u'instrument': u'XSHOOTER', u'containerId': 1465409, u'observingConstraints': {u'seeing': 1.0}, u'mode': u'SM', u'progId': u'60.A-9253(P)', u'itemCount': 7, u'delegated': False, u'runId': 60925315}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'UT1', u'title': u'P2PP tutorial account for KMOS', u'scheduledPeriod': 60, u'period': 60, u'owned': True, u'ipVersion': 101.04, u'instrument': u'KMOS', u'containerId': 1593162, u'observingConstraints': {u'seeing': 1.0}, u'mode': u'SM', u'progId': u'60.A-9253(Q)', u'itemCount': 1, u'delegated': False, u'runId': 60925316}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'UT4', u'title': u'P2PP Tutorial', u'scheduledPeriod': 60, u'period': 60, u'owned': True, u'ipVersion': 101.05, u'instrument': u'MUSE', u'containerId': 1483498, u'observingConstraints': {u'seeing': 1.0}, u'mode': u'SM', u'progId': u'60.A-9253(R)', u'itemCount': 14, u'delegated': False, u'runId': 60925317}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'UT3', u'title': u'P2PP Tutorial', u'scheduledPeriod': 60, u'period': 60, u'owned': True, u'ipVersion': 101.09, u'instrument': u'SPHERE', u'containerId': 1604213, u'observingConstraints': {u'seeing': 1.4}, u'mode': u'SM', u'progId': u'60.A-9253(S)', u'itemCount': 2, u'delegated': False, u'runId': 60925318}, {u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'VLTI', u'title': u'Tutorial run for PIONIER', u'scheduledPeriod': 60, u'period': 60, u'owned': True, u'ipVersion': 101.08, u'instrument': u'PIONIER', u'containerId': 1601182, u'observingConstraints': {u'seeing': 1.0}, u'mode': u'SM', u'progId': u'60.A-9253(T)', u'itemCount': 3, u'delegated': False, u'runId': 60925319}], "blanking"]

    def getItems(self, containerId):
        self.ui.addToLog("FakeAPI.getItems(%s)" % containerId)
        return [[{u'obStatus': u'P', u'obId': 1859094, u'name': u'SCI_GX_Mon_GRAVITY_A0G1J2J3_LOW-SPLIT', u'runId': 60925212, u'userPriority': 1, u'parentContainerId': 1595854, u'itemType': u'OB'}, {u'itemType': u'Folder', u'name': u'New Folder', u'containerId': 1859111, u'runId': 60925212, u'itemCount': 2, u'parentContainerId': 1595854}, {u'obStatus': u'P', u'obId': 1860040, u'name': u'SCI_NX_Pup_GRAVITY_UT1UT2UT3UT4_HIGH-COMBINED', u'runId': 60925212, u'userPriority': 1, u'parentContainerId': 1595854, u'itemType': u'OB'}, {u'obStatus': u'P', u'obId': 1860075, u'name': u'CAL_HD_183936_GRAVITY_UT1UT2UT3UT4_HIGH-COMBINED', u'runId': 60925212, u'userPriority': 1, u'parentContainerId': 1595854, u'itemType': u'OB'}, {u'itemType': u'Folder', u'name': u'HD_190073', u'containerId': 1860078, u'runId': 60925212, u'itemCount': 1, u'parentContainerId': 1595854}, {u'obStatus': u'P', u'obId': 1860083, u'name': u'SCI_WW_Vul_GRAVITY_UT1UT2UT3UT4_HIGH-COMBINED', u'runId': 60925212, u'userPriority': 1, u'parentContainerId': 1595854, u'itemType': u'OB'}, {u'obStatus': u'P', u'obId': 1860086, u'name': u'SCI_WW_Vul_GRAVITY_UT1UT2UT3UT4_HIGH-COMBINED', u'runId': 60925212, u'userPriority': 1, u'parentContainerId': 1595854, u'itemType': u'OB'}, {u'obStatus': u'P', u'obId': 1861125, u'name': u'SCI_WD1-9', u'runId': 60925212, u'userPriority': 1, u'parentContainerId': 1595854, u'itemType': u'OB'}], None]

    def getRun(self, runId):
        self.ui.addToLog("FakeAPI.getRun(%s)" % runId)
        return [{u'pi': {u'lastName': u'P2PP tutorial account', u'emailAddress': u'52052@nodomain.net', u'firstName': u'P2PP'}, u'telescope': u'VLTI', u'title': u'Tutorial run for GRAVITY', u'scheduledPeriod': 60, u'period': 60, u'owned': True, u'ipVersion': 101.07, u'instrument': u'GRAVITY', u'containerId': 1595854, u'observingConstraints': {u'seeing': 2.0}, u'mode': u'SM', u'progId': u'060.A-9252(M)', u'itemCount': 8, u'delegated': False, u'runId': 60925212}, None]

    def createFolder(self, containerId, folderName):
        self.ui.addToLog("FakeAPI.createFolder(%s,%s)" % (containerId, folderName))

    # TO BE COMPLETED

