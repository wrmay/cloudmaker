#Overview#
Cloudmaker makes provisioning servers on Digital Ocean both easy and repeatable.

#Prerequisites#
* A Digital Ocean Account
* A Digital Ocean Personal Access Token ( see this
[Digital Ocean Tutorial](https://www.digitalocean.com/community/tutorials/how-to-use-the-digitalocean-api-v2)
for instructions )
* An ssh key.  If you do not already have one, see [this article](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys--2)
for instructions.  Cloudmaker can automatically upload you public ssh key. Cloudmaker
does not need your privte ssh key.

#Installation#
`pip install cloudmaker`

#Setup#
1. Create a directory to hold the configuration files for your cloud deployment.
You must use a different directory for each Digital Ocean account.
2. Create _security.json_ containing your Digital Ocean API key and the
public portion of the ssh key that you will use to log on to your servers.
An example is show below:
```json
{
    "digital_ocean_api_key" : "fjejhuiu9880hthisimadeup0845943unsff4utrjd"
    ,"public_ssh_key" : "ssh-rsa fr99bjr9urugrbtthisisalsomadeupPDQ fredy@acme.com"
}```

#Usage#
__Generate an inventory of servers  deployed in your Digital Ocean account__

```cloudmaker inventory```

This command will write a file similar to the one below describing the servers
currently deployed.

```
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
NOTES 

* Cloudmaker automatically matches DNS A records and AAAA records with
droplets.  The names matching associated with each droplet are recorded in
the _names_ attribute.
* Each time a cloudmaker command is run, the _cloudmaker\_inventory.json_ file
is updated with the latest information.


your Digital Ocean script based on a JSON cloud
definition.  Provisioning is idempotent so if there is a failure part of the
way through provisioning, it can be run again without harm.

Provisioning proceeds in the following order:
1. If the ssh key provided in _security.json_ is not present within your
Digital Ocean account, it is uploaded.
2. The servers are provisioned.
3. The requested DNS records are created / verified for each server. If
there is already a record with the requested name, mapped to another server,
provisioning will fail.  If the provisioned server supports  ipv6 then an
'AAAA' record will be created pointing to its ipv6 interface (in addition to
an 'A' record pointing to its ipv4 interface).
4. The networking configuration of any provisioned droplets is written back
into _cloud.json_.

4. Create _cloud.json_ to describe what you want to deploy.  See the exammple
below.
```json
{
    "server1" : {
          "region" : "nyc3"
        , "size" : "1gb"
        , "image" :  "debian-7-0-x64"
        , "backups" : false
        , "names" : [ "server1.acme.com", "acme.com"]
    }
    ,"server2" : {
          "region" : "nyc3"
        , "size" : "1gb"
        , "image" :  "debian-7-0-x64"
        , "backups" : false
        , "names" : [ "server2.acme.com"]
    }
}
```
See the reference section for possible values of region, size and image. If the
region supports IPv6, it will automatically be enabled. If the region supports
private networking, it will be enabled. The ssh key defined in _security.json_
will automatically be associated with all created droplets.  
   

#Reference#

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
