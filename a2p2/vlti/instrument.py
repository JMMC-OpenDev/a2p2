#!/usr/bin/env python

__all__ = []

import os
import json
import collections
from a2p2.apis import Instrument
from a2p2.vlti.gui import VltiUI

# define the list of KEYWORD so we avoid typo using only constants
KW_INS_SPEC_RES="INS.SPEC.RES"



class VltiInstrument(Instrument):
    def  __init__(self, facility, insname):
        Instrument.__init__(self, facility, insname)
        self.facility = facility
        self.ui = facility.ui
        
        # use in latter lazy initialisation
        self.rangeTable = None
        self.ditTable = None
    
    def get(self, obj, fieldname, defaultvalue):
        if fieldname in obj._fields:
            return getattr(obj,fieldname)
        else:
            return defaultvalue
    
    def getCoords(self, target, requirePrecision=True):
        """ 
        Format coordinates from given target to be VLTI conformant. 
        Throws an exception if requirePrecision is true and given inputs have less than 3 (RA) or 2 (DEC) digits.
        """
        
        NAME = target.name
        
        RA = target.RA
        w = RA.rfind('.')
        l = len(RA)
        if l-w < 4 and requirePrecision:
            raise ValueError ("Object " + NAME + " has a too low precision in RA to be useable by VLTI, please correct with 3 or more digits.")
        if l-w > 4:
            RA = RA[0:w + 4]
            
        DEC = target.DEC
        w = DEC.rfind('.')
        l = len(DEC)
        if l-w < 3 and requirePrecision:
            raise ValueError ("Object " + NAME + " has a too low precision in DEC to be useable by VLTI,please correct with 2 or more digits.")
        if l-w > 4:
            DEC = DEC[0:w + 4]
            
        return RA, DEC
    
    def getPMCoords(self, target, defaultPMRA=0.0, defaultPMDEC=0.0):
        """
        Returns PMRA, PMDEC as float values. 0.0 is used as default if not present.
        """
        PMRA = self.get(target, "PMRA", defaultPMRA) 
        PMDEC = self.get(target, "PMDEC", defaultPMDEC)
        return float(PMRA), float(PMDEC)
    
    

# -- https://www.eso.org/sci/facilities/paranal/instruments/gravity/doc/Gravity_TemplateManual.pdf

#rangeTable = {}

