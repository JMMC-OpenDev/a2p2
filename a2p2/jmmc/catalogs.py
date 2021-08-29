#!/usr/bin/env python

__all__ = []

import logging

from .utils import JmmcAPI

logger = logging.getLogger(__name__)


PRODLABEL = {True: "production", False: "pre-prod"}


class Catalog():
    """ Get remote access to read and update catalogs exposed through JMMC's API """

    # TODO move preprod toggle False by default
    def __init__(self, catalogName, username=None, password=None, preprod=True):
        """ Init a catalog wrapper given its name.
        Credential can be explicitly given else .netrc file will be used on 401.
        """

        self.catalogName = catalogName
        self.prod = not(preprod)
        # TODO manage here prod & preprod access points
        self.api = JmmcAPI("https://oidb-beta.jmmc.fr/restxq/catalogs", username, password)

        logger.info("Create catalog wrapper to access '%s' (%s API at %s)" %
                    (catalogName, PRODLABEL[self.prod], self.api.rootURL))

    def list(self):
        """ Get list of exposed catalogs """
        return self.api._get("")

    def metadata(self):
        """ Get catalog metadata """
        return self.api._get("/meta/%s" % self.catalogName)

    def getPis(self):
        """ Get PIs from catalog and check for associated JMMC login """
        return self.api._get("/accounts/%s" % self.catalogName)

    def getRow(self, id):
        """ Get a single catalog record.
             usage: cat.getRow(42)
        """
        return self.api._get("/%s/%s" % (self.catalogName, id))

    def updateRow(self, id, values):
        """ update record identified by id with given values.
            usage: cat.updateCatalogRows(42, {"col_a":"a", "col_b":"b" })
        """
        return self.api._put("/%s/%s" % (self.catalogName, id), values)

    def updateRows(self, values):
        """ Update multiple rows.
        Values must contain a list of dictionnary and each entry must contains id key among other columns.
            usage: updateCatalogRows(
                "foo", [ { "id":42, "col_a":"a" }, { "id":24, "col_b":"b" } ])
        """
        return self.api._put("/%s" % (self.catalogName), values)
