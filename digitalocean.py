#!/usr/bin/env python
import httplib
import json
import os.path
import sys

SECURITY_FILE='security.json'
DO_API_HOST='api.digitalocean.com'
PER_PAGE=1000
DIGITAL_OCEAN_API_KEY='digital_ocean_api_key'
PUBLIC_SSH_KEY='public_ssh_key'

class Context:
    
    def __init__(self):
        if not os.path.isfile(SECURITY_FILE):
            raise Exception('could not initialize Digital Ocean Context because the security file, ' + SECURITY_FILE + 'does not exist' )
        
        with open(SECURITY_FILE,'r') as securityFile:
            self.securityInfo = json.load(securityFile)
            print('loaded security information from ' + os.path.abspath(SECURITY_FILE))
            
        if not DIGITAL_OCEAN_API_KEY in self.securityInfo:
            raise Exception(DIGITAL_OCEAN_API_KEY + ' not found in security file')
        
        if not PUBLIC_SSH_KEY in self.securityInfo:
            raise Exception(PUBLIC_SSH_KEY + ' not found in security file')
        
        listKeysResponse = self.doGET('/v2/account/keys')
        keyFound = False
        for key in listKeysResponse['ssh_keys']:
            if key['public_key'] == self.securityInfo[PUBLIC_SSH_KEY]:
                print('ssh key already registered')
                keyFound = True
                break
        
        if not keyFound:
            self.registerSSHKey(self.securityInfo[PUBLIC_SSH_KEY])
            print('ssh key registered')
        
    def doPOST(self, path, body):
        conn = httplib.HTTPSConnection(DO_API_HOST)
        headers = dict()
        headers['Content-Type'] = 'application/json'
        headers['Authorization'] = 'Bearer ' + self.securityInfo[DIGITAL_OCEAN_API_KEY]
        conn.request('POST',path + '?per_page={0}'.format(PER_PAGE),json.dumps(body),headers)
        resp = conn.getresponse()
        if resp.status != 201:
            raise Exception('an error occurred while invoking POST on {0}  - http response was {0}/{1}'.format(resp.status,resp.reason))
    
        responseJSON = json.load(resp)
        return responseJSON
            
    def doGET(self, path):
        conn = httplib.HTTPSConnection(DO_API_HOST)
        headers = dict()
        headers['Content-Type'] = 'application/json'
        headers['Authorization'] = 'Bearer ' + self.securityInfo[DIGITAL_OCEAN_API_KEY]
        conn.request('GET',path + '?per_page={0}'.format(PER_PAGE),None,headers)
        resp = conn.getresponse()
        if resp.status != 200:
            raise Exception('an error occurred while invoking GET on {2}  - http response was {0}/{1}'.format(resp.status,resp.reason, path))
    
        responseJSON = json.load(resp)
        return responseJSON

    def listRegions(self):
        return self.doGET('/v2/regions')
    
    def registerSSHKey(self, key):
        body = dict()
        body['public_key'] = key
        return self.doPOST('/v2/account/keys', body)
    
    
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
              
    
