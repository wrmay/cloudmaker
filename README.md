#Release Notes#

1.0 With cloudmaker 1.0, the ability to not only provision, but completely
set up your machines has been added.

#Overview#
Cloudmaker makes provisioning servers on Digital Ocean both easy and repeatable.
You define your inventory in a json cloud definition file and Cloudmaker takes
care deploying to Digital Ocean including setting up your DNS records.

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
}
```

#Usage#

Cloudmaker supports the following commands:

```
cloudmaker deploy <cloud_def.json>
```
Deploys a collection of resources desribed by a cloud defintion file. See the
reference section for details of the format.

Provisioning is idempotent so if there is a failure part of the way through the
provision command can be run again without harm.

Provisioning proceeds in the following order:
1. If the ssh key provided in _security.json_ is not present within your
Digital Ocean account, it is uploaded.
2. The servers are provisioned. If provided, the server will be provisioned
with your public ssh key so you will be able to access it with
passwordless ssh
3. The requested DNS records are created / verified for each server. If
there is already a record with the requested name, mapped to another server,
provisioning will fail.  If the provisioned server supports  ipv6 then an
'AAAA' record will be created pointing to its public ipv6 interface in addition to
an 'A' record pointing to its public ipv4 interface.
4. The full inventory of droplets provisioned in the Digital Ocean account
(whether provisioned by cloudmaker or something else) is written to
_inventory.json_ in the current directory.  This file contains useful
information that cannot be known before provisioning, such as the ip addresses
of provisioned servers

If the region where a droplet is provisioned supports IPv6, it will
automatically be enabled. Similarly, if a region supports private networking,
it will be enabled on droplets provisioned to that region.   


```
cloudmaker undeploy <cloud_def.json>
```
All droplets defined in the cloud definition file are destroyed.  A records
and AAAA records pointing to the droplet are removed.  If no DNS records
other than NS records remain in the zone file, the whole domain will be removed.
After processing is complete, _inventory.json_ will be updated to reflect the
new state.

```
cloudmaker inventory
```
Updates the _inventory.json_ with the latest information.

#Reference#

__Cloud Definition File Format__

An example is shown below. Valid values for region, size and image appear at
the bottom of the page.

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

__inventory.json File Format__

The _inventory.json_ file is similar to the cloud definition file with
additional information describing the network interfaces of provisioned
droplets.  Note that cloudmaker automatically matches DNS A records and AAAA
records with droplets.  The names associated with each droplet are recorded in
the _names_ attribute.

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
   

__Valid Values for Various Attributes__

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
