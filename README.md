# meraki-updater
Update Meraki devices in a network using the provisioning API. Any information in the CSV will overwrite the dashboard values (including tags) so anything that should not be updated should be empty as shown in the example file. The CSV file should have the following columns: serial,name,tags,lat,lng,address.

Usage:

  Update devices in a single network from CSV:

        meraki-updater.py -k <MERAKI-PROVISIONING-API-KEY> -f <CSV-UPDATE-FILE>

  Write all devices on all accessible networks to a CSV (This file WILL be overwritten):

        meraki-updater.py -k <MERAKI-PROVISIONING-API-KEY> -g -o <CSV-OUTPUT-FILE>

  Arguments:

        -k/--key            Set the Meraki Provisioning API key (required)
        -f/--file           Set the CSV file to read for device updates
        -o/--output         Set the CSV file to write network devices (This file WILL be overwritten)
        -g/--get            Get network devices from all networks and write them to CSV
        -v/--ver/--version  Display the version of this script

<br />
---
Ryan M. Adzima<br />
Twitter: [@radzima](https://twitter.com/radzima)<br />
Blog: [Techvangelist.net](https://techvangelist.net)<br />
