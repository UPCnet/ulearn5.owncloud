#!/bin/bash
# i18ndude should be available in current $PATH (eg by running
# ``export PATH=$PATH:$BUILDOUT_DIR/bin`` when i18ndude is located in your buildout's bin directory)
#
# For every language you want to translate into you need a
# locales/[language]/LC_MESSAGES/ulearn5.owncloud.po
# (e.g. locales/de/LC_MESSAGES/ulearn5.owncloud.po)

domain=ulearn5.owncloud

i18ndude rebuild-pot --pot $domain.pot --create $domain ../
i18ndude sync --pot $domain.pot ca/LC_MESSAGES/$domain.po
i18ndude sync --pot $domain.pot es/LC_MESSAGES/$domain.po
i18ndude sync --pot $domain.pot en/LC_MESSAGES/$domain.po
