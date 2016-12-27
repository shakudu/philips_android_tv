from base64 import b64encode,b64decode
from datetime import datetime
import json
import sys
import requests
import random
import string
from Crypto.Hash import SHA, HMAC
from requests.auth import HTTPDigestAuth
import argparse

# Key used for generated the HMAC signature
secret_key="ZmVay1EQVFOaZhwQ4Kv81ypLAZNczV9sG4KkseXWn1NEk6cXmPKO/MCa9sryslvLCFMnNe4Z4CPXzToowvhHvA=="

def createDeviceId():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(16))


def create_signature(secret_key, to_sign):
    sign = HMAC.new(secret_key, to_sign, SHA)
    return b64encode(sign.hexdigest())

def getDeviceSpecJson():
    device_spec =  { "device_name" : "heliotrope", "device_os" : "Android", "app_name" : "ApplicationName", "type" : "native" }
    device_spec['app_id'] = config['application_id']
    device_spec['id'] = config['device_id']
    return device_spec


def pair(config):
    config['application_id'] = "app.id"
    config['device_id'] = createDeviceId()
    data = { 'scope' :  [ "read", "write", "control"] }
    data['device']  = getDeviceSpecJson()
    print("Starting pairing request")
    r = requests.post("https://" + config['address'] + "1926:/6/pair/request", json=data, verify=False)
    response = r.json()
    auth_Timestamp = response["timestamp"]
    config['auth_key'] = response["auth_key"]
    auth_Timeout = response["timeout"]

    pin = input("Enter onscreen passcode: ")

    auth = { "auth_AppId" : "1" }
    auth ['pin'] = str(pin)
    auth['auth_timestamp'] = auth_Timestamp
    auth['auth_signature'] = create_signature(b64decode(secret_key), str(auth_Timestamp) + str(pin))

    grant_request = {}
    grant_request['auth'] = auth
    grant_request['device']  = getDeviceSpecJson()

    print("Attempting to pair")
    r = requests.post("https://" + config['address'] +":1926/6/pair/grant", json=grant_request, verify=False,auth=HTTPDigestAuth(config['device_id'], config['auth_key']))
    print("Username for subsequent calls is: " + config['device_id'])
    print("Password for subsequent calls is: " + config['auth_key'])

def get_Volume(config):
    r = requests.get("https://" + config['address'] + ":1926/6/audio/volume", verify=False,auth=HTTPDigestAuth(config['device_id'], config['auth_key']))
    print(r.json())



def main():
    config={}
    parser = argparse.ArgumentParser(description='Control a HuaFan WifiSwitch.')
    parser.add_argument("--host", dest='host', help="Host/address of the TV")
    parser.add_argument("--user", dest='user', help="Username")
    parser.add_argument("--pass", dest='password', help="Password")
    parser.add_argument("command",  help="Command to run")

    args = parser.parse_args()

    config['address'] = args.host
 
    if args.command == "pair":
        pair(config)

    config['device_id'] = args.user
    config['auth_key'] = args.password

    if args.command == "get_volume":
        get_Volume(config)


main()




