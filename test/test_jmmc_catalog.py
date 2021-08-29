#!/usr/bin/env python
# Tested on GITHub/Travis
# on your machine, just run pytest in this directory or execute it to get outputs
#

import pytest

from a2p2.jmmc import Catalog

def test_same_id():
    has_same_id("oidb", 38681)
def test_same_id2():
    has_same_id("oidb", 38682)


def has_same_id(catname, id):
    c = Catalog(catname)
    r = c.getRow(id)
    assert r["id"] == id
    print ("We are ok with catalog %s id %s"%(catname, id))
    return
