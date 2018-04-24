# -*- coding: utf-8 -*-
from five import grok
from zope.component import getUtility
from zope.container.interfaces import IObjectAddedEvent, IObjectRemovedEvent
from zope.lifecycleevent import IObjectMovedEvent, IObjectCopiedEvent

from plone.app.layout.navigation.root import getNavigationRootObject
from plone.app.contenttypes.interfaces import IFolder
from plone import api

from ulearn5.core.utils import is_activate_owncloud
from ulearn5.core.content.community import ICommunity
from ulearn5.owncloud.utilities import IOwncloudClient
from ulearn5.owncloud.api.owncloud import HTTPResponseError, OCSResponseError
from ulearn5.owncloud.content.file_owncloud import IFileOwncloud

import logging
logger = logging.getLogger(__name__)


#@grok.subscribe(ICommunity, IObjectAddedEvent)
# def communityAdded(content, event):
#     """ A folder is created in OwnCloud
#         with the same name as the community
#         by the admin owncloud
#     """
#     client = getUtility(IOwncloudClient)
#     valor = client.admin_connection()
#     # Create structure folders community in domain
#     domain = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_domain')
#     import ipdb; ipdb.set_trace()
#     try:
#         valor.file_info(domain.lower() + content.id)
#     except OCSResponseError:
#         pass
#     except HTTPResponseError as err:
#         if err.status_code == 404:
#             valor.mkdir(domain.lower() + '/' + content.id)
#             #valor.mkdir(domain.lower() + '/' + content.id + '/documents')
#             #valor.mkdir(domain.lower() + '/' + content.id + '/documents' + '/media')
#             # Assign owner permissions
#             current = api.user.get_current()
#             valor.share_file_with_user(domain.lower() + '/' + content.id, current.id , perms=Client.OCS_PERMISSION_ALL) #Propietari
#             # Para añadir permisos a un usuario
#             # valor.share_file_with_user('UPC/' + content.id, 'carles.bruguera') #Lector
#             # valor.share_file_with_user('UPC/' + content.id, 'pilar.marinas', perms=Client.OCS_PERMISSION_EDIT) #Editor
#             # valor.share_file_with_user('UPC/' + content.id, 'victor', perms=Client.OCS_PERMISSION_ALL) #Propietari
#             # Para ver los permisos de una comunidad "content.id" es el objecto que creo en este caso comunidad
#             # valor.get_shares('UPC/' + content.id)
#             # Se tendran que recorrer los permisos y modificar los que hagan falta.
#             # Se tiene que pasar el id del permiso a modificar que se obtiene asi
#             # valor.get_shares('UPC/' + content.id)[0].get_id()
#             # share = valor.get_shares('UPC/' + content.id)[0]
#             # Para modificar el permiso de un usuario
#             # valor.update_share(share.get_id(), perms=Client.OCS_PERMISSION_EDIT)
#             # Para borrar el permiso de un usuario
#             # valor.delete_share(share.get_id())
#         else:
#             logger.warning('The community {} not has been creation in owncloud'.format(content.id))
#             raise


@grok.subscribe(IFolder, IObjectAddedEvent)
def folderAdded(content, event):
    """Folder is created in OwnCloud."""
    portal = api.portal.get()
    if is_activate_owncloud(portal):
        portal_state = content.unrestrictedTraverse('@@plone_portal_state')
        root = getNavigationRootObject(content, portal_state.portal())
        ppath = content.getPhysicalPath()
        relative = ppath[len(root.getPhysicalPath()):]
        for p in range(len(relative)):
            now = relative[:p + 1]
            obj = root.unrestrictedTraverse(now)
            if ICommunity.providedBy(obj):
                # Creem carpeta a OwnCloud
                domain = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_domain')
                path = "/".join(relative)
                client = getUtility(IOwncloudClient)
                session = client.admin_connection()
                try:
                    session.mkdir(domain.lower() + '/' + path)
                except OCSResponseError:
                    pass
                except HTTPResponseError as err:
                    if err.status_code == 404:
                        logger.warning('The object {} has not been added in owncloud'.format(path))
            else:
                pass


@grok.subscribe(IFolder, IObjectRemovedEvent)
def folderRemoved(content, event):
    """Folder is removed in OwnCloud."""
    portal = api.portal.get()
    if is_activate_owncloud(portal):
        domain = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_domain')
        portal_state = content.unrestrictedTraverse('@@plone_portal_state')
        root = getNavigationRootObject(content, portal_state.portal())
        ppath = content.getPhysicalPath()
        relative = ppath[len(root.getPhysicalPath()):]
        path = "/".join(relative)
        client = getUtility(IOwncloudClient)
        session = client.admin_connection()
        try:
            session.file_info(domain.lower() + '/' + path)
            session.delete(domain.lower() + '/' + path)
        except OCSResponseError:
            pass
        except HTTPResponseError as err:
            if err.status_code == 404:
                logger.warning('The object {} has not been removed in owncloud'.format(path))


@grok.subscribe(IFileOwncloud, IObjectRemovedEvent)
def fileRemoved(content, event):
    """File is removed in OwnCloud."""
    portal = api.portal.get()
    if is_activate_owncloud(portal):
        domain = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_domain')
        portal_state = content.unrestrictedTraverse('@@plone_portal_state')
        root = getNavigationRootObject(content, portal_state.portal())
        ppath = content.getPhysicalPath()
        relative = ppath[len(root.getPhysicalPath()):]
        path = "/".join(relative)
        client = getUtility(IOwncloudClient)
        session = client.admin_connection()
        try:
            session.file_info(domain.lower() + '/' + path)
            session.delete(domain.lower() + '/' + path)
        except OCSResponseError:
            pass
        except HTTPResponseError as err:
            if err.status_code == 404:
                logger.warning('The object {} has not been removed in owncloud'.format(path))


@grok.subscribe(IFolder, IObjectMovedEvent)
def folderMoved(content, event):
    """File is moved or copied in OwnCloud."""
    portal = api.portal.get()
    if is_activate_owncloud(portal):
        portal_state = content.unrestrictedTraverse('@@plone_portal_state')
        root = getNavigationRootObject(content, portal_state.portal())
        oldParent = event.oldParent
        newParent = event.newParent
        if newParent is not None and oldParent is not None:
            domain = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_domain').lower()
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
            # ADD, REMOVE OR UNKNOWN CASE
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
            domain = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_domain').lower()
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
            # ADD, REMOVE OR UNKNOWN CASE
            pass


@grok.subscribe(IFileOwncloud, IObjectAddedEvent)
def fileCopied(content, event):
    """File is copied in OwnCloud."""
    portal = api.portal.get()
    if is_activate_owncloud(portal):
        root = api.portal.get()
        domain = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_domain').lower()
        if content.fileid is not None:
            # COPY CASE
            new = content.getPhysicalPath()
            target_path = domain + "/" + "/".join(new[len(root.getPhysicalPath()):])

            origin_path = ""
            pc = api.portal.get_tool(name='portal_catalog')
            results = pc.searchResults(portal_type='ulearn5.owncloud.file_owncloud', fileid=content.fileid)
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