#k = 'GRAVITY_gen_acq.tsf'
# using collections.OrderedDict to keep the order of keys:
#rangeTable[k] = collections.OrderedDict({})
#rangeTable[k]['SEQ.FI.HMAG']={'min':-10., 'max':20., 'default':0.0}
#...

    def getDitTable(self):
        if self.ditTable:
            return self.ditTable
        f = os.path.join(self.facility.getConfDir(),self.getName()+"_ditTable.json")
        self.ditTable = json.load(open(f))
        return self.ditTable
    
    def formatDitTable(self):
        ditTable = self.getDitTable()
        buffer = '    Mode     |Spec |  Pol  |Tel |       K       | DIT(s)\n'
        buffer +='--------------------------------------------------------\n'
        for tel in ['AT']:
            for spec in ['MED', 'HIGH']:
                for pol in ['OUT', 'IN']:
                    for i in range(len(ditTable[tel][spec][pol]['DIT'])):
                        buffer += 'Single Field | %4s | %3s | %2s |'%(spec, pol, tel)
                        buffer += ' %4.1f <K<= %3.1f | %4.1f'%(ditTable[tel][spec][pol]['MAG'][i],
                                                     ditTable[tel][spec][pol]['MAG'][i+1],
                                                     ditTable[tel][spec][pol]['DIT'][i])
                        buffer += "\n"                             
            buffer +=' Dual Field  |  all | all | %2s | Kdf = K - %.1f |  -'%(tel,ditTable[tel]['Kdf'])
            buffer += "\n"
        return buffer
        
    def getDit(self, tel, spec, pol, K, dualFeed=False):
        """
        finds DIT according to ditTable and K magnitude K

        'tel' in ditTable.keys()
        'spec' in ditTable[tel].keys()
        'pol' in ditTable[tel][spec].keys()

        * does not manage out of range (returns None) *
        """
        ditTable = self.getDitTable()
        mags = ditTable[tel][spec][pol]['MAG']
        dits = ditTable[tel][spec][pol]['DIT']
        if dualFeed:
            dK = ditTable[tel]['Kdf']
        else:
            dK = 0.0
        for i,d in enumerate(dits):
            if mags[i]<(K-dK) and (K-dK)<=mags[i+1]:
                return d
        return None
    
    def getRangeTable(self):        
        if self.rangeTable:
            return self.rangeTable
        f = os.path.join(self.facility.getConfDir(), self.getName()+"_rangeTable.json")
        # using collections.OrderedDict to keep the order of keys:
        self.rangeTable = json.load(open(f), object_pairs_hook=collections.OrderedDict)
        return self.rangeTable

    def isInRange(self, tpl, key, value):
        """
        check if "value" is in range of keyword "key" for template "tpl"

        ValueError raised if key or tpl is not found.
        """
        rangeTable = self.getRangeTable()
        _tpl = ''
        # -- find relevant range dictionnary
        for k in rangeTable.keys():
            if tpl in [l.strip() for l in k.split(',')]:
                _tpl = k
        if _tpl == '':
            raise ValueError('unknown template')
        tmp = rangeTable[_tpl]
        if not key in rangeTable[_tpl].keys():
            raise ValueError('unknown keyword')            
        if 'min' in rangeTable[_tpl][key].keys() and \
           'max' in rangeTable[_tpl][key].keys():
           return value>=rangeTable[_tpl][key]['min'] and\
                  value<=rangeTable[_tpl][key]['max']
        if 'list' in rangeTable[_tpl][key].keys():
            return value in rangeTable[_tpl][key]['list']
        if 'spaceseparatedlist' in rangeTable[_tpl][key].keys():
            for e in value.split(" "):
                if not e in rangeTable[_tpl][key]['spaceseparatedlist']:
                    return False
            return True
        
    def getRange(self, tpl, key):
        """
        returns range of keyword "key" for template "tpl"

        ValueError raised if key or tpl is not found.
        """
        rangeTable = self.getRangeTable()
        _tpl = ''
        # -- find relevant range dictionnary
        for k in rangeTable.keys():
            if tpl in [l.strip() for l in k.split(',')]:
                _tpl = k
        if _tpl == '':
            raise ValueError('unknown template')
        tmp = rangeTable[_tpl]
        if not key in rangeTable[_tpl].keys():
            raise ValueError('unknown keyword')            
        if 'min' in rangeTable[_tpl][key].keys() and \
           'max' in rangeTable[_tpl][key].keys():
           return (rangeTable[_tpl][key]['min'], rangeTable[_tpl][key]['max'])
        if 'list' in rangeTable[_tpl][key].keys():
            return rangeTable[_tpl][key]['list']
        if 'spaceseparatedlist' in rangeTable[_tpl][key].keys():
            for e in value.split(" "):
                return rangeTable[_tpl][key]['spaceseparatedlist']

    def formatRangeTable(self):
        rangeTable = self.getRangeTable()
        buffer = ""
        for l in rangeTable.keys():
            buffer += l + "\n"
            for k in rangeTable[l].keys():
                constraint = rangeTable[l][k]
                keys = constraint.keys()
                buffer += ' %30s :' % ( k )
                if 'min' in keys and 'max' in keys:
                    buffer += ' %f ... %f ' % ( constraint['min'], constraint['max'])
                elif 'list' in keys:
                    buffer += str(constraint['list'])
                elif "spaceseparatedlist" in keys:
                    buffer += ' ' + " ".join(constraint['spaceseparatedlist'])
                if 'default' in keys:
                    buffer += ' (' + str(constraint['default']) + ')'
                else:
                    buffer +=' -no default-'
                buffer += "\n"
        return buffer
                    
    def getSkyDiff(ra, dec, ftra, ftdec):
        science = SkyCoord(ra, dec, frame='icrs', unit='deg')
        ft = SkyCoord(ftra, ftdec, frame='icrs', unit='deg')
        ra_offset = (science.ra - ft.ra) * np.cos(ft.dec.to('radian'))
        dec_offset = (science.dec - ft.dec)
        return [ra_offset.deg * 3600 * 1000, dec_offset.deg * 3600 * 1000] #in mas
     
    def getHelp(self):
        s  = self.getName()
        s += "\n\nRangeTable:\n"
        s += self.formatRangeTable()
        s += "\n\nDitTable:\n"
        s += self.formatDitTable()
        return s
    
    
class TSF:
    def __init__(self, instrument, tpl):
        self.tpl = tpl
        self.instrument = instrument
        supportedTpl = instrument.getRangeTable().keys()
        if tpl not in supportedTpl:
            raise ValueError ("template '%s' is not in the instrument range table. Must be one of %s" % (tpl, str(supportedTpl)))
        self.tsfParams = {}
        
    def set(key, value, checkRange=True):
        if checkKeyword:
            if not self.instrument.isInRange(self.tpl, key, value):
                raise ValueError("Parameter value (%s) is out of range for keyword %s in template %s "%(str(value), key, self.tpl))
        self.tsfParams[key] = value
        
    # TODO new method to complete with default walking to every non set keywords and using range table
        