#!/usr/bin/env python

__all__ = []

import json
import logging

from .utils import JmmcAPI

logger = logging.getLogger(__name__)


#
# first release done for SAMP interoperability with Aspro2
#


def _model(models, output_mode=None):
    """ Returns a serialisation of given model(s) to XML by default or another format given to output_mode value (only jsonlike at present time)."""

    # deserialize if models is a string
    if isinstance(models, str):
        models=json.loads(models)

    if output_mode:
        return models
    else :
        return _xml_model(models)

def _xml_model(models):
    """ Rough conversion of dict(s) to xml (Aspro2 namespaces)"""

    if isinstance(models, list):
        modellist=[]
        for m in models:
            modellist.append(_xml_model(m))
        return "".join(modellist)

    model = models # models is now a single element
    modeltype=model["type"]
    modelname=model["name"]

    params=""
    paramNames=[ k for k in model.keys() if not k in ("type", "name")]
    # at present time we must use Aspro2's approach with the same xml namespaces
    # see
    for p in paramNames:
        params+=f"""    <tm:parameter name="{modelname}_{p}" type="{p}"><value>{model[p]}</value></tm:parameter>\n"""

    return f"""<tm:model name="{modelname}" type="{modeltype}">\n{params}</tm:model>\n"""


class Models():
    """ Get analytical model's representations (in sync with Aspro2's ones).
    """
    SAMP_UCD_MODEL="meta.code.class;meta.modelled" # use it for colums that would be filled by models below

# generated code below from an Asprox file that contains a single star with list of all supported models
# cd a2p2/jmmc
# xml sel -o "from .models import _model" -n -n -b -t -m "//tm:model" -o "def " -v "@type" -o "( name, " -m "tm:parameter" -v "@type" -o "=" -v "value" -o ", " -b -o " output_mode=None):" -n -o '    """ ' -v "desc" -o ' """ ' -n -n -o '    return _model({' -m "tm:parameter" -o '"' -v "@type" -o '" : ' -v "@type" -o ", " -b -o '"name":name, "type":"' -v "@type" -o '"}, output_mode)' -n -n models_template.asprox > generated_models.py
# xml sel -t -o "    from .generated_models import " -m "//tm:model" -v "@type" -o ", "  -b -n models_template.asprox
# cd -
    from .generated_models import punct, disk, elong_disk, flatten_disk, circle, ring, elong_ring, flatten_ring, gaussian, elong_gaussian, flatten_gaussian, limb_quadratic
