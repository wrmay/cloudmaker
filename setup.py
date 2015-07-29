#!/usr/bin/env python

from distutils.core  import setup

setup(name='cloudmaker',
      version='0.1',
      description='A provisioning tool for Digital Ocean cloud',
      author='Randy May',
      author_email='randy@mathysphere.com',
      url='https://github.com/wrmay/cloudmaker',
      packages=['cloudmaker'],
      package_dir={'cloudmaker' : 'src/packages/cloudmaker'},
      scripts=['src/scripts/cloudmaker']
     )
