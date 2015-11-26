#!/usr/bin/python

import logging

from cloudmaker.provisioner import *

logging.basicConfig(level='INFO')

aptKeyAdd('http://debian.koha-community.org/koha/gpg.asc')


