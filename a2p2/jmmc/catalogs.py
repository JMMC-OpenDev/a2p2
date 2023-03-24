#!/usr/bin/env python

__all__ = []

import logging

from ..client import A2P2ClientPreferences

from .utils import JmmcAPI
from . import PRODLABEL

logger = logging.getLogger(__name__)


class Catalog():
    """ Get remote access to read and update catalogs exposed through JMMC's API.
        Credential can be explicitly given for method that require an authentication, else:
        - a2p2 preferences login will be used if present (see a2p2 -c)
        - or uses .netrc file
    """

    def __init__(self, catalogName, username=None, password=None, prod=False, apiUrl=None):
        self.catalogName = catalogName
        self.prod = prod

        # Manage prod & preprod or user provided access points
        if apiUrl:
            self.apiUrl = apiUrl  # trust given url as catalogAPI if value is provided
        elif self.prod:
            self.apiUrl = "https://oidb.jmmc.fr/restxq/catalogs"
        else:
            self.apiUrl = "https://oidb-beta.jmmc.fr/restxq/catalogs"

        self.api = JmmcAPI(self.apiUrl, username, password)

        logger.info(f"Create catalog wrapper to access '{catalogName}' ({PRODLABEL[self.prod]} API at {self.api.rootURL})")

    def list(self):
        """ Get list of exposed catalogs on API associated to this catalog. """
        return self.api._get("")

    def metadata(self):
        """ Get catalog metadata """
        return self.api._get(f"/meta/{self.catalogName}")

    def pis(self):
        """ Get PIs from catalog and check for associated JMMC login in OiDB datapi table."""
        return self.api._get(f"/accounts/{self.catalogName}")["pi"]

    def piname(self, jmmcLogin=None):
        """ Get the piname associated to the given jmmcLogin.
            If jmmcLogin parameter is not provided, try to get jmmc.login preferences.
            Only pi names returned by pis() can be retrieved.

            usage: piname()
        """
        if not jmmcLogin:
            prefs = A2P2ClientPreferences()
            jmmcLogin = prefs.getJmmcLogin()
        if not jmmcLogin:
            raise Exception(
                "missing login parameter or jmmc.login preference.")
        pis = self.pis()
        for pi in pis:
            if "login" in pi and pi["login"] == jmmcLogin:
                return pi["name"]

    def getRow(self, id):
        """ Get a single catalog record for the given id.

            usage: cat.getRow(42)
        """
        return self.api._get(f"/{self.catalogName}/{id}")

    def updateRow(self, id, values):
        """ Update record identified by given id and associated values.

            usage: cat.updateRows(42, {"col_a":"a", "col_b":"b" })
        """
        return self.api._put(f"/{self.catalogName}/{id}", values)

    def updateRows(self, values):
        """ Update multiple rows.
            Values must contain a list of dictionnary and each entry must contains id key among other columns.

            usage: updateRows([ { "id":42, "col_a":"a" }, { "id":24, "col_b":"b" } ])
        """

        # We may check befere sending payload that we always provide an id for every record
        return self.api._put(f"/{self.catalogName}", values)

    def addRows(self, values):
        """ Add multiple rows.
            Values is an array of row to add. id column values will be ignored.

            usage: addCatalogRows([ { "id":42, "col_a":"a" }, { "id":24, "col_b":"b" } ])
        """
        return self.api._post(f"/{self.catalogName}", json=values)

    def getDelegations(self, pi=None):
        """ Get -all- delegations.
            A specific pi parameter may be given but requires admin priviledges. Else use current piname will be used by remote service.

            usage: getDelegations()
        """
        res = self.api._get(f"/delegations?pi={pi}")
        if "delegations" in res:
            return res["delegations"] # login and pi values not returned

        return []

    def updateDelegations(self, delegations):
        """ Update delegations according given array of delegations.
            A specific "pi" key may be given in delegations dict but requires admin privileges. Else current piname will be used by remote service.
            "action" may be provided with "add" or "remove" value to set proper delegations (default add given delegation).

            usage: addDelegations([{"pi":"mypiname", "catalogs":"mycats", "coi":["alice","bob"]}])

        """
        return self.api._put("/delegations", json=delegations)

    def removeDelegations(self, delegations):
        """ Remove delegations according given array of delegations.
            A specific pi key may be given but requires admin privileges. Else current piname will be used by remote service.
            usage: removeDelegations([{}, {}])
        """
        return "TODO"


