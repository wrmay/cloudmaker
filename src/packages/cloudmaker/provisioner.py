import httplib
import logging
import os.path
import random
import re
import shutil
import string
import subprocess
import tempfile
import urlparse
   
  
def randomPassword(length):
    validchars = string.ascii_letters + string.digits + '@!$'
    result = ''
    rand = random.SystemRandom()
    for i in range(length):
        result += rand.choice(validchars)
        
    return result
    
def run(*args):
    cmd = string.join(args)
        
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = p.communicate()
    if p.returncode == 0:
        logging.info(cmd + ' succeeded')
    
    else:
        msg = cmd + ' failed with the following output: \n\t' + output[0]
        logging.error(msg)
        raise Exception(msg)
 
    

# if filename exists, it will be overwritten
def httpDownload(url, filename):
    o = urlparse.urlparse(url)
    if len(o.netloc) == 0:
        msg = 'httpDownload failed: could not extract host name from url: ' + url
        logging.error(msg)
        raise Exception(msg)
    
    if len(o.path) == 0:
        msg = 'httpDownload failed: could not extract path from url: ' + url
        logging.error(msg)
        raise Exception(msg)
    
    conn = httplib.HTTPConnection(o.netloc)
    conn.request('GET', o.path)
    try :
        r = conn.getresponse()
        if r.status != 200:
            msg = 'httpDownload failed: HTTP GET of ' + url + ' failed with response code ' + r.status
            logging.error(msg)
            raise Exception(msg)
        
        with open(filename,'w', 2000) as f:
            chunk = r.read(2000)
            while len(chunk) > 0:
                f.write(chunk)
                chunk = r.read(2000)
        
    finally:
        conn.close()
        
    logging.info('downloaded ' + url + ' to ' + filename)

def aptKeyAdd(keyURL):
    f = tempfile.NamedTemporaryFile(delete=False)
    f.close()
    
    httpDownload(keyURL,f.name)
    run('apt-key', 'add', f.name)    
    logging.info('key at ' + keyURL + ' was added to the apt trusted key list')
    
# Ensures that url, suite and argument are a debian source.  The listfile
# argument is optional.  If listfile is not provided, /etc/apt/sources.list will
# be examined for the given url/suite/component and they will be added if not
# present.  If listfile is provided, the url/suite/component will be removed
# from /etc/apt/sources.list if presenent and will be added to /etc/apt/sources.list.d/listfile.list
# , which will be created if needed.  This command must be run as root
def aptSourceAdd(url, suite, component, listfile=None):
    regex = r'(deb|deb-src)\s.*' + url + r'\s*' + suite + r'\s.*' + component
    targetFile = '/etc/apt/sources.list'
    if listfile is not None:
        targetFile = '/etc/apt/sources.list.d/' + listfile + '.list'
        #scan /etc/apt/sources.list for this entry and remove it
        found = False
        with open('/etc/apt/sources.list', 'r') as f1:
            line = f1.readline()
            while len(line) > 0:
                match = re.match(regex, line)
                if match is not None:
                    found = True
                    break
                
                line = f1.readline()
                
        if found:
            with tempfile.NamedTemporaryFile(delete=False) as f2:
                with open('/etc/apt/sources.list', 'r') as f1:
                    line = f1.readline()
                    while len(line) > 0:
                        match = re.match(regex, line)
                        if match is None:
                            f2.write(line)
                        line = f1.readline()
                tempfileName = f2.name
            
            shutil.copyfile(tmpfileName,'/etc/apt/sources.list')
            os.remove(tmpfileName)
            logging.info('removed [' + url + ' ' + suite + ' ' + component + '] from /etc/apt/sources.list')
    
    if not os.path.exists(targetFile):
        with open(targetFile, 'w') as f1:
            f1.write('deb ' + url + ' ' + suite + ' ' + component + '\n')
            
        logging.info('created ' + targetFile + ' and added [' + url + ' ' + suite + ' ' + component + ']')
        
    else:
        found = False
        with open(targetFile, 'r') as f1:
            line = f1.readline()
            while len(line) > 0:
                match = re.match(regex, line)
                if match is not None:
                    found = True
                    break
                
                line = f1.readline()
                
        if found:
            logging.info('[' + url + ' ' + suite + ' ' + component + '] is already in ' + targetFile)
        
        else:
            with open(targetFile, 'a') as f1:
                f1.write('\ndeb ' + url + ' ' + suite + ' ' + component + '\n')
                
            logging.info('added [' + url + ' ' + suite + ' ' + component + '] to ' + targetFile)
                
def aptUpdate():
    run('apt-get', 'update')
        
def aptInstall(package):
    run('apt-get', 'install', '-y',package)
    logging.info(package + ' installed')

def debconfSetSelections(package, question, qtype, qval):
    p = subprocess.Popen(['debconf-set-selections'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
    p.stdin.write(package + ' ' + question + ' ' + qtype + ' ' + qval + os.linesep)
    result = p.communicate()
    
    if p.returncode == 0:
        if qtype != 'password':
            logging.info('set Debian selection for ' + package + ' : ' + question + '=' + qval)
        else:
            logging.info('set Debian selection for ' + package + ' : ' + question + '=' + '******')
            
    else:
        msg = 'debconf-set-selections for ' + package + ' failed with the following error.\n\t' + result[0]
        logging.error(msg)
        raise Exception(msg)
    
def propfileSet(propfileName, propName, propVal):
    keymatchRE = r'\s*' + propName + r'\s*=\s*\S*'
    if not os.path.exists(propfileName):
        msg = 'propfileSet failed because property file ' + propfileName + ' does not exist'
        logging.error(msg)
        raise Exception(msg)
    
    found = False
    tmpFile = tempfile.NamedTemporaryFile(delete=False)
    tmpFileName = tmpFile.name
    with tmpFile:
        with open(propfileName, 'r') as propfile:
            line = propfile.readline()
            while len(line) > 0:
                match = re.match(keymatchRE, line)
                if match is None:
                    tmpFile.write(line)
                else:
                    found = True
                    tmpFile.write(propName + '=' + propVal + '\n')
                    
                line = propfile.readline()
                
        if not found:
            tmpFile.write(propName + '=' + propVal + '\n')

    shutil.copyfile( tmpFileName, propfileName)
    os.remove(tmpFileName)
    logging.info('set ' + propName + '=' + propVal + ' in ' + propfileName)
    
def apache2EnableModules(*args):
    modules = string.join(args)
    for arg in args:
        run('a2enmod', arg)
        
    run('service', 'apache2', 'restart')
    logging.info('enabled apache2 modules: ' + modules)
    
    
def kohaCreateSite(siteName, emailEnabled):
    sitelist = subprocess.check_output('koha-list')
    if sitelist.find(siteName) != -1:
        logging.info('Koha site ' + siteName + ' already exists')
    else:
        run('koha-create', '--create-db', siteName )
        
    if emailEnabled:
        run('koha-email-enable', siteName)
    else:
        run('koha-email-disable', siteName)
        
def kohaSuperUser(siteName):
    return subprocess.check_output(['xmlstarlet', 'sel', '-t', '-v', 'yazgfs/config/user', '/etc/koha/sites/' + siteName + '/koha-conf.xml'])

def kohaSuperUserPass(siteName):
    return subprocess.check_output(['xmlstarlet', 'sel', '-t', '-v', 'yazgfs/config/pass', '/etc/koha/sites/' + siteName + '/koha-conf.xml'])
    