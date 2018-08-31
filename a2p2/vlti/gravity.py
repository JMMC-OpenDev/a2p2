#!/usr/bin/env python

__all__ = []

from a2p2.apis import Instrument

from a2p2.vlti.gui import VltiUI
from a2p2.vlti.instrument import VltiInstrument


from astropy.coordinates import SkyCoord
import cgi
import numpy as np
import re
import traceback

import datetime



HELPTEXT="""
Please define Gravity instrument help in a2p2/vlti/gravity.py 
"""

class Gravity(VltiInstrument):
    def  __init__(self, facility):
        VltiInstrument.__init__(self, facility, "GRAVITY")
        
        # TODO extract from conf file
        self.insmodes=[ 'LOW-COMBINED', 'LOW-SPLIT', 'MEDIUM-COMBINED' ,'MEDIUM-SPLIT', 'MED', 'HIGH-COMBINED', 'HIGH-SPLIT']                
    
    # mainly corresponds to a refactoring of old utils.processXmlMessage
    def checkOB(self, ob, p2container, dryMode=True): 
        api = self.facility.getAPI()
        ui = self.ui
        rangeTable = self.getRangeTable()
        
        errors=[]
        
        currentInstrument = p2container.instrument
        containerId = p2container.containerId
    
        try:
            instrumentConfiguration = ob.instrumentConfiguration
            BASELINE = ob.interferometerConfiguration.stations
            instrumentMode = instrumentConfiguration.instrumentMode
            
            if not instrumentMode in self.insmodes:               
                raise ValueError ( "Invalid Instrument Mode '%s'.\n Must be one of %s .\nPlease Correct."%(instrumentMode, self.insmodes) )
        
            #if we have more than 1 obs, then better put it in a subfolder waiting for the existence of a block sequence not yet implemented in P2
            obsconflist = ob.observationConfiguration
            doFolder = (len(obsconflist) > 1)
            parentContainerId = containerId
            if doFolder and not dryMode:
                folderName = obsconflist[0].SCTarget.name
                folderName = re.sub('[^A-Za-z0-9]+', '_', folderName.strip())
                folder, _ = api.createFolder(containerId, folderName)
                containerId = folder['containerId']

            for observationConfiguration in ob.observationConfiguration:                
                if 'SCIENCE' in observationConfiguration.type:
                    OBJTYPE = 'SCIENCE'
                else:
                    OBJTYPE = 'CALIBRATOR'

                scienceTarget = observationConfiguration.SCTarget
                NAME = scienceTarget.name
                SCRA, SCDEC = self.getCoords(scienceTarget)
                PMRA, PMDEC = self.getPMCoords(scienceTarget)
                
                # define some default values                 
                DIAMETER = float(self.get(scienceTarget, "DIAMETER", 0.0))
                VIS = 1.0 #FIXME
                
                # TODO add a check flux method in a VltiInstruments class
                COU_GS_MAG = float(scienceTarget.FLUX_V)
                SEQ_INS_SOBJ_MAG = float(scienceTarget.FLUX_K)
                SEQ_FI_HMAG = float(scienceTarget.FLUX_H)
                
                #setup some default values, to be changed below
                COU_AG_GSSOURCE = 'SCIENCE' #by default
                GSRA = '00:00:00.000'
                GSDEC = '00:00:00.000'                
                COU_AG_PMA = 0.0
                COU_AG_PMD = 0.0                
                dualField = False
                
                # initialize FT variables (must exist)
                FTRA = ""
                FTDEC = ""
                SEQ_FT_ROBJ_NAME = ""
                SEQ_FT_ROBJ_MAG = -99.99
                SEQ_FT_ROBJ_DIAMETER = -1.0
                SEQ_FT_ROBJ_VIS = -1.0

                # if FT Target is not ScTarget, we are in dual-field (TBD)
                ftTarget = ob.get(observationConfiguration, "FTTarget")
                if ftTarget != None:
                    SEQ_FT_ROBJ_NAME = ftTarget.name
                    FTRA, FTDEC = self.getCoords(ftTarget)
                    #no PMRA, PMDE for FT !!                    
                    SEQ_FI_HMAG = float(ftTarget.FLUX_H)  #just to say we must treat the case there is no FT Target
                    SEQ_FT_ROBJ_MAG = SEQ_FI_HMAG
                    SEQ_FT_ROBJ_DIAMETER = 0.0 #FIXME
                    SEQ_FT_ROBJ_VIS = 1.0      #FIXME
                    dualField = True
                    
                    # test distance in dual field mode
                    isUT = (BASELINE[0] == "U") 
                    if isUT:
                        SCtoREFmaxDist = 2000
                        SCtoREFminDist = 400                        
                    else:
                        SCtoREFminDist = 1500
                        SCtoREFmaxDist = 4000
                    #compute x,y between science and ref beams:
                    diff = getSkyDiff(SCRA, SCDEC, FTRA, FTDEC)
                    if np.abs(diff[0]) < SCtoREFminDist:
                        raise ValueError ("Dual-Field distance of two stars is  < " + str(SCtoREFminDist) + " mas, Please Correct.")
                    elif  np.abs(diff[0]) > SCtoREFmaxDist:
                        raise ValueError ("Dual-Field distance of two stars is  > " + str(SCtoREFmaxDist) + " mas, Please Correct.")                      

                #AO target
                aoTarget = ob.get(observationConfiguration, "AOTarget")
                if aoTarget != None:
                    AONAME = aoTarget.name
                    COU_AG_GSSOURCE = 'SETUPFILE' #since we have an AO
                    # TODO check if AO coords should be required by template 
                    # AORA, AODEC  = self.getCoords(aoTarget, requirePrecision=False)                        
                    COU_AG_PMA, COU_AG_PMD = self.getPMCoords(aoTarget)

                #Guide Star
                gsTarget = ob.get(observationConfiguration, 'GSTarget')
                if gsTarget != None:                        
                    COU_AG_SOURCE = 'SETUPFILE' #since we have an GS
                    GSRA, GSDEC = self.getCoords(gsTarget, requirePrecision=False)
                    #no PMRA, PMDE for GS !!
                    COU_GS_MAG = float(gsTarget.FLUX_V)                        

                #LST interval
                try:
                    obsConstraint = observationConfiguration.observationConstraints
                    LSTINTERVAL = obsConstraint.LSTinterval
                except:
                    LSTINTERVAL = None

                    
                #then call the ob-creation using the API. 
                # TODO run this code in a second loop after global check ?
                if dryMode:
                    ui.addToLog(NAME+ " ready for p2 upload")
                    # just try to get ditTable
                    ditTable = self.getDitTable()
                else:
                    createGravityOB(ui, self.facility.a2p2client.getUsername(), api, containerId, OBJTYPE, NAME, BASELINE, instrumentMode, SCRA, SCDEC, PMRA, PMDEC, SEQ_INS_SOBJ_MAG, SEQ_FI_HMAG, DIAMETER, COU_AG_GSSOURCE, GSRA, GSDEC, COU_GS_MAG, COU_AG_PMA, COU_AG_PMD, dualField, FTRA, FTDEC, SEQ_FT_ROBJ_NAME, SEQ_FT_ROBJ_MAG, SEQ_FT_ROBJ_DIAMETER, SEQ_FT_ROBJ_VIS, LSTINTERVAL)
                    ui.addToLog(NAME+ " submitted on p2")
            #endfor
            if doFolder:
                containerId = parentContainerId
                doFolder = False
        
        except ValueError as e:
            errors.append(e)
            ui.ShowErrorMessage("Value error :\n %s " % (e))
            ui.setProgress(0)
        except Exception as e:
            errors.append(e)
            traceback.print_exc()
            trace = traceback.format_exc(limit=1)
            ui.ShowErrorMessage("General error or Absent Parameter in template!\n Missing magnitude or OB not set ?\n\nError :\n %s " % (trace))            
        
        return len(errors)==0

    def submitOB(self, ob, p2container):
        self.checkOB(ob, p2container, False)


