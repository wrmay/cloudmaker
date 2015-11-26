#!/usr/bin/python

import logging

from cloudmaker.provisioner import *

logging.basicConfig(level='INFO')

httpDownload('http://debian.koha-community.org/koha/gpg.asc', '/tmp/koha.gpg')

