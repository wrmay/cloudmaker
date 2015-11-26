import httplib
import logging
import os.path
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
        
    logging.info('downloaded ' + url + ' to ' + ' filename')

def aptKeyAdd(keyURL):
    f = tempfile.NamedTemporaryFile(delete=False)
    f.close()
    
    httpDownload(keyURL,f.name)
    p = subprocess.Popen(['apt-key','add',f.name], stderr=subprocess.STDOUT)
    output = p.communicate[0]
    
    if p.returncode != 0:
        msg = 'aptKeyAdd(' + keyURL + ') failed with the following output.\n' + output
        logging.error(msg)
        raise Exception(msg)
    
    logging.info('key at ' + keyURL + ' was added to the apt trusted key list')
    