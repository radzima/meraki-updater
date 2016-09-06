#!/usr/bin/env python
"""
Usage: 
  Update devices in a single network from CSV:
    meraki-updater.py -k <MERAKI-PROVISIONING-API-KEY> -f <CSV-UPDATE-FILE>

  Update devices from a CSV with network specified per device:
    meraki-updater.py -k <MERAKI-PROVISIONING-API-KEY> -m -f <CSV-UPDATE-FILE>

  Write all devices on all accessible networks to a CSV (This file WILL be overwritten):
    meraki-updater.py -k <MERAKI-PROVISIONING-API-KEY> -g -o <CSV-OUTPUT-FILE>

  Arguments:
    -k/--key            Set the Meraki Provisioning API key (required)
    -f/--file           Set the CSV file to read for device updates
    -o/--output         Set the CSV file to write network devices (This file WILL be overwritten)
    -g/--get            Get network devices from all networks and write them to CSV
    -m/--multinetwork   Update devices across multiple networks using a CSV
    -v/--ver/--version  Display the version of this script
"""

from __future__ import print_function
import os,sys,getopt,csv,json,requests
from os.path import expanduser
from time import sleep

version = 1.1
ver = sys.version_info[0] > 2

multiNetUpdate = False
getDevices = False
apikey = None
network = None
updateFile = None
outputFile = None
organization = None
headers = None
dashboard_url = 'https://dashboard.meraki.com/'
api_url = dashboard_url + 'api/v0/'

class Usage(Exception):
    def __init__(self,msg):
        self.msg = msg

def usage(msg=None):
    print(__doc__)
    if msg:
        print(msg)
    return 0

def promptUser(options,msg='Choose one'):
    print()
    while True:
        for choice in sorted(options):
            print('  ' + choice,end=':')
            if 'id' in options[choice]:
                print(' [' + str(options[choice]['id']) + ']',end='')
                print(' ' + options[choice]['name'])
        print()
        if ver:
            res = input(msg + ': ')
        else:
            res = raw_input(msg + ': ')
        print()
        if res in options:
            c = options[res]
            return c
        else:
            print('Incorrect choice, try again.')

def getNetworkDevices(net,addNetID=False):
    url = api_url + 'networks/' + str(net['id']) + '/devices/'
    devices = json.loads(requests.get(url,headers=headers).text)
    if addNetID:
        for i,device in enumerate(devices):
            devices[i]['network_id'] = net['id']
    return devices

def writeToFile(data):
    print('Writing to {}...'.format(outputFile))
    try:
        with open(outputFile,'wb') as output:
            writer = csv.DictWriter(output,fieldnames=['serial','name','tags','lat','lng','address','mac','model','network_id'],extrasaction='ignore')
            writer.writeheader()
            for row in data:
                writer.writerow(row)
    except IOError,msg:
        usage('IOError: {}'.format(msg))

def updateDevices():
    print('Reading from {}...'.format(updateFile))
    try:
        with open(updateFile,'rU') as updates:
            reader = csv.DictReader(updates)
            for row in reader:
                options = {
                        'serial':row['serial'],
                        'name':row['name'],
                        'tags': row['tags'],
                        'lat': row['lat'],
                        'lng': row['lng'],
                        'address': row['address']
                        }
                print('Updating {} from file...'.format(row['serial']),end='')
                sys.stdout.flush()
                if multiNetUpdate:
                    try:
                        net_id = row['network_id']
                    except:
                        print('Failed!')
                        print('Network not specified in CSV, continuing...')
                        continue
                else:
                    net_id = str(network['id'])
                url = api_url + "networks/" + net_id + "/devices/" + options['serial']
                try:
                    d = json.loads(requests.get(url,headers=headers).text)
                except:
                    print(' Failed!')
                    print('Device {} not found in network {}, continuing...'.format(options['serial'],net_id))
                    continue
                payload = {}
                if options['name']:
                    payload['name'] = options['name']
                if options['tags']:
                    payload['tags'] = options['tags']
                if options['lat']:
                    payload['lat'] = options['lat']
                if options['lng']:
                    payload['lng'] = options['lng']
                if options['address']:
                   payload['address'] = options['address']
                payload['mac'] = d['mac']
                payload['serial'] = options['serial']
                data = json.dumps(payload)
                try:
                    r = requests.put(url,headers=headers, data=data)
                    if r.status_code == 200:
                        print(' Success!')
                    else:
                        print(' Failed!')
                        print(r.content)
                except:
                    print('Cannot update device {}, continuing...'.format(options['serial']))
                    continue
    except IOError,e:
        print('Error reading file.',e)
    except Exception,e:
        print('Error.',e)

