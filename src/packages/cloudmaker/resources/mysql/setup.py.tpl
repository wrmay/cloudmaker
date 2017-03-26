import logging
import subprocess
import cloudmakerutils

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    user = '{{ currentDroplet.currentSetupStep.user }}'
    password = '{{ currentDroplet.currentSetupStep.password }}'
    database = '{{ currentDroplet.currentSetupStep.database }}'

    {% for filename in currentDroplet.currentSetupStep.files %}
    filename = '{{ filename }}'
    with open( filename,'r') as sqlFile:
      p = subprocess.Popen(['mysql', '-u', user, '-p'+password, database], stdin=sqlFile, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      outs,errs = p.communicate()
      if p.returncode == 0:
        logging.info('sql file ' + filename + ' ran successfully')
      else:
        logging.error(outs)
        raise Exception('sql file ' + filename + ' did not run successfully')
    {% endfor %}
