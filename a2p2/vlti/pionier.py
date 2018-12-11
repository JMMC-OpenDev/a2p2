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


class Pionier(VltiInstrument):

    def __init__(self, facility):
        VltiInstrument.__init__(self, facility, "PIONIER")

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
            kappaTSF = TSF(self, "PIONIER_gen_cal_kappa.tsf")
            darkTSF = TSF(self, "PIONIER_gen_cal_dark.tsf")

            obTarget = OBTarget()
            obConstraints = OBConstraints()

            # set common properties
            acqTSF.INS_DISP_NAME = ins_disp

            if 'SCIENCE' in observationConfiguration.type:
                OBJTYPE = 'SCIENCE'
            else:
                OBJTYPE = 'CALIBRATOR'

            scienceTarget = observationConfiguration.SCTarget

            # define target
            # acqTSF.SEQ_INS_SOBJ_NAME = scienceTarget.name.strip()

            acqTSF.TARGET_NAME = scienceTarget.name.strip()
            obTarget.name = acqTSF.TARGET_NAME.replace(
                ' ', '_')  # allowed characters: letters, digits, + - _ . and no spaces
            obTarget.ra, obTarget.dec = self.getCoords(scienceTarget)
            obTarget.properMotionRa, obTarget.properMotionDec = self.getPMCoords(
                scienceTarget)

            # define some default values
            DIAMETER = float(self.get(scienceTarget, "DIAMETER", 0.0))
            VIS = 1.0  # FIXME

            # Retrieve Fluxes
            TEL_COU_MAG = self.getFlux(scienceTarget, "V")
            acqTSF.ISS_IAS_HMAG = self.getFlux(scienceTarget, "H")

            # setup some default values, to be changed below
            TEL_COU_GSSOURCE = 'SCIENCE'  # by default
            GSRA = '00:00:00.000'
            GSDEC = '00:00:00.000'

            # initialize FT variables (must exist)

            # AO target
            aoTarget = ob.get(observationConfiguration, "AOTarget")
            if aoTarget != None:
                AONAME = aoTarget.name
                TEL_COU_GSSOURCE = 'SETUPFILE'  # since we have an AO
                # TODO check if AO coords should be required by template
                # AORA, AODEC  = self.getCoords(aoTarget,
                # requirePrecision=False)
                acqTSF.TEL_COU_PMA, acqTSF.TEL_COU_PMD = self.getPMCoords(
                    aoTarget)

            # Guide Star
            gsTarget = ob.get(observationConfiguration, 'GSTarget')
            if gsTarget != None:
                TEL_COU_GSSOURCE = 'SETUPFILE'  # since we have an GS
                GSRA, GSDEC = self.getCoords(gsTarget, requirePrecision=False)
                # no PMRA, PMDE for GS !!
                TEL_COU_MAG = float(gsTarget.FLUX_V)

            # LST interval
            try:
                obsConstraint = observationConfiguration.observationConstraints
                LSTINTERVAL = obsConstraint.LSTinterval
            except:
                LSTINTERVAL = None

            # Constraints
            obConstraints.name = 'Aspro-created constraints'
            skyTransparencyMagLimits = {"AT": 3, "UT": 5}
            if acqTSF.ISS_IAS_HMAG < skyTransparencyMagLimits[tel]:
                obConstraints.skyTransparency = 'Variable, thin cirrus'
            else:
                obConstraints.skyTransparency = 'Clear'

            if acqTSF.ISS_IAS_HMAG > 7.5:
                    acqTSF.INS_DISP_NAME = "FREE"

            # FIXME: error (OB): "Phase 2 constraints must closely follow what was requested in the Phase 1 proposal.
            # The seeing value allowed for this OB is >= java0x0 arcsec."
            obConstraints.seeing = 1.0
            obConstraints.baseline = BASELINE.replace(' ', '-')
            # FIXME: default values NOT IN ASPRO!
            # constaints.airmass = 5.0
            # constaints.fli = 1

            # compute dit, ndit, nexp

            # and store computed values in obsTSF
            obsTSF.SEQ_NEXPO = 5
            # obsTSF.NSCANS = 100
            # kappaTSF.SEQ_DOIT=False
            # darkTSF.SEQ_DOIT=True

            # then call the ob-creation using the API.
            if dryMode:
                ui.addToLog(
                    obTarget.name + " ready for p2 upload (details logged)")
                ui.addToLog(obTarget, False)
                ui.addToLog(obConstraints, False)
                ui.addToLog(acqTSF, False)
                ui.addToLog(obsTSF, False)
                ui.addToLog(kappaTSF, False)
                ui.addToLog(darkTSF, False)

            else:
                self.createPionierOB(
                    ui, self.facility.a2p2client.getUsername(
                    ), api, containerId, obTarget, obConstraints, acqTSF,
                                     obsTSF, kappaTSF, darkTSF, OBJTYPE, instrumentMode, TEL_COU_GSSOURCE, GSRA, GSDEC, TEL_COU_MAG, LSTINTERVAL)
                ui.addToLog(obTarget.name + " submitted on p2")
        # endfor
        if doFolder:
            containerId = parentContainerId
            doFolder = False

    def submitOB(self, ob, p2container):
        self.checkOB(ob, p2container, False)

    def getPionierTemplateName(self, templateType, OBJTYPE):
        objType = "calibrator"
        if OBJTYPE and "SCI" in OBJTYPE:
            objType = "science"
        if OBJTYPE:
            return "_".join((self.getName(), templateType, objType))
        return "_".join((self.getName(), templateType))

    def getPionierObsTemplateName(self, OBJTYPE):
        return self.getPionierTemplateName("obs", OBJTYPE)

    def createPionierOB(
        self, ui, username, api, containerId, obTarget, obConstraints, acqTSF, obsTSF, kappaTSF, darkTSF, OBJTYPE, instrumentMode,
                       TEL_COU_GSSOURCE, GSRA, GSDEC, TEL_COU_MAG, LSTINTERVAL):
        ui.setProgress(0.1)

        # TODO compute value
        VISIBILITY = 1.0

        # everything seems OK
        # create new OB in container:
        goodName = re.sub('[^A-Za-z0-9]+', '_', acqTSF.TARGET_NAME)
        OBS_DESCR = OBJTYPE[0:3] + '_' + goodName + '_PIONIER_' + \
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
            lsts = LSTINTERVAL.split('/')
            lstStartSex = lsts[0]
            lstEndSex = lsts[1]
            # p2 seems happy with endlst < startlst
            # a = SkyCoord(lstStartSex+' +0:0:0',unit=(ugetPionierTemplateName.hourangle,u.deg))
            # b = SkyCoord(lstEndSex+' +0:0:0',unit=(u.hourangle,u.deg))
            # if b.ra.deg < a.ra.deg:
            # api.saveSiderealTimeConstraints(obId,[ {'from': lstStartSex, 'to': '00:00'},{'from': '00:00','to': lstEndSex}], stcVersion)
            # else:
            api.saveSiderealTimeConstraints(
                obId, [{'from': lstStartSex, 'to': lstEndSex}], stcVersion)
        ui.setProgress(0.2)

        # then, attach acquisition template(s)
        tpl, tplVersion = api.createTemplate(obId, 'PIONIER_acq')
        # and put values
        # start with acqTSF ones and complete manually missing ones
        values = acqTSF.getDict()
        values.update({'TEL.COU.GSSOURCE':   TEL_COU_GSSOURCE,
                       'TEL.COU.ALPHA':   GSRA,
                       'TEL.COU.DELTA':   GSDEC,
                       'TEL.COU.MAG':  round(TEL_COU_MAG, 3)
                       })

        tpl, tplVersion = api.setTemplateParams(obId, tpl, values, tplVersion)
        ui.setProgress(0.3)

        # Put Obs template
        tpl, tplVersion = api.createTemplate(
            obId, self.getPionierObsTemplateName(OBJTYPE))
        ui.setProgress(0.4)
        values = obsTSF.getDict()
        tpl, tplVersion = api.setTemplateParams(obId, tpl, values, tplVersion)
        ui.setProgress(0.5)

        # put Kappa Matrix Template
        tpl, tplVersion = api.createTemplate(obId, 'PIONIER_gen_cal_kappa')
        ui.setProgress(0.6)
        values = kappaTSF.getDict()
        tpl, tplVersion = api.setTemplateParams(obId, tpl, values, tplVersion)
        ui.setProgress(0.7)

        # put Dark Template
        tpl, tplVersion = api.createTemplate(obId, 'PIONIER_gen_cal_dark')
        ui.setProgress(0.8)
        values = darkTSF.getDict()
        tpl, tplVersion = api.setTemplateParams(obId, tpl, values, tplVersion)
        ui.setProgress(0.9)

        # verify OB online
        response, _ = api.verifyOB(obId, True)
        ui.setProgress(1.0)
        self.showP2Response(response, ob, obId)

        # fetch OB again to confirm its status change
        #   ob, obVersion = api.getOB(obId)
        # python3: print('Status of verified OB', obId, 'is now',
        # ob['obStatus'])
