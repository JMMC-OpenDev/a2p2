#!/usr/bin/env python

__all__ = []

from a2p2.apis import Instrument
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

HELPTEXT="""
Please define Gravity instrument help in a2p2/vlti/gravity.py 
"""

class Gravity(VltiInstrument):
    def  __init__(self, facility):
        VltiInstrument.__init__(self, facility, "GRAVITY")
               
    # mainly corresponds to a refactoring of old utils.processXmlMessage
    def checkOB(self, ob, p2container, dryMode=True): 
        api = self.facility.getAPI()
        ui = self.ui
        containerId = p2container.containerId
        
        instrumentConfiguration = ob.instrumentConfiguration
        BASELINE = ob.interferometerConfiguration.stations
        tel = BASELINE[0]+'T'
        instrumentMode = instrumentConfiguration.instrumentMode

        # Retrieve SPEC and POL info from instrumentMode
        for res in self.getRange("GRAVITY_gen_acq.tsf", "INS.SPEC.RES"):
            if res in instrumentMode[0:len(res)]:
                ins_spec_res = res
        if "COMBINED" in instrumentMode:
            ins_pol="OUT"
        else:    
            inspol = 'IN'

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

            # create keywords storage objects
            acqTSF = TSF(self,"GRAVITY_gen_acq.tsf" )
            obsTSF = TSF(self,"GRAVITY_single_obs_exp.tsf") # alias for ,GRAVITY_single_obs_calibrator.tsf,GRAVITY_dual_obs_exp.tsf,GRAVITY_dual_obs_calibrator.tsf")                            
            target = OBTarget()
            constraints = OBConstraints()

            acqTSF.INS_SPEC_RES = ins_spec_res                   
            acqTSF.INS_FT_POL = ins_pol
            acqTSF.INS_SPEC_POL = ins_pol
            
            if 'SCIENCE' in observationConfiguration.type:
                OBJTYPE = 'SCIENCE'
            else:
                OBJTYPE = 'CALIBRATOR'

            scienceTarget = observationConfiguration.SCTarget

            target.name = scienceTarget.name.strip()
            acqTSF.SEQ_INS_SOBJ_NAME = target.name
            target.ra, target.dec = self.getCoords(scienceTarget)
            target.properMotionRa , target.properMotionDec = self.getPMCoords(scienceTarget)

            # define some default values                 
            DIAMETER = float(self.get(scienceTarget, "DIAMETER", 0.0))
            VIS = 1.0 #FIXME

            # Retrieve Fluxes
            COU_GS_MAG = self.getFlux(scienceTarget, "V")
            acqTSF.SEQ_INS_SOBJ_MAG = self.getFlux(scienceTarget, "K")
            acqTSF.SEQ_FI_HMAG = self.getFlux(scienceTarget, "H")

            #setup some default values, to be changed below
            COU_AG_GSSOURCE = 'SCIENCE' #by default
            GSRA = '00:00:00.000'
            GSDEC = '00:00:00.000'                             
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
                if tel=="UT":
                    SCtoREFmaxDist = 2000
                    SCtoREFminDist = 400                        
                else:
                    SCtoREFminDist = 1500
                    SCtoREFmaxDist = 4000
                #compute x,y between science and ref beams:
                diff = getSkyDiff(target.ra, target.dec, FTRA, FTDEC)
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
                acqTSF.COU_AG_PMA, acqTSF.COU_AG_PMD = self.getPMCoords(aoTarget)

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

            #Constraints                
            constraints.name = 'Aspro-created constraints'
            skyTransparencyMagLimits = {"AT":3, "UT":5}                
            if acqTSF.SEQ_INS_SOBJ_MAG  < skyTransparencyMagLimits[tel]:
                constraints.skyTransparency = 'Variable, thin cirrus'
            else:
                constraints.skyTransparency = 'Clear'
            #FIXME: error (OB): "Phase 2 constraints must closely follow what was requested in the Phase 1 proposal.
            #                    The seeing value allowed for this OB is >= java0x0 arcsec."
            constraints.seeing = 1.0
            constraints.baseline =  BASELINE.replace(' ', '-')
            # FIXME: default values NOT IN ASPRO!
            #constaints.airmass = 5.0 
            #constaints.fli = 1           

            #compute dit, ndit, nexp
            dit=self.getDit(tel, acqTSF.INS_SPEC_RES, acqTSF.INS_SPEC_POL, acqTSF.SEQ_INS_SOBJ_MAG, dualField, showWarning=dryMode)
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

            #then call the ob-creation using the API. 
            # TODO run this code in a second loop after global check ?
            if dryMode:
                ui.addToLog(target.name + " ready for p2 upload")  
                ui.addToLog(str(constraints))                
            else:
                self.createGravityOB(ui, self.facility.a2p2client.getUsername(), api, containerId, acqTSF, constraints, OBJTYPE, BASELINE, instrumentMode, target, DIAMETER, COU_AG_GSSOURCE, GSRA, GSDEC, COU_GS_MAG, dualField, SEQ_FT_ROBJ_NAME, SEQ_FT_ROBJ_MAG, SEQ_FT_ROBJ_DIAMETER, SEQ_FT_ROBJ_VIS, LSTINTERVAL)
                ui.addToLog(target.name + " submitted on p2")
        #endfor
        if doFolder:
            containerId = parentContainerId
            doFolder = False

    def submitOB(self, ob, p2container):
        self.checkOB(ob, p2container, False)


    def createGravityOB(self,ui, username, api, containerId, acqTSF, obConstraints, OBJTYPE, BASELINE, instrumentMode, obTarget, 
                        DIAMETER, COU_AG_GSSOURCE, GSRA, GSDEC, COU_GS_MAG, dualField, SEQ_FT_ROBJ_NAME, SEQ_FT_ROBJ_MAG,
                        SEQ_FT_ROBJ_DIAMETER, SEQ_FT_ROBJ_VIS, LSTINTERVAL):
        ui.setProgress(0.1)

        # TODO compute value
        VISIBILITY = 1.0

        #everything seems OK
        #create new OB in container:
        goodName = re.sub('[^A-Za-z0-9]+', '_', obTarget.name)
        OBS_DESCR = OBJTYPE[0:3] + '_' + goodName + '_GRAVITY_' + BASELINE.replace(' ', '') + '_' + instrumentMode

        ob, obVersion = api.createOB(containerId, OBS_DESCR)
        obId = ob['obId']

        #we use obId to populate OB
        ob['obsDescription']['name'] = OBS_DESCR[0:min(len(OBS_DESCR), 31)]
        ob['obsDescription']['userComments'] = 'Generated by ' + username + ' using ASPRO 2 (c) JMMC on '+ datetime.datetime.now().isoformat()
        #ob['obsDescription']['InstrumentComments'] = 'AO-B1-C2-E3' #should be a list of alternative quadruplets!

        # copy target info
        targetInfo = obTarget.getDict()
        for key in targetInfo:
            ob['target'][key] = targetInfo[key]

        #copy constraints info
        constraints = obConstraints.getDict() 
        for k in constraints:
            ob['constraints'][k] = constraints[k]

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

        # then, attach acquisition template(s)
        tpl, tplVersion = api.createTemplate(obId, self.getAcqTemplateName(dualField=dualField))
        
        # and put values        
        if dualField:                
            tpl, tplVersion = api.setTemplateParams(obId, tpl, {
                                                    'SEQ.FT.ROBJ.NAME': SEQ_FT_ROBJ_NAME,
                                                    'SEQ.FT.ROBJ.MAG': round(SEQ_FT_ROBJ_MAG, 3),
                                                    'SEQ.FT.ROBJ.DIAMETER': SEQ_FT_ROBJ_DIAMETER,
                                                    'SEQ.FT.ROBJ.VIS':  SEQ_FT_ROBJ_VIS,
                                                    'SEQ.FT.MODE':      "AUTO",
                                                    'SEQ.INS.SOBJ.NAME': acqTSF.SEQ_INS_SOBJ_NAME,
                                                    'SEQ.INS.SOBJ.MAG': acqTSF.SEQ_INS_SOBJ_MAG,
                                                    'SEQ.INS.SOBJ.DIAMETER':   DIAMETER,
                                                    'SEQ.INS.SOBJ.VIS':   VISIBILITY,
                                                    'SEQ.INS.SOBJ.X': diff[0],
                                                    'SEQ.INS.SOBJ.Y': diff[1],
                                                    'SEQ.FI.HMAG':   acqTSF.SEQ_FI_HMAG,
                                                    'TEL.TARG.PARALLAX':   0.0,
                                                    'INS.SPEC.RES': acqTSF.INS_SPEC_RES,
                                                    'INS.FT.POL': acqTSF.INS_FT_POL,
                                                    'INS.SPEC.POL':  acqTSF.INS_SPEC_POL,
                                                    'COU.AG.GSSOURCE':   COU_AG_GSSOURCE,
                                                    'COU.AG.ALPHA':   GSRA,
                                                    'COU.AG.DELTA':   GSDEC,
                                                    'COU.GS.MAG':  round(COU_GS_MAG, 3),
                                                    'COU.AG.PMA':  acqTSF.COU_AG_PMA,
                                                    'COU.AG.PMD':  acqTSF.COU_AG_PMD
                                                    }, tplVersion)
        else:
            tpl, tplVersion = api.setTemplateParams(obId, tpl, {
                                                    'SEQ.INS.SOBJ.NAME':   acqTSF.SEQ_INS_SOBJ_NAME,
                                                    'SEQ.INS.SOBJ.MAG':   acqTSF.SEQ_INS_SOBJ_MAG,
                                                    'SEQ.INS.SOBJ.DIAMETER':   DIAMETER,
                                                    'SEQ.INS.SOBJ.VIS':   VISIBILITY,
                                                    'COU.AG.GSSOURCE':   COU_AG_GSSOURCE,
                                                    'COU.AG.ALPHA':   GSRA,
                                                    'COU.AG.DELTA':   GSDEC,
                                                    'COU.GS.MAG':  round(COU_GS_MAG, 3),
                                                    'COU.AG.PMA':  acqTSF.COU_AG_PMA,
                                                    'COU.AG.PMD':  acqTSF.COU_AG_PMD,
                                                    'SEQ.FI.HMAG':   acqTSF.SEQ_FI_HMAG,
                                                    'TEL.TARG.PARALLAX':   0.0,
                                                    'INS.SPEC.RES': acqTSF.INS_SPEC_RES,
                                                    'INS.FT.POL': acqTSF.INS_FT_POL,
                                                    'INS.SPEC.POL':  acqTSF.INS_SPEC_POL
                                                    }, tplVersion)
        
        

        templateId = tpl['templateId']

        ui.setProgress(0.3)

        tpl, tplVersion = api.createTemplate(obId, self.getObsTemplateName(OBJTYPE, dualField))
        templateId = tpl['templateId']

        ui.setProgress(0.4)

        # put values. they are the same except for dual obs science (?)
        if dualField and OBJTYPE == 'SCIENCE':
            tpl, tplVersion = api.setTemplateParams(obId, tpl, {
                                                    'DET2.DIT':  str(dit),
                                                    'DET2.NDIT.OBJECT':  ndit,
                                                    'DET2.NDIT.SKY':  ndit,
                                                    'SEQ.OBSSEQ':  my_sequence,
                                                    'SEQ.SKY.X':  2000,
                                                    'SEQ.SKY.Y':  2000
                                                    }, tplVersion)
        else:
            tpl, tplVersion = api.setTemplateParams(obId, tpl, {
                                                    'DET2.DIT':  str(dit),
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