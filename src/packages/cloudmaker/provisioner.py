import httplib
import logging
import os.path
import re
import subprocess
import tempfile
import urlparse


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
    p = subprocess.Popen(['apt-key','add',f.name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = p.communicate()[0]
    
    if p.returncode != 0:
        msg = 'aptKeyAdd("' + keyURL + '") failed with the following output.\n\t' + output
        logging.error(msg)
        raise Exception(msg)
    
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
            
            os.remove('/etc/apt/sources.list')
            os.rename(tempfileName,'/etc/apt/sources.list')
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
    p = subprocess.Popen(['apt-get', 'update'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = p.communicate()
    if p.returncode == 0:
        logging.info('apt-get update succeeded')
    
    else:
        msg = 'apt-get update failed with the following output: \n\t' + output[0]
        logging.error(msg)
        raise Exception(msg)
        
