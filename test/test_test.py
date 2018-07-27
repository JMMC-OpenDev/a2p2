#!/usr/bin/env python
# Tested on GITHub/Travis
# on your machine, just run pytest in this directory or execute it to get outputs
#

import xml.etree.ElementTree as ET
import json
from collections import defaultdict,namedtuple
import os

from a2p2.ob import OB

def test_obs():
    for root, dirs, files in os.walk("."):
        for file in files:
            if ".obxml" in file:
               check_obs(os.path.join(root, file))

def check_obs(path):
    ob = OB(path)
    print("checking OB at %s location"%path)
    for obsc in ob.observationConfiguration:
        print("obsConfig.id=%s"%obsc.id)
    for obss in ob.observationSchedule.OB:
        print("obsSchedule.ref=%s"%str(obss.ref))
        
    print (ob)
    print("\n\n")
    assert True

test_obs()
