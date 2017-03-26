import httplib
import logging
import os
import subprocess
import tempfile
import urlparse

import cloudmakerutils

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)
  {% if currentDroplet.currentSetupStep.keyURL %}
  keyURL = '{{ currentDroplet.currentSetupStep.keyURL }}'
  cloudmakerutils.aptKeyAdd(keyURL)
  {% endif %}
  sourceURL = '{{ currentDroplet.currentSetupStep.sourceURL }}'
  suite = '{{ currentDroplet.currentSetupStep.suite }}'
  component = '{{ currentDroplet.currentSetupStep.component }}'
  {% if currentDroplet.currentSetupStep.listFile %}
  listFile = '{{ currentDroplet.currentSetupStep.listFile }}'
  cloudmakerutils.aptSourceAdd(sourceURL, suite, component, listfile = listFile)
  {% else %}
  cloudmakerutils.aptSourceAdd(sourceURL, suite, component)
  {% endif %}
  cloudmakerutils.aptUpdate()
  logging.info('added ' + sourceURL + ' to apt sources')
