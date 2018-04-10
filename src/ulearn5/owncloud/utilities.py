from five import grok
from zope.interface import Interface
from plone import api
from zope.component import getUtility
from ulearn5.owncloud.api.owncloud import Client


class IOwncloudClient(Interface):
    """ Marker for OwncloudClient global utility """


class OwncloudClient(object):
    grok.implements(IOwncloudClient)

    def __init__(self):
        self._client = None

    def __call__(self):
        return self.connection

    def create_new_connection(self, user, password):
        self.es_url = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_url')
        self._client = Client(self.es_url)
        try:
            self._client.login(user, password)
        except:
            pass

    @property
    def connection(self):
        if self._client._session is None:
            pass
            #Falta ver que hacemos cuando no tenemos user y password (que no se ha creado la conecxion al hacer login)
            #self.create_new_connection(user, password)
        return self._client

grok.global_utility(OwncloudClient)
