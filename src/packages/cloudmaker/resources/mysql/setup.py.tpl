import os
import subprocess

def debconfSetSelections(package, question, qtype, qval):
    p = subprocess.Popen(['debconf-set-selections'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
    p.stdin.write(package + ' ' + question + ' ' + qtype + ' ' + qval + os.linesep)
    result = p.communicate()

    if p.returncode == 0:
        if qtype != 'password':
            print 'set Debian selection for ' + package + ' : ' + question + '=' + qval
        else:
            print 'set Debian selection for ' + package + ' : ' + question + '=' + '******'

    else:
        msg = 'debconf-set-selections for ' + package + ' failed with the following error.\n\t' + result[0]
        raise Exception(msg)

if __name__ == '__main__':
  passw = '{{ currentDroplet.currentSetupStep.rootPassword }}'
  debconfSetSelections('mysql-server', 'mysql-server/root_password', 'password', passw)
  debconfSetSelections('mysql-server', 'mysql-server/root_password_again', 'password', passw)
  subprocess.check_call(['apt-get','install','-y', 'mysql-server'])
