#!/usr/bin/env python
from __future__ import print_function
import digitalocean
import json
import os.path
import re
import sys
import time

# droplet is the droplet definition returned by the Digital Ocean
# API, dropletReq is from the cloud definition file
def dropletMatchesRequest(droplet, dropletReq):
    if droplet['image']['slug'] is None:
        return False
    elif droplet['image']['slug'] != dropletReq['image']:
        return False
    
    if droplet['size_slug'] != dropletReq['size']:
        return False
    
    if droplet['region']['slug'] != dropletReq['region']:
        return False
    
    if dropletReq['backups']:
        if 'backups' not in droplet['features']:
            return False
    else:
        if 'backups' in droplet['features']:
            return False
    
    #dont check the name enrtries - if this is a retry of a failed provision
    #then the droplet may exist but the names haven't been created yet
    
    return True

# also validates the request
def createDropletRequest(dropletDef):
    result = dict()
    
    #region
    if 'region' not in dropletDef:
        raise Exception('droplet defintion is missing required property: region')
    
    regionName = dropletDef['region']
    
    if regionName not in regions:
        raise  Exception('droplet definition has unkown or unavailable region: ' + regionName)
    else:
        result['region'] = regionName
        
    #backups
    if 'backups' not in dropletDef:
        raise Exception('droplet defintion is missing required property: backups')
        
    if dropletDef['backups']:
        if 'backups' not in regions[regionName]['features']:
            raise Exception('droplet requested backups, which are not supported in region ' + regionName)
        else:
            result['backups'] = True
    else:
        result['backups'] = False
       
    #image 
    if 'image' not in dropletDef:
        raise Exception('droplet defintion is missing required property: backups')
    
    imageName = dropletDef['image']
    if imageName not in images:
        raise Exception(imageName + ' is not a known image name')
    
    if regionName not in images[imageName]['regions']:
        raise Exception(imageName + ' image does not exist in ' + regionName + ' region')
    
    result['image'] = imageName
    
    #size
    if 'size' not in dropletDef:
        raise Exception('droplet defintion is missing required property: size')
        
    if dropletDef['size'] not in regions[regionName]['sizes']:
        raise Exception(dropletDef['size'] + ' is not a defined size in the ' + regionName + ' region')
    
    result['size'] = dropletDef['size']
    
    if 'ipv6' in regions[regionName]['features']:
        result['ipv6'] = True
    else:
        result['ipv6'] = False
        
    if 'private_networking' in regions[regionName]['features']:
        result['private_networking'] = True
    else:
        result['private_networking'] = False
        
    # currently not supporting user data
    # result['user_data'] = None
    
    return result

if __name__ == '__main__':
    if not os.path.isfile('cloud.json'):
        sys.exit('required file clound.json not found in the current directory')
        
    with open('cloud.json', 'r') as cloudFile:
        cloudDef = json.load(cloudFile)
        
    do = digitalocean.Context()
    
    #grab reference information about regions and images
    resp = do.listRegions()
    regions = dict()
    for region in resp['regions']:
        if region['available']:
            regions[region['slug']] = region
        
    resp = do.listImages()
    images = dict()
    for image in resp['images']:
        if image['slug'] is not None:
            images[image['slug']] = image
            
    resp = do.listDroplets()
    droplets = dict()
    for droplet in resp['droplets']:
        droplets[droplet['name']] = droplet

    provisionedDroplets = dict() #map of droplet name to action id        
    nameRE = re.compile('[a-zA-Z0-9.]+$')        
    for name in cloudDef.keys():
        if nameRE.match(name) is None:
            sys.exit('{0} is an invalid droplet name.  Droplet names may contain numbers, letters and the period character'.format(name))
            
        if name in droplets:
            if dropletMatchesRequest(droplets[name], cloudDef[name]):
                print('a droplet matching {0} already exists'.format(name), file=sys.stderr)
            else:
                sys.exit('a droplet named {0} already exists but with different characteristics'.format(name))
        else:
            dropletRequest = createDropletRequest(cloudDef[name])
            dropletRequest['name'] = name
            resp = do.createDroplet(dropletRequest)
            provisionedDroplets[name] = resp['links']['actions'][0]['id']
            print('droplet ' + name + ' requested in region ' + dropletRequest['region'], file=sys.stderr)
            
    if len(provisionedDroplets) == 0:
        sys.exit(0) #EXIT
        
    # now wait for all droplets to actually be provisioned
    errCount = 0
    print('waiting 60s for droplets to be provisioned', file=sys.stderr)
    time.sleep(60)
    for attempt in range(0,10):
        for name in provisionedDroplets.keys():
            resp = do.getAction(provisionedDroplets[name])
            if resp['action']['status'] == 'completed':
                print('droplet {0} provisioned'.format(name), file=sys.stderr)
                del provisionedDroplets[name]
            elif resp['action']['status'] == 'errored':
                errCount += 1
                print('provisioning of droplet {0} failed'.format(name), file=sys.stderr)
                del provisionedDroplets[name]
        
        if len(provisionedDroplets) == 0:
            break
        
        print('waiting 20s for droplets to be provisioned', file=sys.stderr)
        time.sleep(20)
        
    if errCount > 0:
        raise Exception('{0} droplet(s) could not be provisioned'.format(errCount))
        
    
    