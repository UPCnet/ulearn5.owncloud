from five import grok
from zope.interface import Interface
from plone import api
from ulearn5.owncloud.api.owncloud import Client
from ulearn5.owncloud.interfaces import IUlearn5OwncloudLayer


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
            pass

    def create_new_connection_admin(self, user, password):
        self.es_url = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_url')
        self._adminclient = Client(self.es_url)
        try:
            self._adminclient.login(user, password)
        except:
            pass

    @property
    def connection(self):
        if self._client._session is None:
            pass
            #Falta ver que hacemos cuando no tenemos user y password (que no se ha creado la conecxion al hacer login)
            #self.create_new_connection(user, password)
        return self._client

    @property
    def admin_connection(self):
        if self._adminclient._session is None:
            pass
            #Falta ver que hacemos cuando no tenemos user y password (que no se ha creado la conecxion al hacer login)
            #self.create_new_connection(user, password)
        return self._adminclient

grok.global_utility(OwncloudClient)