def createGravityOB(ui, username, api, containerId, OBJTYPE, NAME, BASELINE, instrumentMode, SCRA, SCDEC, PMRA, PMDEC, SEQ_INS_SOBJ_MAG, SEQ_FI_HMAG,
                    DIAMETER, COU_AG_GSSOURCE, GSRA, GSDEC, COU_GS_MAG, COU_AG_PMA, COU_AG_PMD, dualField, FTRA, FTDEC, SEQ_FT_ROBJ_NAME, SEQ_FT_ROBJ_MAG,
                    SEQ_FT_ROBJ_DIAMETER, SEQ_FT_ROBJ_VIS, LSTINTERVAL):
    ui.setProgress(0.1)
    
    # UT or AT?
    isUT = (BASELINE[0] == "U")
    if isUT:
        SCtoREFmaxDist = 2000
        SCtoREFminDist = 400
        tel = 1
        if SEQ_INS_SOBJ_MAG  < 5:
            skyTransparencyConstrainText = 'Variable, thin cirrus'
        else:
            skyTransparencyConstrainText = 'Clear'
    else:
        SCtoREFminDist = 1500
        SCtoREFmaxDist = 4000
        tel = 0
        if SEQ_INS_SOBJ_MAG  < 3:
            skyTransparencyConstrainText = 'Variable, thin cirrus'
        else:
            skyTransparencyConstrainText = 'Clear'

    VISIBILITY = 1.0
    dualmode = 0
    if dualField:
        dualmode = 1
        #compute x,y between science and ref beams:
        diff = getSkyDiff(SCRA, SCDEC, FTRA, FTDEC)
    
    # self.getRange("GRAVITY_gen_acq.tsf", self.KW_INS_SPEC_RES)    
    
    if instrumentMode == 'LOW-COMBINED':
        INS_SPEC_RES = 'LOW'
        INS_FT_POL = 'OUT'
        INS_SPEC_POL = 'OUT'
        string_dit = getDit(SEQ_INS_SOBJ_MAG, 0, 0, tel, dualmode)
    elif instrumentMode == 'LOW-SPLIT':
        INS_SPEC_RES = 'LOW'
        INS_FT_POL = 'IN'
        INS_SPEC_POL = 'IN'
        string_dit = getDit(SEQ_INS_SOBJ_MAG, 0, 1, tel, dualmode)
    elif instrumentMode == 'MEDIUM-COMBINED':
        INS_SPEC_RES = 'MED'
        INS_FT_POL = 'OUT'
        INS_SPEC_POL = 'OUT'
        string_dit = getDit(SEQ_INS_SOBJ_MAG, 1, 0, tel, dualmode)
    elif instrumentMode == 'MEDIUM-SPLIT':
        INS_SPEC_RES = 'MED'
        INS_FT_POL = 'IN'
        INS_SPEC_POL = 'IN'
        string_dit = getDit(SEQ_INS_SOBJ_MAG, 1, 1, tel, dualmode)
    elif instrumentMode == 'HIGH-COMBINED':
        INS_SPEC_RES = 'HIGH'
        INS_FT_POL = 'OUT'
        INS_SPEC_POL = 'OUT'
        string_dit = getDit(SEQ_INS_SOBJ_MAG, 2, 0, tel, dualmode)
    elif instrumentMode == 'HIGH-SPLIT':
        INS_SPEC_RES = 'HIGH'
        INS_FT_POL = 'IN'
        INS_SPEC_POL = 'IN'
        string_dit = getDit(SEQ_INS_SOBJ_MAG, 2, 1, tel, dualmode)    

    #compute ndit, nexp
    dit = float(string_dit)
    ndit = 300 / dit
    if ndit < 10:
        ndit = 10
    if ndit > 300:
        ndit = 300
    ndit = int(ndit) #must be integer
    exptime = int(ndit * dit + 40) #40 sec overhead by exp
    nexp = (1800-900) / exptime
    nexp = int(nexp)
    ui.addToLog('number of exposures to reach 1800 s per OB is ' + str(nexp))
    if nexp < 3:
        nexp = 3 #min is O S O
        # recompute ndit
        exptime = (1800-900) / nexp
        ndit = (exptime-40) / dit
        ndit = int(ndit)
        if ndit < 10:
            ndit = 10
            ui.addToLog("**Warning**, OB NDIT has been set to min value=10, but OB will take longer than 1800 s")
    nexp %= 40
    sequence = 'O S O O S O O S O O S O O S O O S O O S O O S O O S O O S O O S O O S O O S O O'
    my_sequence = sequence[0:2 * nexp]

    #everything seems OK
    #create new OB in container:
    goodName = re.sub('[^A-Za-z0-9]+', '_', NAME.strip())
    if OBJTYPE == 'SCIENCE':
        isCalib = False
        OBS_DESCR = 'SCI_' + goodName + '_GRAVITY_' + BASELINE.replace(' ', '') + '_' + instrumentMode
    else:
        isCalib = True
        OBS_DESCR = 'CAL_' + goodName + '_GRAVITY_' + BASELINE.replace(' ', '') + '_' + instrumentMode
    ob, obVersion = api.createOB(containerId, OBS_DESCR)
    obId = ob['obId']

    #we use obId to populate OB
    ob['obsDescription']['name'] = OBS_DESCR[0:min(len(OBS_DESCR), 31)]
    ob['obsDescription']['userComments'] = 'Generated by ' + username + ' using ASPRO 2 (c) JMMC on '+ datetime.datetime.now().isoformat()
    #ob['obsDescription']['InstrumentComments'] = 'AO-B1-C2-E3' #should be a list of alternative quadruplets!

    ob['target']['name'] = NAME.replace(' ', '_')
    ob['target']['ra'] = SCRA
    ob['target']['dec'] = SCDEC
    ob['target']['properMotionRa'] = round(PMRA / 1000.0, 4)
    ob['target']['properMotionDec'] = round(PMDEC / 1000.0, 4)


    ob['constraints']['name']  = 'Aspro-created constraint'
    #FIXME: error (OB): "Phase 2 constraints must closely follow what was requested in the Phase 1 proposal.
    #                    The seeing value allowed for this OB is >= java0x0 arcsec."
    ob['constraints']['seeing'] = 1.0
    ob['constraints']['skyTransparency'] = skyTransparencyConstrainText
    ob['constraints']['baseline']  = BASELINE.replace(' ', '-')
    # FIXME: default values NOT IN ASPRO!
    #ob['constraints']['airmass'] = 5.0
    #ob['constraints']['fli'] = 1

    ob, obVersion = api.saveOB(ob, obVersion)

    ##LST constraints if present
    ##by default, above 40 degree. Will generate a WAIVERABLE ERROR if not.
    if LSTINTERVAL:
        sidTCs, stcVersion = api.getSiderealTimeConstraints(obId)
        lsts = LSTINTERVAL.split('/')
        lstStartSex = lsts[0]
        lstEndSex = lsts[1]
        ## p2 seems happy with endlst < startlst
        ## a = SkyCoord(lstStartSex+' +0:0:0',unit=(u.hourangle,u.deg))
        ## b = SkyCoord(lstEndSex+' +0:0:0',unit=(u.hourangle,u.deg))
        ## if b.ra.deg < a.ra.deg:
        ## api.saveSiderealTimeConstraints(obId,[ {'from': lstStartSex, 'to': '00:00'},{'from': '00:00','to': lstEndSex}], stcVersion)
        ## else:
        api.saveSiderealTimeConstraints(obId, [{'from': lstStartSex, 'to': lstEndSex}], stcVersion)

    ui.setProgress(0.2)

    #then, attach acquisition template(s)
    if dualField:
        tpl, tplVersion = api.createTemplate(obId, 'GRAVITY_dual_acq')
        # put values
        tpl, tplVersion = api.setTemplateParams(obId, tpl, {
                                                'SEQ.FT.ROBJ.NAME': SEQ_FT_ROBJ_NAME,
                                                'SEQ.FT.ROBJ.MAG': round(SEQ_FT_ROBJ_MAG, 3),
                                                'SEQ.FT.ROBJ.DIAMETER': SEQ_FT_ROBJ_DIAMETER,
                                                'SEQ.FT.ROBJ.VIS':  SEQ_FT_ROBJ_VIS,
                                                'SEQ.FT.MODE':      "AUTO",
                                                'SEQ.INS.SOBJ.NAME':   NAME,
                                                'SEQ.INS.SOBJ.MAG':   round(SEQ_INS_SOBJ_MAG, 3),
                                                'SEQ.INS.SOBJ.DIAMETER':   DIAMETER,
                                                'SEQ.INS.SOBJ.VIS':   VISIBILITY,
                                                'SEQ.INS.SOBJ.X': diff[0],
                                                'SEQ.INS.SOBJ.Y': diff[1],
                                                'SEQ.FI.HMAG':   round(SEQ_FI_HMAG, 3),
                                                'TEL.TARG.PARALLAX':   0.0,
                                                'INS.SPEC.RES': INS_SPEC_RES,
                                                'INS.FT.POL': INS_FT_POL,
                                                'INS.SPEC.POL':  INS_SPEC_POL,
                                                'COU.AG.GSSOURCE':   COU_AG_GSSOURCE,
                                                'COU.AG.ALPHA':   GSRA,
                                                'COU.AG.DELTA':   GSDEC,
                                                'COU.GS.MAG':  round(COU_GS_MAG, 3),
                                                'COU.AG.PMA':  round(COU_AG_PMA / 1000, 4),
                                                'COU.AG.PMD':  round(COU_AG_PMD / 1000, 4)
                                                }, tplVersion)

    else:
        tpl, tplVersion = api.createTemplate(obId, 'GRAVITY_single_acq')
        # put values
        tpl, tplVersion = api.setTemplateParams(obId, tpl, {
                                                'SEQ.INS.SOBJ.NAME':   NAME,
                                                'SEQ.INS.SOBJ.MAG':   round(SEQ_INS_SOBJ_MAG, 3),
                                                'SEQ.INS.SOBJ.DIAMETER':   DIAMETER,
                                                'SEQ.INS.SOBJ.VIS':   VISIBILITY,
                                                'COU.AG.GSSOURCE':   COU_AG_GSSOURCE,
                                                'COU.AG.ALPHA':   GSRA,
                                                'COU.AG.DELTA':   GSDEC,
                                                'COU.GS.MAG':  round(COU_GS_MAG, 3),
                                                'COU.AG.PMA':  round(COU_AG_PMA / 1000, 4),
                                                'COU.AG.PMD':  round(COU_AG_PMD / 1000, 4),
                                                'SEQ.FI.HMAG':   round(SEQ_FI_HMAG, 3),
                                                'TEL.TARG.PARALLAX':   0.0,
                                                'INS.SPEC.RES': INS_SPEC_RES,
                                                'INS.FT.POL': INS_FT_POL,
                                                'INS.SPEC.POL':  INS_SPEC_POL
                                                }, tplVersion)

    templateId = tpl['templateId']

    ui.setProgress(0.3)

    if isCalib:
        if dualField:
            tpl, tplVersion = api.createTemplate(obId, 'GRAVITY_dual_obs_calibrator')
        else:
            tpl, tplVersion = api.createTemplate(obId, 'GRAVITY_single_obs_calibrator')
    else:
        if dualField:
            tpl, tplVersion = api.createTemplate(obId, 'GRAVITY_dual_obs_exp')
        else:
            tpl, tplVersion = api.createTemplate(obId, 'GRAVITY_single_obs_exp')
    templateId = tpl['templateId']

    ui.setProgress(0.4)

    # put values. they are the same except for dual obs science (?)
    if dualField and not isCalib:
        tpl, tplVersion = api.setTemplateParams(obId, tpl, {
                                                'DET2.DIT':  string_dit,
                                                'DET2.NDIT.OBJECT':  ndit,
                                                'DET2.NDIT.SKY':  ndit,
                                                'SEQ.OBSSEQ':  my_sequence,
                                                'SEQ.SKY.X':  2000,
                                                'SEQ.SKY.Y':  2000
                                                }, tplVersion)
    else:
        tpl, tplVersion = api.setTemplateParams(obId, tpl, {
                                                'DET2.DIT':  string_dit,
                                                'DET2.NDIT.OBJECT':  ndit,
                                                'DET2.NDIT.SKY':  ndit,
                                                'SEQ.OBSSEQ':  my_sequence,
                                                'SEQ.RELOFF.X':  "0.0",
                                                'SEQ.RELOFF.Y':  "0.0",
                                                'SEQ.SKY.X':  2000,
                                                'SEQ.SKY.Y':  2000
                                                }, tplVersion)

    ui.setProgress(0.5)

    #verify OB online
    response, _ = api.verifyOB(obId, True)

    ui.setProgress(1.0)

    if response['observable']:
        ui.ShowInfoMessage('OB ' + str(obId) + ' ' + ob['name'] + ' is OK.')
        ui.addToLog('OB: ' + str(obId) + ' is ok')
    else:
        s = ""
        for ss in response['messages']:
            s += cgi.escape(ss) + '\n'
        ui.ShowWarningMessage('OB ' + str(obId) + ' <b>HAS Warnings</b>. ESO says:\n\n' + s)
        ui.addToLog('OB: ' + str(obId) + ' created with warnings')
        # (NOTE: we need to escape things like <= in returned text)

        #   # fetch OB again to confirm its status change
        #   ob, obVersion = api.getOB(obId)
        #   python3: print('Status of verified OB', obId, 'is now', ob['obStatus'])

