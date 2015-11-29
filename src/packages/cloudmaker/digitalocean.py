#!/usr/bin/env python
from __future__ import print_function
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
            print('loaded security information from ' + os.path.abspath(SECURITY_FILE), file=sys.stderr)
            
        if not DIGITAL_OCEAN_API_KEY in self.securityInfo:
            raise Exception(DIGITAL_OCEAN_API_KEY + ' not found in security file')
        
        if not PUBLIC_SSH_KEY in self.securityInfo:
            raise Exception(PUBLIC_SSH_KEY + ' not found in security file')
        
        listKeysResponse = self.doGET('/v2/account/keys')
        self.sshKeyId = None
        for key in listKeysResponse['ssh_keys']:
            if key['public_key'] == self.securityInfo[PUBLIC_SSH_KEY]:
                print('ssh key already registered', file=sys.stderr)
                self.sshKeyId = key['id']
                break
        
        if self.sshKeyId is None:
            resp = self.registerSSHKey(self.securityInfo[PUBLIC_SSH_KEY])
            self.sshKeyId = resp['ssh_key']['id']
            print('ssh key registered', file = sys.stderr)
        
    def doPOST(self, path, body):
        conn = httplib.HTTPSConnection(DO_API_HOST)
        headers = dict()
        headers['Content-Type'] = 'application/json'
        headers['Authorization'] = 'Bearer ' + self.securityInfo[DIGITAL_OCEAN_API_KEY]
        conn.request('POST',path + '?per_page={0}'.format(PER_PAGE),json.dumps(body),headers)
#        conn.request('POST',path,bytearray(json.dumps(body),'utf-8'),headers)
        resp = conn.getresponse()
        if resp.status != 201 and resp.status != 202:
            raise Exception('an error occurred while invoking POST on {2}  - http response was {0}/{1}'.format(resp.status,resp.reason, path))
    
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

    def doDELETE(self, path):
        conn = httplib.HTTPSConnection(DO_API_HOST)
        headers = dict()
        headers['Content-Type'] = 'application/json'
        headers['Authorization'] = 'Bearer ' + self.securityInfo[DIGITAL_OCEAN_API_KEY]
        conn.request('DELETE',path + '?per_page={0}'.format(PER_PAGE),None,headers)
        resp = conn.getresponse()
        if resp.status != 204:
            raise Exception('an error occurred while invoking DELETE on {2}  - http response was {0}/{1}'.format(resp.status,resp.reason, path))

    def listImages(self):
        return self.doGET('/v2/images')
    
    def listSizes(self):
        return self.doGET('/v2/sizes')
    
    def listRegions(self):
        return self.doGET('/v2/regions')
    
    def listDroplets(self):
        return self.doGET('/v2/droplets')
    
    def listDomains(self):
        return self.doGET('/v2/domains')
    
    def listDomainRecords(self, domainName):
        return self.doGET('/v2/domains/' + domainName + '/records')
    
    def getAction(self, id):
        return self.doGET('/v2/actions/{0}'.format(id))
    
    def getDroplet(self, id):
        return self.doGET('/v2/droplets/{0}'.format(id))
    
    def registerSSHKey(self, key):
        body = dict()
        body['public_key'] = key
        return self.doPOST('/v2/account/keys', body)
    
    def createDroplet(self, request):
        # seems like this class should not be doing this - consider refactoring
        request['ssh_keys'] = [self.sshKeyId]
        return self.doPOST('/v2/droplets', request)
            
    def createDomain(self, domain, ipAddress):
        body = dict()
        body['name'] = domain
        body['ip_address'] = ipAddress
        return self.doPOST('/v2/domains', body)

    def createDomainRecord(self, domain, name, ipAddress, recType):
        body = dict()
        body['name'] = name
        body['data'] = ipAddress
        body['type'] = recType
        return self.doPOST('/v2/domains/' + domain + '/records', body)

    def deleteDomain(self, domainName):
        self.doDELETE('/v2/domains/' + domainName)

    
    def deleteDomainRecord(self, domainName, recordId):
        self.doDELETE('/v2/domains/' + domainName + '/records/{0}'.format(recordId))
        
    def deleteDroplet(self, dropletId):
        self.doDELETE('/v2/droplets/{0}'.format(dropletId) )
        
            
    def publicAddressIPV4(self, droplet):
        for network in droplet['networks']['v4']:
            if network['type'] == 'public':
                return network['ip_address']
        
        return None
    
    def publicAddressIPV6(self, droplet):
        for network in droplet['networks']['v6']:
            if network['type'] == 'public':
                return network['ip_address']
        
        return None
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'list':
            if len(sys.argv) > 2 and sys.argv[2] == 'regions':
                do = Context()
                regions = do.listRegions()
                json.dump(regions,sys.stdout,indent=3)
                sys.exit(0)
            elif len(sys.argv) > 2 and sys.argv[2] == 'images':
                do = Context()
                images = do.listImages()
                json.dump(images,sys.stdout,indent=3)
                sys.exit(0)
            elif len(sys.argv) > 2 and sys.argv[2] == 'sizes':
                do = Context()
                sizes = do.listSizes()
                json.dump(sizes,sys.stdout,indent=3)
                sys.exit(0)
        
    print('usage', file=sys.stderr)
    print('\tdigitalocean list regions        #list all regions', file=sys.stderr)
              
    
