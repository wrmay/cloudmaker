#!/usr/bin/env python
import httplib
import json
import os.path
import sys

SECURITY_FILE='security.json'
DO_API_HOST='api.digitalocean.com'
PER_PAGE=1000

class Context:
    
    def __init__(self):
        if not os.path.isfile(SECURITY_FILE):
            raise Exception('could not initialize Digital Ocean Context because the security file, ' + SECURITY_FILE + 'does not exist' )
        
        with open(SECURITY_FILE,'r') as securityFile:
            self.securityInfo = json.load(securityFile)
            print('loaded security information from ' + os.path.abspath(SECURITY_FILE))
            
    def doGET(self, path):
        conn = httplib.HTTPSConnection(DO_API_HOST)
        headers = dict()
        headers['Content-Type'] = 'application/json'
        headers['Authorization'] = 'Bearer ' + self.securityInfo['digital_ocean_api_key']
        conn.request('GET',path + '?per_page={0}'.format(PER_PAGE),None,headers)
        resp = conn.getresponse()
        if resp.status != 200:
            raise Exception('an error occurred while invoking GET on {0}  - http response was {0}/{1}'.format(response.status,response.message))
    
        responseJSON = json.load(resp)
        return responseJSON

    def listRegions(self):
        return self.doGET('/v2/regions')
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'list':
            if len(sys.argv) > 2 and sys.argv[2] == 'regions':
                do = Context()
                regions = do.listRegions()
                json.dump(regions,sys.stdout,indent=3)
                sys.exit(0)
        
    print('usage')
    print('\tdigitalocean list regions                     #list all regions')
              
    
