# -*- coding: utf-8 -*-
from five import grok
from zope import schema
from z3c.form import button
from zope.interface import implements, Interface
from plone.directives import form
from plone.dexterity.content import Item
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.dexterity.browser.add import DefaultAddForm, DefaultAddView
from plone.dexterity.browser.edit import DefaultEditForm
from ulearn5.owncloud import _
from Products.CMFCore.interfaces import IFolderish
from plone import api
from plone.app.layout.navigation.root import getNavigationRootObject
from zope.component import getUtility
from ulearn5.owncloud.utilities import IOwncloudClient
from ulearn5.owncloud.api.owncloud import HTTPResponseError, OCSResponseError
from ulearn5.owncloud.interfaces import IUlearn5OwncloudLayer
from ulearn5.owncloud.api.owncloud import Client

from plone.dexterity.utils import createContentInContainer
import transaction
from z3c.form.interfaces import IAddForm, IEditForm

from Products.statusmessages.interfaces import IStatusMessage
from zope.event import notify
from plone.dexterity.events import EditBegunEvent
from plone.dexterity.events import EditCancelledEvent
from plone.dexterity.events import EditFinishedEvent
import requests


class IFileOwncloud(form.Schema):

    title = schema.TextLine(
        title=_(u'file_owncloud_title'),
        description=_(u'file_owncloud_description'),
        required=True
    )

    form.mode(IEditForm, fileid='hidden')
    fileid = schema.TextLine(
        title=_(u'fileid_owncloud_title'),
        description=_(u'fileid_owncloud_description'),
        required=False
    )



class FileOwncloud(Item):
    implements(IFileOwncloud)


class UploadFileOwnCloud(grok.View):
    grok.context(IFolderish)
    grok.name('upload-file')

    def render(self):
        """ AJAX callback for Uploadify """

        portal = api.portal.get()
        portal_state = self.context.unrestrictedTraverse('@@plone_portal_state')
        root = getNavigationRootObject(self.context, portal_state.portal())
        ppath = self.context.getPhysicalPath()
        relative = ppath[len(root.getPhysicalPath()):]

        # Create file in plone
        filename = self.request.file.filename
        obj = createContentInContainer(self.context,
                                       'ulearn5.owncloud.file_owncloud',
                                       id=filename,
                                       title=filename)

        # Save first the file in plone in case there are any with the same name
        filename = obj.id

        # Create file in OwnCloud
        domain = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_domain')
        path = "/".join(relative)
        client = getUtility(IOwncloudClient)
        session = client.admin_connection()
        remote_path = domain.lower() + '/' + path + '/' + filename
        data = self.request.file.read()
        session.put_file_contents(remote_path, data)

        info_file = session.file_info(remote_path)
        fileid = info_file.attributes.get('{http://owncloud.org/ns}fileid')

        # Save the fileid owncloud in plone file
        obj.fileid = fileid
        transaction.commit()

class CreateFileTextOwnCloud(grok.View):
    grok.context(IFolderish)
    grok.name('create-file')

    def render(self):
        """ AJAX callback for Uploadify """

        portal = api.portal.get()
        portal_state = self.context.unrestrictedTraverse('@@plone_portal_state')
        root = getNavigationRootObject(self.context, portal_state.portal())
        ppath = self.context.getPhysicalPath()
        relative = ppath[len(root.getPhysicalPath()):]

        # Create file in plone
        file_id = self.request.form['file'] + '.' + self.request.form['type']
        filename = self.request.form['file']
        obj = createContentInContainer(self.context,
                                       'ulearn5.owncloud.file_owncloud',
                                       id=file_id,
                                       title=filename)

        # Save first the file in plone in case there are any with the same name
        filename = obj.id

        # Create file in OwnCloud
        domain = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_domain')
        path = "/".join(relative)
        client = getUtility(IOwncloudClient)
        session = client.admin_connection()
        remote_path = domain.lower() + '/' + path + '/' + filename
        data = ''
        session.put_file_contents(remote_path, data)

        info_file = session.file_info(remote_path)
        fileid = info_file.attributes.get('{http://owncloud.org/ns}fileid')

        # Save the fileid owncloud in plone file
        obj.fileid = fileid
        transaction.commit()

class FileOwncloudView(grok.View):
    grok.context(IFileOwncloud)
    grok.name('view')

    def render(self):
        self.template = ViewPageTemplateFile('file_owncloud_templates/view.pt')
        return self.template(self)

    def getTitle(self):
        return self.context.title

    def getURLFileOwncloud(self):
        domain = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_domain')
        connector_url = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_url')

        portal = api.portal.get()
        portal_state = self.context.unrestrictedTraverse('@@plone_portal_state')
        root = getNavigationRootObject(self.context, portal_state.portal())
        ppath = self.context.getPhysicalPath()
        relative = ppath[len(root.getPhysicalPath()):]
        path = '/' + domain.lower() + '/' + "/".join(relative[0:len(relative)-1])
        url_file_owncloud = connector_url + '/index.php/apps/richdocuments/index?fileId=' + self.context.fileid + '&dir=' + path

        return url_file_owncloud


class FileOwncloudAdder(DefaultAddForm):

    portal_type = 'ulearn5.owncloud.file_owncloud'

    def update(self):
        DefaultAddForm.update(self)


class AddView(DefaultAddView):

    form = FileOwncloudAdder

    def render(self):
        self.template = ViewPageTemplateFile('file_owncloud_templates/fileowncloudadder.pt')
        return self.template(self)


class FileOwncloudEdit(DefaultEditForm):
    grok.name('fileowncloudedit')
    grok.context(IFileOwncloud)
    grok.require('cmf.ModifyPortalContent')

    def render(self):
        self.template = ViewPageTemplateFile('file_owncloud_templates/fileowncloudedit.pt')
        return self.template(self)

    def getTitle(self):
        return self.context.title

    def getURLFileOwncloud(self):
        domain = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_domain')
        connector_url = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_url')

        portal = api.portal.get()
        portal_state = self.context.unrestrictedTraverse('@@plone_portal_state')
        root = getNavigationRootObject(self.context, portal_state.portal())
        ppath = self.context.getPhysicalPath()
        relative = ppath[len(root.getPhysicalPath()):]
        path = '/' + domain.lower() + '/' + "/".join(relative[0:len(relative)-1])
        url_file_owncloud = connector_url + '/index.php/apps/richdocuments/index?fileId=' + self.context.fileid + '&dir=' + path

        return url_file_owncloud

        # self.request.response.redirect(url_file_owncloud, 302)

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(
            self.success_message, "info"
        )
        self.request.response.redirect(self.nextURL())
        notify(EditFinishedEvent(self.context))

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(
            _(u"Edit cancelled"), "info"
        )
        self.request.response.redirect(self.nextURL())
        notify(EditCancelledEvent(self.context))
