# -*- coding: utf-8 -*-
from zope import schema
from plone.supermodel import model
from plone.app.registry.browser import controlpanel
from ulearn5.core import _


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
        default=u'UPC',
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


class OwnCloudControlPanel(controlpanel.ControlPanelFormWrapper):
    form = OCSettingsEditForm
