# -*- coding: utf-8 -*-
from zope import schema
from plone.supermodel import model
from plone.app.registry.browser import controlpanel
from ulearn5.core import _
from zope.component import getUtility
from z3c.form import button
from plone import api
from Products.statusmessages.interfaces import IStatusMessage
from ulearn5.core.utils import is_activate_owncloud
from ulearn5.owncloud.utilities import IOwncloudClient
from ulearn5.owncloud.api.owncloud import HTTPResponseError, OCSResponseError
from ulearn5.owncloud.api.owncloud import Client


class IOCSettings(model.Schema):
    """ OwnCloud connector settings """

    connector_url = schema.TextLine(
        title=_(u'Connection URL of storage'),
        description=_(u'WebDAV: http://host:port/path/to/webdav,'
                      'Local filesystem: file://path/to/directory, '
                      'AWS S3: s3://bucketname, SFTP sftp://host/path, '
                      'FTP: ftp://host/path'),
        default=u'',
        required=True
        )

    connector_mode = schema.TextLine(
        title=_(u'Connector mode'),
        description=_(u'Connector mode (defaults to \'owncloud\')'),
        default=u'owncloud',
        required=False
        )

    connector_username = schema.TextLine(
        title=_(u'Username for manage OwnCloud'),
        default=u'ulearn.owncloud',
        required=True
        )

    connector_password = schema.Password(
        title=_(u'Password overriding the system settings'),
        required=True
        )

    connector_domain = schema.TextLine(
        title=_(u'Domain manage communities in OwnCloud'),
        default=u'upc',
        required=True
        )


class OCSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IOCSettings
    id = 'OCSettingsEditForm'
    label = _(u'OwnCloud Settings')
    description = _(u'')

    def updateFields(self):
        super(OCSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(OCSettingsEditForm, self).updateWidgets()

    @button.buttonAndHandler(_('Save'), name=None)
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)

        #import ipdb; ipdb.set_trace()
        if is_activate_owncloud(self):
            client = getUtility(IOwncloudClient)
            session = client.admin_connection()
            # Create structure folders community in domain
            #aa = data.get('domain')
            domain = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_domain')
            try:
                session.file_info(domain.lower())

            except OCSResponseError:
                IStatusMessage(self.request).addStatusMessage(_(u'The community {} not has been created in owncloud due to {}'.format(community.id, OCSResponseError)), 'error')

            except HTTPResponseError as err:
                if err.status_code == 404:
                    session.mkdir(domain.lower())
                    # Assign owner permissions
                    current = api.user.get_current()
                    # Propietari
                    session.share_file_with_user(domain.lower(), current.id, perms=Client.OCS_PERMISSION_ALL)
                else:
                    IStatusMessage(self.request).addStatusMessage(_(u'The community {} not has been created in owncloud due to {}'.format(community.id, OCSResponseError)), 'error')

        IStatusMessage(self.request).addStatusMessage(_(u'Changes saved'),
                                                      'info')
        self.context.REQUEST.RESPONSE.redirect('@@owncloud-settings')

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u'Edit cancelled'),
                                                      'info')
        self.request.response.redirect('%s/%s' % (self.context.absolute_url(),
                                                  self.control_panel_view))



class OwnCloudControlPanel(controlpanel.ControlPanelFormWrapper):
    form = OCSettingsEditForm
