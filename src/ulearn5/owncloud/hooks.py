# -*- coding: utf-8 -*-
from five import grok
from plone import api
from plone.app.contenttypes.interfaces import IFolder
from plone.app.layout.navigation.root import getNavigationRootObject
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from ulearn5.core.content.community import ICommunity
from ulearn5.core.utils import is_activate_owncloud
from ulearn5.owncloud.api.owncloud import HTTPResponseError
from ulearn5.owncloud.api.owncloud import OCSResponseError
from ulearn5.owncloud.content.file_owncloud import IFileOwncloud
from ulearn5.owncloud.utilities import IOwncloudClient
from ulearn5.owncloud.utils import get_domain
from zope.component import getUtility
from zope.container.interfaces import IObjectAddedEvent
from zope.container.interfaces import IObjectRemovedEvent
from zope.lifecycleevent import IObjectMovedEvent

import logging


logger = logging.getLogger(__name__)


@grok.subscribe(IFolder, IObjectAddedEvent)
def folderAdded(content, event):
    """Folder is created in OwnCloud."""
    if IPloneSiteRoot.providedBy(event.object):
        pass
    else:
        portal = api.portal.get()
        if is_activate_owncloud(portal):
            portal_state = content.unrestrictedTraverse('@@plone_portal_state')
            root = getNavigationRootObject(content, portal_state.portal())
            ppath = content.getPhysicalPath()
            relative = ppath[len(root.getPhysicalPath()):]
            path = "/".join(relative)
            is_in_community = False
            for p in range(len(relative)):
                now = relative[:p + 1]
                obj = root.unrestrictedTraverse(now)
                if ICommunity.providedBy(obj):
                    # Creem carpeta a OwnCloud
                    is_in_community = True
                    client = getUtility(IOwncloudClient)
                    session = client.admin_connection()
                    try:
                        domain = get_domain()
                        session.mkdir(domain + '/' + path)
                    except OCSResponseError:
                        pass
                    except HTTPResponseError as err:
                        if err.status_code == 404:
                            logger.warning('The object {} has not been added in owncloud'.format(path))
                    break
            if not is_in_community:
                logger.warning('There is not necessary Add folder in OwnCloud because ICommunity is not provided')


@grok.subscribe(IFolder, IObjectRemovedEvent)
def folderRemoved(content, event):
    """Folder is removed in OwnCloud."""
    if IPloneSiteRoot.providedBy(event.object) or \
       ICommunity.providedBy(event.object) or \
       (IPloneSiteRoot.providedBy(content.aq_parent) and \
            not ICommunity.providedBy(event.object)):
        pass
    else:
        portal = api.portal.get()
        if is_activate_owncloud(portal):
            portal_state = content.unrestrictedTraverse('@@plone_portal_state')
            root = getNavigationRootObject(content, portal_state.portal())
            ppath = content.getPhysicalPath()
            relative = ppath[len(root.getPhysicalPath()):]
            path = "/".join(relative)
            is_in_community = False
            for pa in range(len(relative)):
                now = relative[:pa + 1]
                obj = root.unrestrictedTraverse(now)
                if ICommunity.providedBy(obj):
                    # Esborrem carpeta a OwnCloud
                    is_in_community = True
                    client = getUtility(IOwncloudClient)
                    session = client.admin_connection()
                    try:
                        domain = get_domain()
                        session.file_info(domain + '/' + path)
                        session.delete(domain + '/' + path)
                        break
                    except OCSResponseError:
                        pass
                    except HTTPResponseError as err:
                        if err.status_code == 404:
                            logger.warning('The object {} has not been removed in owncloud'.format(path))
                    break
            if not is_in_community:
                logger.warning('There is not necessary Remove folder in OwnCloud because ICommunity is not provided')


