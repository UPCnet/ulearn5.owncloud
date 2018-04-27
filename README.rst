.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

================
ulearn5.owncloud
================

Package for integrate and connect Plone Site with OwnCloud service

Features
--------
Supports connecting to ownCloud 8.2, 9.0, 9.1 and newer.

General information
-------------------

- retrieve information about ownCloud instance (e.g. version, host, URL, etc.)

Accessing files
---------------

- basic file operations like getting a directory listing, file upload/download, directory creation, etc
- read/write file contents from strings
- upload with chunking and mtime keeping
- upload whole directories
- directory download as zip

Sharing (OCS Share API)
-----------------------

- share a file/directory via public link
- share a file/directory with another user or group
- unshare a file/directory
- check if a file/directory is already shared
- get information about a shared resource
- update properties of a known share

Apps (OCS Provisioning API)
---------------------------

- enable/disable apps
- retrieve list of enabled apps

Users (OCS Provisioning API)
----------------------------

- create/delete users
- create/delete groups
- add/remove user from groups

App data
--------

- store app data as key/values using the privatedata OCS API

Requirements
============

- Python >= 2.7 or Python >= 3.5
- requests module (for making HTTP requests)

Usage
=====

Example for uploading a file then sharing with link:

.. code-block:: python

    import owncloud

    oc = owncloud.Client('http://domain.tld/owncloud')

    oc.login('user', 'password')

    oc.mkdir('testdir')

    oc.put_file('testdir/remotefile.txt', 'localfile.txt')

    link_info = oc.share_file_with_link('testdir/remotefile.txt')

    print "Here is your link: " + link_info.get_link()

Example for do actions with OwnCloud utility

.. code-block:: python

    from ulearn5.owncloud.utilities import IOwncloudClient
    
    from zope.component import getUtility

    client = getUtility(IOwncloudClient)

    valor = client.connection()

    valor.list('Documents', depth=1)

Installation
------------

Install ulearn5.owncloud by adding it to your buildout::

    [buildout]

    ...

    eggs =
        ulearn5.owncloud


and then running ``bin/buildout``


License
-------

The project is licensed under the GPLv2.
