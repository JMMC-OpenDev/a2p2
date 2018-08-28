#!/usr/bin/env python

__all__ = []

from a2p2.apis import Instrument

from a2p2.vlti.gui import VltiUI

class VltiInstrument(Instrument):
    def  __init__(self, facility, insname):
        Instrument.__init__(self, facility, insname)
        self.facility = facility
        self.ui = facility.ui
    
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
        
        
        
        