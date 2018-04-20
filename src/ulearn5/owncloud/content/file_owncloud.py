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


class IFileOwncloud(form.Schema):

    title = schema.TextLine(
        title=_(u'file_owncloud_title'),
        description=_(u'file_owncloud_description'),
        required=True
    )

    fileid = schema.TextLine(
        title=_(u'fileid_owncloud_title'),
        description=_(u'fileid_owncloud_description'),
        required=True
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

        # Create file in OwnCloud
        domain = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_domain')
        path = "/".join(relative)
        client = getUtility(IOwncloudClient)
        session = client.admin_connection()
        filename = self.request.file.filename
        remote_path = domain.lower() + '/' + path + '/' + filename
        data = self.request.file.read()
        session.put_file_contents(remote_path, data)

        info_file = session.file_info(remote_path)
        fileid = info_file.attributes.get('{http://owncloud.org/ns}fileid')

        # Create file in plone
        obj = createContentInContainer(self.context,
                                       'ulearn5.owncloud.file_owncloud',
                                       id=filename,
                                       title=filename,
                                       fileid=fileid)
        obj.reindexObject()
        transaction.commit()


class FileOwncloudView(grok.View):
    grok.context(IFileOwncloud)
    grok.name('view')

    def render(self):
        self.template = ViewPageTemplateFile('file_owncloud_templates/view.pt')
        return self.template(self)

    def getTitle(self):
        return self.context.title


class FileOwncloudAdder(DefaultAddForm):

    portal_type = 'ulearn5.owncloud.file_owncloud'

    def update(self):
        print "ADD FORM FIRE!!!!!!!!!!!!"
        DefaultAddForm.update(self)


class AddView(DefaultAddView):

    form = FileOwncloudAdder

    def render(self):
        self.template = ViewPageTemplateFile('file_owncloud_templates/fileowncloudadder.pt')
        return self.template(self)



# class FileOwncloudAdder(DefaultAddForm):
#     grok.name('addOwncloudfile')
#     grok.context(IFileOwncloud)
#     grok.require('cmf.ModifyPortalContent')

#     schema = IFileOwncloud
#     ignoreContext = True

#     def update(self):
#         super(FileOwncloudAdder, self).update()
#         import ipdb;ipdb.set_trace()
#         self.actions['save'].addClass('context')

#     def updateWidgets(self):
#         super(FileOwncloudAdder, self).updateWidgets()
#         import ipdb;ipdb.set_trace()
#         # Override the interface forced 'hidden' to 'input' for add form only
#         # self.widgets['community_type'].mode = 'input'

#     @button.buttonAndHandler(_(u'Add file owncloud'), name='save')
#     def handleApply(self, action):
#         import ipdb;ipdb.set_trace()
#         data, errors = self.extractData()
#         if errors:
#             self.status = self.formErrorsMessage
#             return

#         nom = data['title']

#         self.request.response.redirect('http://pc47194.estacions.upcnet.es/')

# class FileOwncloudAdder(DefaultAddForm):
#     grok.name('fileowncloudadder')
#     grok.context(IFileOwncloud)
#     grok.require('cmf.ModifyPortalContent')

#     # def render(self):
#     #     import ipdb;ipdb.set_trace()
#     #     self.template = ViewPageTemplateFile('file_owncloud_templates/fileowncloudadder.pt')
#     #     return self.template(self)


#     # portal_type = 'ulearn5.owncloud.file_owncloud'
#     # immediate_view = 'fileowncloudadder'
#     # schema = IFileOwncloud
#     # ignoreContext = True

#     def __init__(self, context, request, ti=None):
#         super(DefaultAddForm, self).__init__(context, request)
#         import ipdb;ipdb.set_trace()
#         if ti is not None:
#             self.ti = ti
#             self.portal_type = ti.getId()
#         self.request.form['disable_border'] = True


#     def update(self):
#         import ipdb;ipdb.set_trace()
#         super(FileOwncloudAdder, self).update()
#         self.actions['save'].addClass('context')

#     def updateWidgets(self):
#         import ipdb;ipdb.set_trace()


#     @button.buttonAndHandler(_(u'Add file owncloud'), name='save')
#     def handleApply(self, action):
#         import ipdb;ipdb.set_trace()

#         data, errors = self.extractData()
#         if errors:
#             self.status = self.formErrorsMessage
#             return

#         nom = data['title']


#         self.request.response.redirect(self.context.absolute_url())

# class AddView(DefaultAddView):
#     form = FileOwncloudAdder

#     def render(self):
#         import ipdb;ipdb.set_trace()
#         self.template = ViewPageTemplateFile('file_owncloud_templates/fileowncloudadder.pt')
#         return self.template(self)

class FileOwncloudEdit(DefaultEditForm):
    grok.name('fileowncloudedit')
    grok.context(IFileOwncloud)
    grok.require('cmf.ModifyPortalContent')

    # schema = IFileOwncloud
    # ignoreContext = True

    def render(self):
        self.template = ViewPageTemplateFile('file_owncloud_templates/fileowncloudedit.pt')
        return self.template(self)

    def getTitle(self):
        return self.context.title

    # def render(self):
    #     import ipdb;ipdb.set_trace()
    #     self.template = ViewPageTemplateFile('file_owncloud_templates/fileowncloudedit.pt')
    #     return self.template(self)

    # def update(self):
    #     super(FileOwncloudEdit, self).update()
    #     self.actions['save'].addClass('context')

    # def updateWidgets(self):
    #     super(FileOwncloudEdit, self).updateWidgets()

    #     self.widgets['title'].value = self.context.title


    # @button.buttonAndHandler(_(u'Edit file owncloud'), name='save')
    # def handleApply(self, action):
    #     data, errors = self.extractData()
    #     if errors:
    #         self.status = self.formErrorsMessage
    #         return
    #     import ipdb;ipdb.set_trace()
    #     nom = data['title']


    #     self.request.response.redirect(self.context.absolute_url())
