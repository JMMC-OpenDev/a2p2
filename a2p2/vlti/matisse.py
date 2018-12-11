#!/usr/bin/env python

__all__ = []

from a2p2.instrument import Instrument
from a2p2.vlti.gui import VltiUI
from a2p2.vlti.instrument import VltiInstrument
from a2p2.vlti.instrument import TSF
from a2p2.vlti.instrument import OBConstraints
from a2p2.vlti.instrument import OBTarget

from astropy.coordinates import SkyCoord
import cgi
import numpy as np
import re
import datetime

HELPTEXT = """
Please define PIONIER instrument help in a2p2/vlti/pionier.py
"""


class Matisse(VltiInstrument):

    def __init__(self, facility):
        VltiInstrument.__init__(self, facility, "MATISSE")

    # mainly corresponds to a refactoring of old utils.processXmlMessage
    def checkOB(self, ob, p2container, dryMode=True):
        api = self.facility.getAPI()
        ui = self.ui
        containerId = p2container.containerId

        instrumentConfiguration = ob.instrumentConfiguration
        BASELINE = ob.interferometerConfiguration.stations
        # Compute tel = UT or AT
        # TODO move code into common part
        if "U" in BASELINE:
            tel = "UT"
        else:
            tel = "AT"

        instrumentMode = instrumentConfiguration.instrumentMode

        # Retrieve SPEC and POL info from instrumentMode
        for disp in self.getRange("PIONIER_acq.tsf", "INS.DISP.NAME"):
            if disp in instrumentMode[0:len(disp)]:
                ins_disp = disp

        # if we have more than 1 obs, then better put it in a subfolder waiting
        # for the existence of a block sequence not yet implemented in P2
        obsconflist = ob.observationConfiguration
        doFolder = (len(obsconflist) > 1)
        parentContainerId = containerId
        if doFolder and not dryMode:
            folderName = obsconflist[0].Target.name
            folderName = re.sub('[^A-Za-z0-9]+', '_', folderName.strip())
            folder, _ = api.createFolder(containerId, folderName)
            containerId = folder['containerId']

        for observationConfiguration in ob.observationConfiguration:

            # create keywords storage objects
            acqTSF = TSF(self, "PIONIER_acq.tsf")
            obsTSF = TSF(self, "PIONIER_obs_calibrator.tsf")
                         # alias for PIONIER_obs_calibrator.tsf and
                         # PIONIER_obs_science.tsf")
            obTarget = OBTarget()
            obConstraints = OBConstraints()

            # set common properties
            acqTSF.INS_DISP = ins_disp

            if 'SCIENCE' in observationConfiguration.type:
                OBJTYPE = 'SCIENCE'
            else:
                OBJTYPE = 'CALIBRATOR'

            # define target
            # acqTSF.SEQ_INS_SOBJ_NAME = scienceTarget.name.strip()
            # obTarget.name = acqTSF.SEQ_INS_SOBJ_NAME.replace(' ', '_') #
            # allowed characters: letters, digits, + - _ . and no spaces
            obTarget.ra, obTarget.dec = self.getCoords(scienceTarget)
            obTarget.properMotionRa, obTarget.properMotionDec = self.getPMCoords(
                scienceTarget)

            # define some default values
            DIAMETER = float(self.get(scienceTarget, "DIAMETER", 0.0))
            VIS = 1.0  # FIXME

            # Retrieve Fluxes
            COU_GS_MAG = self.getFlux(scienceTarget, "V")
            acqTSF.SEQ_IAS_HMAG = self.getFlux(scienceTarget, "H")

            # setup some default values, to be changed below
            COU_AG_GSSOURCE = 'SCIENCE'  # by default
            GSRA = '00:00:00.000'
            GSDEC = '00:00:00.000'
            dualField = False

            # initialize FT variables (must exist)
            # TODO remove next lines using a dual_acq TSF that would handle
            # them

            # AO target
            aoTarget = ob.get(observationConfiguration, "AOTarget")
            if aoTarget != None:
                AONAME = aoTarget.name
                COU_AG_GSSOURCE = 'SETUPFILE'  # since we have an AO
                # TODO check if AO coords should be required by template
                # AORA, AODEC  = self.getCoords(aoTarget,
                # requirePrecision=False)
                acqTSF.COU_PMA, acqTSF.COU_PMD = self.getPMCoords(aoTarget)

            # Guide Star
            gsTarget = ob.get(observationConfiguration, 'GSTarget')
            if gsTarget != None:
                COU_GS_SOURCE = 'SETUPFILE'  # since we have an GS
                GSRA, GSDEC = self.getCoords(gsTarget, requirePrecision=False)
                # no PMRA, PMDE for GS !!
                COU_GS_MAG = float(gsTarget.FLUX_V)

            # LST interval
            try:
                obsConstraint = observationConfiguration.observationConstraints
                LSTINTERVAL = obsConstraint.LSTinterval
            except:
                LSTINTERVAL = None

            # Constraints
            obConstraints.name = 'Aspro-created constraints'
            skyTransparencyMagLimits = {"AT": 3, "UT": 5}
            if acqTSF.IAS.HMAG < skyTransparencyMagLimits[tel]:
                obConstraints.skyTransparency = 'Variable, thin cirrus'
            else:
                obConstraints.skyTransparency = 'Clear'
            # FIXME: error (OB): "Phase 2 constraints must closely follow what was requested in the Phase 1 proposal.
            # The seeing value allowed for this OB is >= java0x0 arcsec."
            obConstraints.seeing = 1.0
            obConstraints.baseline = BASELINE.replace(' ', '-')
            # FIXME: default values NOT IN ASPRO!
            # constaints.airmass = 5.0
            # constaints.fli = 1

            # compute dit, ndit, nexp

            my_sequence = sequence[0:2 * nexp]
            # and store computed values in obsTSF
            obsTSF.NEXPO = 5
            obsTSF.NSCANS = 100

            # then call the ob-creation using the API.
            if dryMode:
                ui.addToLog(
                    obTarget.name + " ready for p2 upload (details logged)")
                ui.addToLog(obTarget, False)
                ui.addToLog(obConstraints, False)
                ui.addToLog(acqTSF, False)
                ui.addToLog(obsTSF, False)

            else:
                self.createPionierOB(
                    ui, self.facility.a2p2client.getUsername(
                    ), api, containerId, obTarget, obConstraints, acqTSF, obsTSF, OBJTYPE, instrumentMode,
                                     DIAMETER, COU_AG_GSSOURCE, GSRA, GSDEC, COU_GS_MAG, dualField, SEQ_FT_ROBJ_NAME, SEQ_FT_ROBJ_MAG, SEQ_FT_ROBJ_DIAMETER, SEQ_FT_ROBJ_VIS, LSTINTERVAL)
                ui.addToLog(obTarget.name + " submitted on p2")
        # endfor
        if doFolder:
            containerId = parentContainerId
            doFolder = False

    def submitOB(self, ob, p2container):
        self.checkOB(ob, p2container, False)

    def createGPionierOB(
        self, ui, username, api, containerId, obTarget, obConstraints, acqTSF, obsTSF, OBJTYPE, instrumentMode,
                        DIAMETER, COU_AG_GSSOURCE, GSRA, GSDEC, COU_GS_MAG, dualField, SEQ_FT_ROBJ_NAME, SEQ_FT_ROBJ_MAG,
                        SEQ_FT_ROBJ_DIAMETER, SEQ_FT_ROBJ_VIS, LSTINTERVAL):
        ui.setProgress(0.1)

        # TODO compute value
        VISIBILITY = 1.0

        # everything seems OK
        # create new OB in container:
        goodName = re.sub('[^A-Za-z0-9]+', '_', acqTSF.SEQ_INS_SOBJ_NAME)
        OBS_DESCR = OBJTYPE[0:3] + '_' + goodName + '_GRAVITY_' + \
            obConstraints.baseline.replace('-', '') + '_' + instrumentMode

        ob, obVersion = api.createOB(containerId, OBS_DESCR)
        obId = ob['obId']

        # we use obId to populate OB
        ob['obsDescription']['name'] = OBS_DESCR[0:min(len(OBS_DESCR), 31)]
        ob['obsDescription']['userComments'] = 'Generated by ' + username + \
            ' using ASPRO 2 (c) JMMC on ' + datetime.datetime.now().isoformat()
        # ob['obsDescription']['InstrumentComments'] = 'AO-B1-C2-E3' #should be
        # a list of alternative quadruplets!

        # copy target info
        targetInfo = obTarget.getDict()
        for key in targetInfo:
            ob['target'][key] = targetInfo[key]

        # copy constraints info
        constraints = obConstraints.getDict()
        for k in constraints:
            ob['constraints'][k] = constraints[k]

        ob, obVersion = api.saveOB(ob, obVersion)

        # LST constraints if present
        # by default, above 40 degree. Will generate a WAIVERABLE ERROR if not.
        if LSTINTERVAL:
            sidTCs, stcVersion = api.getSiderealTimeConstraints(obId)
            print ("debug lst")
            print (LSTINTERVAL)
            lsts = LSTINTERVAL.split('/')
            lstStartSex = lsts[0]
            lstEndSex = lsts[1]
            # p2 seems happy with endlst < startlst
            # a = SkyCoord(lstStartSex+' +0:0:0',unit=(u.hourangle,u.deg))
            # b = SkyCoord(lstEndSex+' +0:0:0',unit=(u.hourangle,u.deg))
            # if b.ra.deg < a.ra.deg:
            # api.saveSiderealTimeConstraints(obId,[ {'from': lstStartSex, 'to': '00:00'},{'from': '00:00','to': lstEndSex}], stcVersion)
            # else:
            api.saveSiderealTimeConstraints(
                obId, [{'from': lstStartSex, 'to': lstEndSex}], stcVersion)
        ui.setProgress(0.2)

        # then, attach acquisition template(s)
        tpl, tplVersion = api.createTemplate(
            obId, self.getAcqTemplateName(dualField=dualField))
        # and put values
        # start with acqTSF ones and complete manually missing ones
        values = acqTSF.getDict()
        values.update({
            'SEQ.INS.SOBJ.DIAMETER':   DIAMETER,
                    'SEQ.INS.SOBJ.VIS':   VISIBILITY,
                    'COU.AG.GSSOURCE':   COU_AG_GSSOURCE,
                    'COU.AG.ALPHA':   GSRA,
                    'COU.AG.DELTA':   GSDEC,
                    'COU.GS.MAG':  round(COU_GS_MAG, 3),
                    'TEL.TARG.PARALLAX':   0.0
        })

        tpl, tplVersion = api.setTemplateParams(obId, tpl, values, tplVersion)
        ui.setProgress(0.3)

        tpl, tplVersion = api.createTemplate(
            obId, self.getObsTemplateName(OBJTYPE, dualField))
        ui.setProgress(0.4)

        # put values. they are the same except for dual obs science (?)
        values = obsTSF.getDict()
        tpl, tplVersion = api.setTemplateParams(obId, tpl, values, tplVersion)
        ui.setProgress(0.5)

        # verify OB online
        response, _ = api.verifyOB(obId, True)
        ui.setProgress(1.0)
        self.showP2Response(response, ob, obId)

        # fetch OB again to confirm its status change
        #   ob, obVersion = api.getOB(obId)
        # python3: print('Status of verified OB', obId, 'is now',
        # ob['obStatus'])
