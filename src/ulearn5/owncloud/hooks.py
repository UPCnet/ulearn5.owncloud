# -*- coding: utf-8 -*-
from five import grok
from Acquisition import aq_chain
from zope.component import getUtility

from zope.component.hooks import getSite
from zope.container.interfaces import IObjectAddedEvent

from Products.CMFCore.utils import getToolByName

from ulearn5.core.interfaces import IAppImage
from ulearn5.core.interfaces import IAppFile
from ulearn5.core.content.community import ICommunity

from mrs5.max.utilities import IMAXClient
from plone import api
from souper.soup import get_soup
from souper.soup import Record
from repoze.catalog.query import Eq
from DateTime.DateTime import DateTime
from zope.component import providedBy
from plone.app.workflow.interfaces import ILocalrolesModifiedEvent
from Products.CMFPlone.interfaces import IConfigurationChangedEvent
from Products.PluggableAuthService.interfaces.events import IUserLoggedInEvent
from zope.globalrequest import getRequest

import logging

logger = logging.getLogger(__name__)

from ulearn5.owncloud.utilities import IOwncloudClient
from zope.component import getUtility
from ulearn5.owncloud.api.owncloud import ResponseError, HTTPResponseError, OCSResponseError
from ulearn5.owncloud.interfaces import IUlearn5OwncloudLayer
from ulearn5.owncloud.api.owncloud import Client


@grok.subscribe(ICommunity, IObjectAddedEvent)
def communityAdded(content, event):
    """ A folder is created in OwnCloud
        with the same name as the community
    """
    client = getUtility(IOwncloudClient)
    valor = client.admin_connection()
    try:
        valor.file_info('UPC/' + content.id)
    except OCSResponseError:
        pass
    except HTTPResponseError as err:
        if err.status_code == 404:
            #Para crear carpetas
            valor.mkdir('UPC/' + content.id)
            valor.mkdir('UPC/' + content.id + '/Documents')
            valor.mkdir('UPC/' + content.id + '/Documents' + '/Media')

            #Para añadir permisos a un usuario
            valor.share_file_with_user('UPC/' + content.id, 'carles.bruguera') #Lector
            valor.share_file_with_user('UPC/' + content.id, 'pilar.marinas', perms=Client.OCS_PERMISSION_EDIT) #Editor
            valor.share_file_with_user('UPC/' + content.id, 'victor', perms=Client.OCS_PERMISSION_ALL) #Propietari
            # import ipdb;ipdb.set_trace()

            #Para ver los permisos de una comunidad "content.id" es el objecto que creo en este caso comunidad
            valor.get_shares('UPC/' + content.id)
            #Se tendran que recorrer los permisos y modificar los que hagan falta.
            #Se tiene que pasar el id del permiso a modificar que se obtiene asi
            valor.get_shares('UPC/' + content.id)[0].get_id()
            share = valor.get_shares('UPC/' + content.id)[0]
            #Para modificar el permiso de un usuario
            valor.update_share(share.get_id(), perms=Client.OCS_PERMISSION_EDIT)
            #Para borrar el permiso de un usuario
            #valor.delete_share(share.get_id())

        else:
            logger.warning('The community {} not has been creation in owncloud'.format(content.id))
            raise
