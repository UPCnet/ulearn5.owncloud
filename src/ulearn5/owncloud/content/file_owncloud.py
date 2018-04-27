# -*- coding: utf-8 -*-
import transaction
import webbrowser
from five import grok
from zope import schema
from zope.interface import implements
from zope.event import notify
from z3c.form import button
from z3c.form.interfaces import IEditForm

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.interfaces import IFolderish
from Products.statusmessages.interfaces import IStatusMessage

from plone import api
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.dexterity.browser.add import DefaultAddForm, DefaultAddView
from plone.dexterity.browser.edit import DefaultEditForm
from plone.directives import form
from plone.dexterity.content import Item
from plone.dexterity.utils import createContentInContainer
from plone.dexterity.events import EditCancelledEvent, EditFinishedEvent

from ulearn5.owncloud import _
from ulearn5.owncloud.utils import create_file_in_owncloud, construct_url_for_owncloud


class IFileOwncloud(form.Schema):
    """Schema for FileOwnCloud contenttype."""

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
    """OwnCloud object itself."""

    implements(IFileOwncloud)


class UploadFileOwnCloud(grok.View):
    """Helper class for update Files in OwnCloud."""

    grok.context(IFolderish)
    grok.name('upload-file')

    def render(self):
        """AJAX callback for Uploadify."""
        portal_state = self.context.unrestrictedTraverse('@@plone_portal_state')
        root = getNavigationRootObject(self.context, portal_state.portal())
        ppath = self.context.getPhysicalPath()
        relative = ppath[len(root.getPhysicalPath()):]
        path = "/".join(relative)

        # Create file in plone
        filename = self.request.file.filename
        obj = createContentInContainer(self.context,
                                       'ulearn5.owncloud.file_owncloud',
                                       id=filename,
                                       title=filename)

        # Save first the file in plone in case there are any with the same name
        filename = obj.id
        content = self.request.file.read()
        # Save the fileid owncloud in plone file
        obj.fileid = create_file_in_owncloud(filename, path, content)

        transaction.commit()


class CreateFileTextOwnCloud(grok.View):
    """Helper class for create new empty Files in OwnCloud."""

    grok.context(IFolderish)
    grok.name('create-file')

    def render(self):
        """AJAX callback for Uploadify."""
        portal_state = self.context.unrestrictedTraverse('@@plone_portal_state')
        root = getNavigationRootObject(self.context, portal_state.portal())
        ppath = self.context.getPhysicalPath()
        relative = ppath[len(root.getPhysicalPath()):]
        path = "/".join(relative)

        # Create file in plone
        file_id = self.request.form['file'] + '.' + self.request.form['type']
        filename = self.request.form['file']
        obj = createContentInContainer(self.context,
                                       'ulearn5.owncloud.file_owncloud',
                                       id=file_id,
                                       title=filename)

        # Save first the file in plone in case there are any with the same name
        filename = obj.id
        content = ''
        # Save the fileid owncloud in plone file
        obj.fileid = create_file_in_owncloud(filename, path, content)

        transaction.commit()

        connector_url = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_url')
        url_file_owncloud = connector_url + '/index.php/apps/richdocuments/index?fileId=' + obj.fileid + '&dir=' + path

        webbrowser.open_new_tab(url_file_owncloud)
        # return self.request.response.redirect(url_file_owncloud)


class FileOwncloudView(grok.View):
    """View class for FileOwnCloud contenttype."""

    grok.context(IFileOwncloud)
    grok.name('view')

    def render(self):
        self.template = ViewPageTemplateFile('file_owncloud_templates/view.pt')
        return self.template(self)

    def getTitle(self):
        return self.context.title

    def getURLFileOwncloud(self):
        url_file_owncloud = construct_url_for_owncloud(self.context)
        return url_file_owncloud


class FileOwncloudAdder(DefaultAddForm):
    """Adder form class for FileOwnCloud contenttype."""

    portal_type = 'ulearn5.owncloud.file_owncloud'

    def update(self):
        DefaultAddForm.update(self)


class AddView(DefaultAddView):
    """Helper class for Adder form FileOwnCloud contenttype."""

    form = FileOwncloudAdder

    def render(self):
        self.template = ViewPageTemplateFile('file_owncloud_templates/fileowncloudadder.pt')
        return self.template(self)


class FileOwncloudEdit(DefaultEditForm):
    """Edit form class for FileOwnCloud contenttype."""

    grok.name('fileowncloudedit')
    grok.context(IFileOwncloud)
    grok.require('cmf.ModifyPortalContent')

    def render(self):
        self.template = ViewPageTemplateFile('file_owncloud_templates/fileowncloudedit.pt')
        return self.template(self)

    def getTitle(self):
        return self.context.title

    def getURLFileOwncloud(self):
        url_file_owncloud = construct_url_for_owncloud(self.context)
        return url_file_owncloud

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleApply(self, action):
        """Save button in edit form."""
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
        """Cancel button in edit form."""
        IStatusMessage(self.request).addStatusMessage(
            _(u"Edit cancelled"), "info"
            )
        self.request.response.redirect(self.nextURL())
        notify(EditCancelledEvent(self.context))