# here dit must be a string since this is what p2 expects. NOT an integer or real/double.
def getDit(mag, spec, pol, tel, mode):
    string_dit = "1"

    if mode == 1: #Dual
        if tel == 1:
            mag -= 3.7 #UT, DUAL
        else:
            mag -= 0.7 #AT, DUAL
    elif tel == 1:
        mag -= 3.0 #UT, SINGLE

    if spec == 2: #HR
        if pol == 1: #SPLIT
            if mag > 1:
                string_dit = "30"
            elif mag > 0:
                string_dit = "10"
            elif mag > -0.5:
                string_dit = "5"
            else:
                string_dit = "3"
        else: #COMB
            if mag > 2:
                string_dit = "30"
            elif mag > 0.5:
                string_dit = "10"
            elif mag > -0.5:
                string_dit = "5"
            else:
                string_dit = "1"
    elif spec == 1: #MR
        if pol == 1: #SPLIT
            if mag > 4:
                string_dit = "30"
            elif mag > 3:
                string_dit = "10"
            elif mag > 2.5:
                string_dit = "5"
            elif mag > 1.5:
                string_dit = "3"
            elif mag > 0.0:
                string_dit = "1"
            else:
                string_dit = "0.3"
        else: #COMB
            if mag > 5:
                string_dit = "30"
            elif mag > 3.5:
                string_dit = "10"
            elif mag > 3.0:
                string_dit = "5"
            elif mag > 2.5:
                string_dit = "3"
            elif mag > 1.0:
                string_dit = "1"
            else:
                string_dit = "0.3"
    elif spec == 0: #LR FIXME VALUES ARE NOT GIVEN!!!!!!!!
        if pol == 1: #SPLIT
            if mag > 9:
                string_dit = "30"
            elif mag > 7:
                string_dit = "10"
            elif mag > 6.5:
                string_dit = "5"
            elif mag > 5.5:
                string_dit = "3"
            elif mag > 4.0:
                string_dit = "1"
            else:
                string_dit = "0.3"
        else: #COMB
            if mag > 10:
                string_dit = "30"
            elif mag > 9:
                string_dit = "10"
            elif mag > 7.5:
                string_dit = "5"
            elif mag > 6.5:
                string_dit = "3"
            elif mag > 5.0:
                string_dit = "1"
            else:
                string_dit = "0.3"
    return string_dit
