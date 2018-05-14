# -*- coding: utf-8 -*-
from five import grok
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import alsoProvides

from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone import api
from plone.app.contenttypes.interfaces import IFolder

from ulearn5.core.content.community import ICommunity, ICommunityACL

from ulearn5.owncloud.utils import get_domain, update_owncloud_permission
from ulearn5.owncloud.utilities import IOwncloudClient
from ulearn5.owncloud.api.owncloud import HTTPResponseError, OCSResponseError

import logging
logger = logging.getLogger(__name__)


class createCommunitiesInOwncloudIfNotExists(grok.View):
    """ Aquesta vista replica l'estructura de carpetes i assigna permisos de les comunitats en owncloud """
    grok.name('migrate2owncloud')
    grok.context(IPloneSiteRoot)
    grok.require('cmf.ManagePortal')

    def render(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass
        domain = get_domain()
        pc = api.portal.get_tool('portal_catalog')
        communities = pc.unrestrictedSearchResults(portal_type='ulearn.community')

        for brain in communities:
            obj = brain.getObject()
            remote_path = domain + '/' + obj.id

            client = getUtility(IOwncloudClient)
            session = client.admin_connection()
            try:
                session.file_info(remote_path)
            except OCSResponseError:
                pass
            except HTTPResponseError as err:
                if err.status_code == 404:
                    logger.warning("La comunitat {} no existeix a owncloud".format(remote_path))
                    logger.warning("Creant i replicant tota l'estructura de {} a owncloud".format(remote_path))

                    community_path = '/' + obj.virtual_url_path()
                    community_tree = pc.unrestrictedSearchResults(path=community_path, sort_on='path')
                    for brain in community_tree:
                        element = brain._unrestrictedGetObject()
                        if IFolder.providedBy(element) or ICommunity.providedBy(element):
                            portal = getSite()
                            ppath = element.getPhysicalPath()
                            relative = ppath[len(portal.getPhysicalPath()):]
                            path = "/".join(relative)
                            session.mkdir(domain + '/' + path)

            acl = ICommunityACL(obj)().attrs.get('acl', '')
            update_owncloud_permission(obj, acl)
            logger.warning("Estructura replicada per {} a owncloud".format(remote_path))
