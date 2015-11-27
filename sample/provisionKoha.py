#!/usr/bin/python

import logging

from cloudmaker.provisioner import *

logging.basicConfig(level='INFO')

aptKeyAdd('http://debian.koha-community.org/koha/gpg.asc')
aptSourceAdd('http://debian.koha-community.org/koha', 'stable', 'main', listfile='koha')
aptUpdate()
aptInstall('koha-common')
passw = randomPassword(8)
debconfSetSelections('mysql-server', 'mysql-server/root_password', 'password', passw)
debconfSetSelections('mysql-server', 'mysql-server/root_password_again', 'password', passw)
aptInstall('mysql-server')
propfileSet('/etc/koha/koha-sites.conf', 'DOMAIN', '".clearlib.com"')
propfileSet('/etc/koha/koha-sites.conf', 'INTRASUFFIX', '"-staff"')
apache2EnableModules('rewrite', 'cgi')
siteName = 'testlib'
kohaCreateSite(siteName, True)
logging.info('koha provisioning complete - log in to the web interface with {0}/{1} to continue configuration.'.format(kohaSuperUser(siteName), kohaSuperUserPass(siteName)))
