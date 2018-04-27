# -*- coding: utf-8 -*-
from plone import api
from zope.component import getUtility
from ulearn5.owncloud.utilities import IOwncloudClient


def create_file_in_owncloud(filename, path, content):
    # Find destination to put file in OwnCloud
    domain = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_domain')
    remote_path = domain.lower() + '/' + path + '/' + filename
    
    # Create session with admin user in OwnCloud and put file
    client = getUtility(IOwncloudClient)
    session = client.admin_connection()
    session.put_file_contents(remote_path, content)
    info_file = session.file_info(remote_path)
    fileid = info_file.attributes.get('{http://owncloud.org/ns}fileid')

    return fileid
    
def construct_url_for_owncloud(context):
    domain = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_domain')
    connector_url = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_url')

    portal_state = context.unrestrictedTraverse('@@plone_portal_state')
    root = getNavigationRootObject(context, portal_state.portal())
    ppath = context.getPhysicalPath()
    relative = ppath[len(root.getPhysicalPath()):]
    path = '/' + domain.lower() + '/' + "/".join(relative[0:len(relative)-1])
    url_file_owncloud = connector_url + '/index.php/apps/richdocuments/index?fileId=' + context.fileid + '&dir=' + path
    return url_file_owncloud