#Overview#
Cloudbuilder provisions your Digital Ocean script based on a JSON cloud
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

#Setup#

1. Create a directory to hold the configuration files for your cloud deployment.
2. Copy the cloudmaker python scripts into that directory.
3. Create _security.json_ containing your Digital Ocean API key and the
public portion of the ssh key that you will use to log on to your servers.
An example is show below:
```json
{
    "digital_ocean_api_key" : "fjejhuiu9880hthisimadeup0845943unsff4utrjd"
    ,"public_ssh_key" : "ssh-rsa fr99bjr9urugrbtthisisalsomadeupPDQ fredy@acme.com"
}```
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