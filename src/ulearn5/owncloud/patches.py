# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
import logging
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from ZODB.POSException import ConflictError
from zope.component import getMultiAdapter
from zope.container.interfaces import INameChooser
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
import transaction

from plone import api
from ulearn5.core.utils import is_activate_owncloud
from ulearn5.owncloud import objectRenamed

logger = logging.getLogger(__name__)


def __call__(self):
    self.errors = []
    self.protect()
    context = aq_inner(self.context)

    catalog = getToolByName(context, 'portal_catalog')
    mtool = getToolByName(context, 'portal_membership')

    missing = []
    for key in self.request.form.keys():
        if not key.startswith('UID_'):
            continue
        index = key.split('_')[-1]
        uid = self.request.form[key]
        brains = catalog(UID=uid, show_inactive=True)
        if len(brains) == 0:
            missing.append(uid)
            continue
        obj = brains[0].getObject()
        title = self.objectTitle(obj)
        if not mtool.checkPermission('Copy or Move', obj):
            self.errors(_(u'Permission denied to rename ${title}.',
                          mapping={u'title': title}))
            continue

        sp = transaction.savepoint(optimistic=True)

        newid = self.request.form['newid_' + index].encode('utf8')
        newtitle = self.request.form['newtitle_' + index]
        try:
            obid = obj.getId()
            title = obj.Title()
            change_title = newtitle and title != newtitle
            if change_title:
                getSecurityManager().validate(obj, obj, 'setTitle',
                                              obj.setTitle)
                obj.setTitle(newtitle)
                notify(ObjectModifiedEvent(obj))
            if newid and obid != newid:
                parent = aq_parent(aq_inner(obj))
                # Make sure newid is safe
                newid = INameChooser(parent).chooseName(newid, obj)
                # Update the default_page on the parent.
                context_state = getMultiAdapter(
                    (obj, self.request), name='plone_context_state')
                if context_state.is_default_page():
                    parent.setDefaultPage(newid)
                parent.manage_renameObjects((obid, ), (newid, ))
            elif change_title:
                # the rename will have already triggered a reindex
                obj.reindexObject()
            portal = api.portal.get()
            if is_activate_owncloud(portal) and (obj.Type() == "Folder" or obj.Type() == "File Owncloud"):
                domain = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_domain')
                username = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_username')
                password = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_password')
                objectRenamed(self, obj, obid, domain, username, password)
        except ConflictError:
            raise
        except Exception as e:
            sp.rollback()
            logger.error(u'Error renaming "{title}": "{exception}"'.format(title=title.decode('utf8'), exception=e))
            self.errors.append(_(u'Error renaming ${title}', mapping={
                'title': title.decode('utf8')}))

    return self.message(missing)