def getOrgs():
    try:
        url = api_url + 'organizations/'
        orgs = json.loads(requests.get(url,headers=headers).text)
        orgDict = {}
        x = 1
        for org in orgs:
            orgDict[str(x)] = org
            x += 1
        return orgDict
    except Exception,e:
        sys.exit('Unable to retrieve organizations.',e)

def getNets(org):
    try:
        print('Getting networks for {}...'.format(org['name']))
        url = api_url + 'organizations/' + str(org['id']) + '/networks'
        nets = json.loads(requests.get(url,headers=headers).text)
        netDict = {}
        x = 1
        for net in nets:
            netDict[str(x)] = net
            x += 1
        return netDict
    except Exception,e:
        sys.exit('Unable to retrieve networks.',e)

def setFile(f,create=False):
    try:
        if '~' in f:
            f = str.replace('~',expanduser('~'))
        if os.path.isfile(f):
            print('File {} found, continuing...'.format(f))
            return f
        else:
            if create:
                c = open(f,'w')
                c.write('')
                c.close()
            else:
                usage('File {} not found.'.format(f))
    except IOError,msg:
        usage('File error. {}'.format(msg))

def setHeaders(key):
    global headers
    headers = {
        'X-Cisco-Meraki-API-Key': key,
        'Content-Type': 'application/json'
        }
    return True

def parseOptions(argv):
    global apikey
    global network
    global updateFile
    global getDevices
    global outputFile
    global multiNetUpdate
    while True:
        try:
            try:
                opts,args = getopt.getopt(argv[1:],'hgmvk:f:o:',['output=','get','ver','version','help','key=','file=','multinetwork'])
            except getopt.error,msg:
                return usage('Error: {}'.format(msg))
            for o,a in opts:
                if o in ('-h','--help'):
                    usage()
                    return 0
                elif o in ('-f','--file'):
                    updateFile = setFile(a)
                elif o in ('-k','--key'):
                    apikey = a
                    setHeaders(apikey)
                elif o in ('-v','--ver','--version'):
                    print('Meraki Device Updater Version: {}'.format(version))
                    return 0
                elif o in ('-g','--get'):
                    getDevices = True
                elif o in ('-o','--output'):
                    outputFile = setFile(a,True)
                elif o in ('-m','--multinetwork'):
                    multiNetUpdate = True
                else:
                    return usage('Error: Unknown option, exiting...')
            if not apikey:
                return usage('Error: API key (-k/--key) not provided, exiting.')
            if not outputFile and getDevices:
                return usage('Error: Output file (-o/--output) not provided, exiting.')
            if not updateFile and not getDevices:
                return usage('Error: Input file (-f/--file) not provided, exiting.')
            break
        except Exception,msg:
            return usage('Error initializaing. {}'.format(msg))
    return 1
            

def main(argv=None):
    global organization
    global network
    if argv is None:
        argv = sys.argv
        init = parseOptions(argv)
        if init == 0:
            return 0
        elif init == 1:
            if getDevices:
                orgs = getOrgs()
                while True:
                    if len(orgs) > 1:
                        try:
                            organization = promptUser(orgs,'Select an organization')
                            break
                        except Exception,e:
                            print(e)
                    else:
                        organization = orgs['1']
                        break
                nets = getNets(organization)
                allDevices = []
                for net in nets:
                    devices = getNetworkDevices(nets[net],True)
                    for d in devices:
                        allDevices.append(d)
                writeToFile(allDevices)
                return 0
            else:
                print('Getting organizations for this account...')
                orgs = getOrgs()
                while True:
                    if len(orgs) > 1:
                        try:
                            organization = promptUser(orgs,'Select an organization')
                            break
                        except Exception,e:
                            print(e)
                    else:
                        organization = orgs['1']
                        break
                if not multiNetUpdate:
                    nets = getNets(organization)
                    while True:
                        if len(nets) > 0:
                            try:
                                network = promptUser(nets,'Select a network')
                                break
                            except Exception,e:
                                print(e)
                while True:
                    try:
                        updateDevices()
                        break
                    except Exception,e:
                        print('Unable to process...',e)
                return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except (KeyboardInterrupt):
        sys.exit('User cancelled, exiting.')
