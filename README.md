#Release Notes#

0.7 Added an option to load digital ocean security settings from server.json['digital_ocean']
Also added the templates package with a render method

#Overview#
Cloudmaker makes provisioning servers on Digital Ocean both easy and repeatable.
It also provides simple python methods for doing common setup tasks like
installing packages.

With Cloudmaker, each server is described by a directory which contains 2 files.
* server.json - describes the server to be deployed
* setup.py - a python script that will be run on the server after it has been provisioned

#Prerequisites#
* A Digital Ocean Account
* A Digital Ocean Personal Access Token ( see this
[Digital Ocean Tutorial](https://www.digitalocean.com/community/tutorials/how-to-use-the-digitalocean-api-v2)
for instructions )
* An ssh key.  If you do not already have one, see [this article](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys--2)
for instructions.  Cloudmaker can automatically upload you public ssh key. Cloudmaker
does not need your private ssh key.

#Installation#
`pip install cloudmaker`

#Setup#
* create ~/.cloudmaker.json similar to the one below containing your digital
ocean api key and the public portion of the ssh key you will use to accesss
your servers.

```json
{
    "digital_ocean_api_key" : "fjejhuiu9880hthisimadeup0845943unsff4utrjd"
    ,"public_ssh_key" : "ssh-rsa fr99bjr9urugrbtthisisalsomadeupPDQ fredy@acme.com"
}
```

* test by running `cloudmaker inventory`.  You should see something like the
following:

```
loaded security information from /Users/randy/cloudmaker/~/.cloudmaker.json
ssh key already registered
wrote inventory to file: "inventory.json"
```

#Walk Through: Using Cloudmaker to Deploy a Server with Apach2 and MySQL Server#

* Create a new directory: "myserver".  Edit "myserver/server.json" to look
something like the one below

```json
{
    "digitalocean" : {
        "provision": {
            "name" : "myserver"
            , "region" : "nyc3"
            , "size" : "512mb"
            , "image" :  "debian-7-0-x64"
            , "backups" : false,
            , "dnsRecords" : ["myserver.com","www.myserver.com"]
        }
    }
}
```

* In the same dirctory, create an install script for your server called
"setup.py" with contents similar to the following:

```python
#!/usr/bin/python

import logging
import sys

from cloudmaker.linux import *

logging.basicConfig(level='INFO')

passw = 'my-db-pass'
debconfSetSelections('mysql-server', 'mysql-server/root_password', 'password', passw)
debconfSetSelections('mysql-server', 'mysql-server/root_password_again', 'password', passw)
aptInstall('mysql-server')
aptInstall('apache2')
```

* Deploy it!  

```
cloudmaker deploy myserver
```

* To undeploy everything and remove the name records, just run:

```
cloudmaker undeploy myserver
```

THATS IT!

#Implementation Notes#
Provisioning proceeds in the following order:
1. If the ssh key provided in _security.json_ is not present within your
Digital Ocean account, it is uploaded.
2. The server is provisioned. If provided, the server will be provisioned
with your public ssh key so you will be able to access it with
passwordless ssh
3. The requested DNS records are created / verified . If there is already a
record with the requested name, mapped to another server, that one will be
removed and a correct one will be created. Currently only "A" records are
created.


#Reference#


__sample inventory.json file__


```json
{
   "server1": {
      "names": [
         "server1.acme.com", 
         "acme.com"
      ], 
      "region": "nyc3", 
      "private_network_interfaces": {
         "ipv4": "10.132.247.60"
      }, 
      "public_network_interfaces": {
         "ipv4": "45.55.221.186", 
         "ipv6": "2604:a880:0800:0010:0000:0000:0060:c001"
      }, 
      "backups": false, 
      "image": "debian-7-0-x64", 
      "size": "1gb"
   }, 
   "server2": {
      "names": [
         "server2.acme.com"
      ], 
      "region": "nyc3", 
      "private_network_interfaces": {
         "ipv4": "10.132.241.32"
      }, 
      "public_network_interfaces": {
         "ipv4": "45.55.221.139", 
         "ipv6": "2604:a880:0800:0010:0000:0000:0060:e001"
      }, 
      "backups": false, 
      "image": "debian-7-0-x64", 
      "size": "1gb"
   }
}
```

__Valid Values for Digital Ocean Size, Region and Image Attributes__

Sizes
* "512mb"
* "1gb"
* "2gb"
* "4gb"
* "8gb"
* "16gb"
* "32gb"
* "48gb"
* "64gb"

Regions
* "nyc1"
* "ams1"
* "sfo1"
* "nyc2"
* "ams2"
* "sgp1"
* "lon1"
* "nyc3"
* "ams3"
* "fra1"

Images
* "coreos-stable"
* "coreos-beta"
* "coreos-alpha"
* "centos-5-8-x64"
* "centos-5-8-x32"
* "debian-6-0-x64"
* "debian-6-0-x32"
* "fedora-21-x64"
* "ubuntu-14-10-x32"
* "ubuntu-14-10-x64"
* "freebsd-10-1-x64"
* "ubuntu-12-04-x64"
* "ubuntu-12-04-x32"
* "debian-7-0-x64"
* "debian-7-0-x32"
* "centos-7-0-x64"
* "centos-6-5-x32"
* "centos-6-5-x64"
* "ubuntu-14-04-x64"
* "ubuntu-14-04-x32"
* "fedora-22-x64"
* "debian-8-x64"
* "ubuntu-15-04-x64"
* "debian-8-x32"
* "ubuntu-15-04-x32"
