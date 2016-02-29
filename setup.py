#!/usr/bin/env python

from distutils.core  import setup

setup(name='cloudmaker',
      version='0.9',
      description='A provisioning tool for Digital Ocean cloud',
      author='Randy May',
      author_email='randy@mathysphere.com',
      url='https://github.com/wrmay/cloudmaker',
      packages=['cloudmaker'],
      package_dir={'' : 'src/packages'},
      scripts=['src/scripts/cloudmaker'],
      requires=['Jinja2']
     )
