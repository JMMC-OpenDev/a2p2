#!/usr/bin/env python

__all__ = []

class Instrument():
    def __init__(self, facility, insname, help="Help TBD"):
        self.facility=facility
        self.insname=insname
        self.help=help
        facility.registerInstrument(self)

    def getName(self):
        return self.insname

    def getHelp(self):
        return self.help
