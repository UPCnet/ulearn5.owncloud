# -*- coding: utf-8 -*-
from plone import api
from zope.component import getUtility
from ulearn5.owncloud.utilities import IOwncloudClient
from plone.app.layout.navigation.root import getNavigationRootObject

from ulearn5.owncloud.api.owncloud import Client



def get_domain():
    return api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_domain').lower()

def create_file_in_owncloud(filename, path, content):
    # Find destination to put file in OwnCloud
    domain = get_domain()
    remote_path = domain + '/' + path + '/' + filename

    # Create session with admin user in OwnCloud and put file
    client = getUtility(IOwncloudClient)
    session = client.admin_connection()
    session.put_file_contents(remote_path, content)
    info_file = session.file_info(remote_path)
    fileid = info_file.attributes.get('{http://owncloud.org/ns}fileid')

    return fileid

def construct_url_for_owncloud(context):
    connector_url = api.portal.get_registry_record('ulearn5.owncloud.controlpanel.IOCSettings.connector_url')

    portal_state = context.unrestrictedTraverse('@@plone_portal_state')
    root = getNavigationRootObject(context, portal_state.portal())
    ppath = context.getPhysicalPath()
    relative = ppath[len(root.getPhysicalPath()):]
    path = '/' + "/".join(relative[0:len(relative)-1])
    url_file_owncloud = connector_url + 'index.php/apps/richdocuments/index?fileId=' + context.fileid + '&dir=' + path
    return url_file_owncloud

def update_owncloud_permission(obj, acl):
    domain = get_domain()
    portal = api.portal.get()
    ppath = obj.getPhysicalPath()
    relative = ppath[len(portal.getPhysicalPath()):]
    path = "/".join(relative)

    permissions = []
    users_permissions = []
    users_editacl = []
    groups_editacl = []

    # Get permissions owncloud for the community
    client = getUtility(IOwncloudClient)
    session = client.admin_connection()
    share_info = session.get_shares(domain.lower() + '/' + path)

    for share in share_info:
        new_permission = dict(user_id = share.get_share_with(),
                              share_id = share.get_id())
        permissions.append(new_permission)
        users_permissions.append(share.get_share_with())

    # Search the users that we have to remove and delete our owncloud permissions
    users_editacl = [user['id'] for user in acl['users']]
    if 'groups' in acl:
        groups_editacl = [group['id'] for group in acl['groups']]
    else:
        groups_editacl = []
    users_delete = set(users_permissions) - set(users_editacl) - set(groups_editacl)

    for user in users_delete:
        share_id = [aa['share_id'] for aa in permissions if (aa['user_id'] == user)]
        session.delete_share(share_id[0])

    # Add or modify the permissions of the users
    for user in acl['users']:
        update_share = False
        if 'owner' in user['role']:
            for share in share_info:
                if user['id'] in share.get_share_with():
                    session.update_share(share.get_id(), perms=Client.OCS_PERMISSION_ALL)
                    update_share = True
                    break
            if not update_share:
                session.share_file_with_user(domain.lower() + '/' + path, user['id'], perms=Client.OCS_PERMISSION_ALL) #Propietari
        elif 'writer' in user['role']:
            for share in share_info:
                if user['id'] in share.get_share_with():
                    session.update_share(share.get_id(), perms=Client.OCS_PERMISSION_EDIT)
                    update_share = True
                    break
            if not update_share:
                session.share_file_with_user(domain.lower() + '/' + path, user['id'], perms=Client.OCS_PERMISSION_EDIT) #Editor
        elif 'reader' in user['role']:
            for share in share_info:
                if user['id'] in share.get_share_with():
                    session.update_share(share.get_id(), perms=Client.OCS_PERMISSION_READ)
                    update_share = True
                    break
            if not update_share:
                session.share_file_with_user(domain.lower() + '/' + path, user['id']) #Lector
        else:
            pass


    # Add or modify the permissions of the groups
    if 'groups' in acl:
        for group in acl['groups']:
            update_share = False
            if 'owner' in group['role']:
                for share in share_info:
                    if group['id'] in share.get_share_with():
                        session.update_share(share.get_id(), perms=Client.OCS_PERMISSION_ALL)
                        update_share = True
                        break
                if not update_share:
                    session.share_file_with_group(domain.lower() + '/' + path, group['id'], perms=Client.OCS_PERMISSION_ALL) #Propietari
            elif 'writer' in group['role']:
                for share in share_info:
                    if group['id'] in share.get_share_with():
                        session.update_share(share.get_id(), perms=Client.OCS_PERMISSION_EDIT)
                        update_share = True
                        break
                if not update_share:
                    session.share_file_with_group(domain.lower() + '/' + path, group['id'], perms=Client.OCS_PERMISSION_EDIT) #Editor
            elif 'reader' in group['role']:
                for share in share_info:
                    if group['id'] in share.get_share_with():
                        session.update_share(share.get_id(), perms=Client.OCS_PERMISSION_READ)
                        update_share = True
                        break
                if not update_share:
                    session.share_file_with_group(domain.lower() + '/' + path, group['id']) #Lector
            else:
                pass
