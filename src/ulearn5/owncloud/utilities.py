from five import grok
from zope.interface import Interface
from plone import api
from ulearn5.owncloud.api.owncloud import Client
from ulearn5.owncloud.interfaces import IUlearn5OwncloudLayer
from Products.CMFPlone import PloneMessageFactory as _
import logging


logger = logging.getLogger("ulearn5/owncloud/utilities.py")


class IOwncloudClient(Interface):
    """ Marker for OwncloudClient global utility """


class OwncloudClient(object):
    grok.implements(IOwncloudClient)
    grok.layer(IUlearn5OwncloudLayer)

    def __init__(self):
        self._client = None
        self._adminclient = None

    def __call__(self):
        return self.connection, self.admin_connection

    def create_new_connection(self, user, password):
        self.es_url = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_url')
        self._client = Client(self.es_url)
        try:
            self._client.login(user, password)
        except:
            message = _(u"your user or password does not exists in OwnCloud server. Or server url is wrong configured.")
            logger.error(message)

    def create_new_connection_admin(self, user, password):
        self.es_url = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_url')
        self._adminclient = Client(self.es_url)
        try:
            self._adminclient.login(user, password)
        except:
            message = _(u"admin user or admin password or server url is wrong configured in OwnCloud controlpanel.")
            logger.error(message)

    @property
    def connection(self):
        self._client._session = None
        if self._client._session is None:
            message = _(u"your client session with OwnCloud server is not ready, please, do logout and login again.")
            logger.error(message)
        return self._client

    @property
    def admin_connection(self):
        if self._adminclient is None:
            # Connect admin user with OwnCloud in WebDAV mode
            username = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_username')
            password = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_password')
            self.create_new_connection_admin(username, password)
        return self._adminclient

grok.global_utility(OwncloudClient)
