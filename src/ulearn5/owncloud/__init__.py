# -*- coding: utf-8 -*-
"""Init and utils."""
from zope.i18nmessageid import MessageFactory
import logging
from plone.app.layout.navigation.root import getNavigationRootObject
from zope.component import getUtility
from ulearn5.owncloud.utilities import IOwncloudClient
from ulearn5.owncloud.api.owncloud import HTTPResponseError, OCSResponseError


logger = logging.getLogger(__name__)

_ = MessageFactory('ulearn5.owncloud')


def objectRenamed(self, content, id_source, domain, username, password):
    """ A folder is renamed in OwnCloud """
    portal_state = content.unrestrictedTraverse('@@plone_portal_state')
    root = getNavigationRootObject(content, portal_state.portal())
    ppath = content.getPhysicalPath()
    path_source = "/".join(ppath[len(root.getPhysicalPath()):-1])
    origin_path = domain.lower() + '/' + path_source + '/' + id_source

    path_dest = "/".join(ppath[len(root.getPhysicalPath()):])
    target_path = domain.lower() + '/' + path_dest

    client = getUtility(IOwncloudClient)
    try:
        session = client.admin_connection()
    except:
        client.create_new_connection_admin(username, password)
        session = client.admin_connection()
    try:
        session.file_info(origin_path)
        session.move(origin_path, target_path)
    except OCSResponseError:
        pass
    except HTTPResponseError as err:
        if err.status_code == 404:
            logger.warning('The object {} has not been renamed in owncloud'.format(id_source))
            pass
