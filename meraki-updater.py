#!/usr/bin/env python
"""
Usage: meraki-updater.py -k MERAKI-PROVISIONING-API-KEY -f CSV-UPDATE-FILE

Required arguments:
    -k/--key            Set the Meraki Provisioning API key
    -f/--file           Set the file to read for device updates

Optional arguments:
    -v/--ver/--version  Display the version of this script
"""

from __future__ import print_function
import os,sys,getopt,csv,json,requests
from os.path import expanduser
from time import sleep

version = 1.0
ver = sys.version_info[0] > 2

apikey = None
network = None
updateFile = None
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

def updateDevices():
    print('Reading from {}...'.format(updateFile))
    try:
        with open(updateFile,'rb') as updates:
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
                print('Updating {} from file...'.format(row['serial']))
                url = api_url + "networks/" + str(network['id']) + "/devices/" + options['serial']
                d = json.loads(requests.get(url,headers=headers).text)
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
                print(data)
                r = requests.put(url,headers=headers, data=data)
                print('Status code',r.status_code,end=': ')
                if r.status_code == 200:
                    print('Success!')
                else:
                    print('Failed!')
                    print(r.content)
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

def setFile(f):
    try:
        if '~' in f:
            f = str.replace('~',expanduser('~'))
        if os.path.isfile(f):
            print('File {} found, continuing...'.format(f))
            return f
        else:
            sys.exit('File {} not found.'.format(f))
    except IOError,msg:
        sys.exit('File error.',msg)

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
    while True:
        try:
            try:
                opts,args = getopt.getopt(argv[1:],'hvk:f:',['ver','version','help','key=','file='])
            except getopt.error,msg:
                return usage('Error:',msg)
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
                else:
                    return usage('Error: Unknown option, exiting...')
            if not apikey:
                return usage('Error: -k option not provided, exiting.')
            if not updateFile:
                return usage('Error: -f option not provided, exiting.')
            break
        except Exception,msg:
            return usage('Error initializaing.')
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
