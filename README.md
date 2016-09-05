# meraki-updater
Update Meraki devices in a network using the provisioning API. Any information in the CSV will overwrite the dashboard values (including tags) so anything that should not be updated should be empty as shown in the example file. The CSV file should have the following columns: serial,name,tags,lat,lng,address.

        meraki-updater.py -k MERAKI-PROVISIONING-API-KEY -f CSV-UPDATE-FILE

            Required arguments:
                -k/--key            Set the Meraki Provisioning API key
                -f/--file           Set the file to read for device updates

            Optional arguments:
                -v/--ver/--version  Display the version of this script

<br />
---
Ryan M. Adzima<br />
Twitter: [@radzima](https://twitter.com/radzima)<br />
Blog: [Techvangelist.net](https://techvangelist.net)<br />
