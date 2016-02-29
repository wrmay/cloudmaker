#!/usr/bin/env python
from __future__ import print_function
import httplib
import json
import logging
import os.path
import sys
import time


SECURITY_FILE='~/.cloudmaker.json'
DO_API_HOST='api.digitalocean.com'
PER_PAGE=1000
DIGITAL_OCEAN_API_KEY='digital_ocean_api_key'
PUBLIC_SSH_KEY='public_ssh_key'

class Context:
    
    def __init__(self):
        if not os.path.isfile(os.path.expanduser(SECURITY_FILE)):
            raise Exception('could not initialize Digital Ocean Context because the security file, ' + SECURITY_FILE + 'does not exist' )
        
        with open(os.path.expanduser(SECURITY_FILE),'r') as securityFile:
            securityInfo = json.load(securityFile)
            print('loaded security information from ' + os.path.abspath(SECURITY_FILE), file=sys.stderr)
            self.__init__(securityInfo)
        
    def __init__(self, securitySettings):
        self.securityInfo = securitySettings
            
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
        
    #gets the public ipv4 address from a droplet definition
    #e.g. one returned from getDroplet
    def publicAddressIPV4(self, droplet):
        for network in droplet['networks']['v4']:
            if network['type'] == 'public':
                return network['ip_address']
        
        return None
    
    #gets the public ipv6 address from a droplet definition
    #e.g. one returned from getDroplet
    def publicAddressIPV6(self, droplet):
        for network in droplet['networks']['v6']:
            if network['type'] == 'public':
                return network['ip_address']
        
        return None
    
    ### begin high level functions

        
    # This idempotent method first checks for a droplet with the given name
    # that is already deployed. If one is found, that droplet def is compared to
    # the passed droplet def. If there is a difference, the droplet will be
    # undeployed and reprovisioned, if they are the same , the droplet def
    # of the existing droplet will be returned. If no droplet with the same
    # name exists, a new one will be provisioned and its definition will be
    # returned.
    def deploy(self, dropletDef):
        serverName = dropletDef['name']
        resp = self.listDroplets()
        
        result = None
        for droplet in resp['droplets']:
            if droplet['name'] == serverName:
                same = True
                
                if dropletDef['region'] != droplet['region']['slug']:
                    #logging.info('existing={0} requested={1}'.format(droplet['region']['name'],dropletDef['region']))
                    same = False
                elif dropletDef['size'] != droplet['size_slug']:
                    #logging.info('existing={0} requested={1}'.format(droplet['size_slug'],dropletDef['size']))
                    same = False
                elif dropletDef['image'] != droplet['image']['slug']:
                    #logging.info('existing={0} requested={1}'.format(droplet['image']['slug'],dropletDef['image']))
                    same = False
                elif  'backups' in dropletDef and (dropletDef['backups'] == True and  'backups' not in droplet['features']):
                    same = False
                elif 'ipv6' in dropletDef and ( dropletDef['ipv6'] == True and 'ipv6' not in droplet['features']):
                    same = False
                elif 'private_networking' in dropletDef and (dropletDef['private_networking'] == True and 'private_networking' not in droplet['features']):
                    same = False
    
                if same:                    
                    logging.info(serverName + ' is already deployed')
                    result = droplet
                    return result #RETURN
                else:
                    self.deleteDroplet(droplet['id'])
                    logging.info('deleted droplet named ' + serverName + ' having a different definition')
                    break
        
        resp = self.createDroplet(dropletDef)
        dropletId = resp['droplet']['id']
        action = resp['links']['actions'][0]['id']
        timedOut = True
        logging.info('waiting 60s for ' + dropletDef['name'] + ' to be provisioned on Digital Ocean')
        time.sleep(60)
        for attempt in range(10):
            getActionResp = self.getAction(action)
            if getActionResp['action']['status'] == 'completed':
                timedOut = False
                break
            elif getActionResp['action']['status'] == 'errored':
                msg = 'provisioning of ' + dropletDef['name'] + ' on Digital Ocean failed'
                logging.error(msg)
    
            logging.info('waiting 20s for ' + dropletDef['name'] + ' to be provisioned on Digital Ocean')
            time.sleep(20)
        
        if timedOut:
            raise Exception('timed out waiting for ' + dropletDef['name'] + ' to deploy on Digital Ocean')
        
        resp = self.getDroplet(dropletId)
        logging.info(serverName + ' deployed on Digital Ocean')
        return resp['droplet']


    # this is an idempotent version of create domain that will create a new
    # domain if it does not exist - does not return anything
    def createDomainIfAbsent(self, domainName):
        domains = self.listDomains()
        found = False
        for domain in domains['domains']:
            if domain['name'] == domainName:
                found = True
                break
            
        if found:
            logging.info('domain "' + domainName + '" already exists')
        else:
            self.createDomain(domainName, '127.0.0.1')
            self.listDomainRecords(domainName)
            did = None
            for domainrec in self.listDomainRecords(domainName)['domain_records']:
                if domainrec['name'] == '@' and domainrec['type'] != 'NS':
                    did = domainrec['id']
                    break
                
            if did is not None:
                self.deleteDomainRecord(domainName, did)
                
            logging.info('domain "' + domainName + '" created')

    def parseFQDN(self,fqdn):
        lastDot = fqdn.find('.')
        if lastDot == -1:
            logging.error("expected a fully qualified domain name - found: " + fqdn)
            raise Exception('unexepected error' )
            
        while True:
            i = fqdn.find('.',lastDot + 1)
            if i == -1:
                break
            else:
                lastDot = i
                
        secondToLastDot = fqdn.find('.',0,lastDot)
        
        if secondToLastDot == -1:
            domainName = fqdn
            recordName = '@'
        else:
            while True:
                i = fqdn.find('.', secondToLastDot + 1, lastDot)
                if i == -1:
                    break
                else:
                    secondToLastDot = i
                    
            domainName = fqdn[secondToLastDot + 1:]
            recordName = fqdn[:secondToLastDot]
        
        return recordName,domainName

    #idempotent A and AAAA record creation for a droplet
    def createNameRecords(self, dropletDef, fqdn):        
        parseResult = self.parseFQDN(fqdn)
        domainName = parseResult[1]
        recordName = parseResult[0]
        
        self.createDomainIfAbsent(domainName)
        
        ipv4 = self.publicAddressIPV4(dropletDef)
        ipv6 = self.publicAddressIPV6(dropletDef)
        if ipv6 is not None:
            ipv6 = ipv6.lower()
        
        foundARecord = False
        foundAAAARecord = False
            
        # if the domain already exists, check the existing domain records
        # if they point to the wrong thing, remove them, if they are
        # correct, set aRecordFound/aaaaRecordFound = true
        domainRecords = self.listDomainRecords(domainName)
        for dr in domainRecords['domain_records']:
            if dr['type'] == 'A':
                if dr['name'] == recordName:        
                    if dr['data'] == ipv4:
                        foundARecord = True
                        logging.info('Correct A record for ' + recordName + '.' + domainName + ' already exists')
                    else:
                        self.deleteDomainRecord(domainName, dr['id'])
                        logging.info('Removed incorrect A record for ' + fqdn + ' pointing to ' + dr['data'])

            if dr['type'] == 'AAAA':
                if dr['name'] == recordName:        
                    if dr['data'].lower() == ipv6:
                        foundAAAARecord = True
                        logging.info('Correct AAAA record for ' + recordName + '.' + domainName + ' already exists')
                    else:
                        self.deleteDomainRecord(domainName, dr['id'])
                        logging.info('Removed incorrect AAAA record for ' + fqdn + ' pointing to ' + dr['data'])

        if not foundARecord and ipv4 is not None:
            self.createDomainRecord(domainName, recordName, ipv4, 'A')
            logging.info('created A record for ' + recordName + '.' + domainName + ' pointing to ' + ipv4)
            
        if not foundAAAARecord and ipv6 is not None:
            self.createDomainRecord(domainName, recordName, ipv6, 'AAAA')
            logging.info('created AAAA record for ' + recordName + '.' + domainName + ' pointing to ' + ipv6)
    

    def removeNameRecords(self, fqdn):
        parseResult = self.parseFQDN(fqdn)
        recordName = parseResult[0]
        domainName = parseResult[1]
    
        # check that the domain exists
        domainExists = False
        for domain in self.listDomains()['domains']:
            if domain['name'] == domainName:
                domainExists = True
                break
            
        if not domainExists:
            logging.info('"' + domainName + '" domain does not exist')
            return
    
        countNonNSRecords = 0
        deletedRecords = 0
        for domainRec in self.listDomainRecords(domainName)['domain_records']:
            if domainRec['type'] != 'NS':
                countNonNSRecords += 1            
                if domainRec['type'] == 'A' or domainRec['type'] == 'AAAA':
                    if domainRec['name'] == recordName:
                        self.deleteDomainRecord(domainName, domainRec['id'])
                        countNonNSRecords -= 1
                        deletedRecords += 1
                        logging.info('removed "' + domainRec['type'] + '" record for ' + fqdn)
                        
        if deletedRecords == 0:
            logging.info('there are no "A" or "AAAA" records for ' + fqdn)
            
        if countNonNSRecords == 0:
            self.deleteDomain(domainName)
            logging.info('deleted DNS domain: ' + domainName)
                        
          
    def undeploy(self,dropletName):
        found = False
        resp = self.listDroplets()
        for droplet in resp['droplets']:
            if droplet['name'] == dropletName:
                found = True
                self.deleteDroplet(droplet['id'])
                logging.info('deleted droplet ' + dropletName)
                
        if found == False:
            logging.info('no droplet named "' + dropletName + '" was found')
                            
    
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
              
    