@grok.subscribe(IFolder, IObjectMovedEvent)
def folderMoved(content, event):
    """File is moved or copied in OwnCloud."""
    if IPloneSiteRoot.providedBy(event.object):
        pass
    else:
        portal = api.portal.get()
        if is_activate_owncloud(portal):
            portal_state = content.unrestrictedTraverse('@@plone_portal_state')
            root = getNavigationRootObject(content, portal_state.portal())
            oldParent = event.oldParent
            newParent = event.newParent
            if newParent is not None and oldParent is not None:
                domain = get_domain()
                # COPY / MOVE CASE
                old = oldParent.getPhysicalPath()
                origin_path = domain + "/" + "/".join(old[len(root.getPhysicalPath()):]) + "/" + content.id
                new = newParent.getPhysicalPath()
                target_path = domain + "/" + "/".join(new[len(root.getPhysicalPath()):]) + "/" + content.id
                client = getUtility(IOwncloudClient)
                session = client.admin_connection()
                try:
                    session.file_info(origin_path)
                    session.move(origin_path, target_path)
                except OCSResponseError:
                    pass
                except HTTPResponseError as err:
                    if err.status_code == 404:
                        logger.warning('The object {} has not been moved in owncloud'.format(origin_path))
            else:
            	# ADD, REMOVE OR OTHER CASE
            	pass


@grok.subscribe(IFileOwncloud, IObjectMovedEvent)
def fileMoved(content, event):
    """File is moved in OwnCloud."""
    portal = api.portal.get()
    if is_activate_owncloud(portal):
        portal_state = content.unrestrictedTraverse('@@plone_portal_state')
        root = getNavigationRootObject(content, portal_state.portal())
        oldParent = event.oldParent
        newParent = event.newParent
        if newParent is not None and oldParent is not None:
            domain = get_domain()
            # MOVE CASE
            old = oldParent.getPhysicalPath()
            origin_path = domain + "/" + "/".join(old[len(root.getPhysicalPath()):]) + "/" + content.id
            new = newParent.getPhysicalPath()
            target_path = domain + "/" + "/".join(new[len(root.getPhysicalPath()):]) + "/" + content.id

            client = getUtility(IOwncloudClient)
            session = client.admin_connection()
            try:
                session.file_info(origin_path)
                session.move(origin_path, target_path)
            except OCSResponseError:
                pass
            except HTTPResponseError as err:
                if err.status_code == 404:
                    logger.warning('The object {} has not been moved in owncloud'.format(origin_path))
        else:
            # ADD, REMOVE OR OTHER CASE
            pass


@grok.subscribe(IFileOwncloud, IObjectAddedEvent)
def fileCopied(content, event):
    """File is copied in OwnCloud."""
    portal = api.portal.get()
    if is_activate_owncloud(portal):
        root = api.portal.get()
        if content.fileid is not None:
            domain = get_domain()
            # COPY CASE
            new = content.getPhysicalPath()
            target_path = domain + "/" + "/".join(new[len(root.getPhysicalPath()):])

            origin_path = ""
            pc = api.portal.get_tool(name='portal_catalog')
            results = pc.searchResults(portal_type='CloudFile', fileid=content.fileid)
            for r in results:
                path = tuple(r.getPath().split('/'))
                if new != path:
                    # Hemos encontrado el objeto de origen
                    origin_path = domain + "/" + "/".join(path[len(root.getPhysicalPath()):])

            client = getUtility(IOwncloudClient)
            session = client.admin_connection()
            try:
                session.file_info(origin_path)
                session.copy(origin_path, target_path)
                info_file = session.file_info(target_path)
                newfileid = info_file.attributes.get('{http://owncloud.org/ns}fileid')

                # Save the fileid owncloud in plone file
                content.fileid = newfileid
                content.reindexObject()
            except OCSResponseError:
                pass
            except HTTPResponseError as err:
                if err.status_code == 404:
                    logger.warning('The object {} has not been copied in owncloud'.format(origin_path))
        else:
            # ADD CASE
            pass


@grok.subscribe(IFileOwncloud, IObjectRemovedEvent)
def fileRemoved(content, event):
    """File is removed in OwnCloud."""
    portal = api.portal.get()
    if is_activate_owncloud(portal):
        portal_state = content.unrestrictedTraverse('@@plone_portal_state')
        root = getNavigationRootObject(content, portal_state.portal())
        ppath = content.getPhysicalPath()
        relative = ppath[len(root.getPhysicalPath()):]
        path = "/".join(relative)
        client = getUtility(IOwncloudClient)
        session = client.admin_connection()
        try:
            domain = get_domain()
            session.file_info(domain + '/' + path)
            session.delete(domain + '/' + path)
        except OCSResponseError:
            pass
        except HTTPResponseError as err:
            if err.status_code == 404:
                logger.warning('The object {} has not been removed in owncloud'.format(path))
