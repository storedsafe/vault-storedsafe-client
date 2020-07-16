#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
vault-storedsafe-client.py: ansible vault password client script for StoredSafe
"""

import sys
import os
import os.path
import sys
import socket
import getopt
import re
import base64
import traceback
import requests
import json
import pprint

__author__     = "Fredrik Soderblom"
__copyright__  = "Copyright 2020, AB StoredSafe"
__license__    = "GPL"
__version__    = "1.0.1"
__maintainer__ = "Fredrik Soderblom"
__email__      = "fredrik@storedsafe.com"
__status__     = "Production"

# Globals

url              = False
token            = False
verbose          = False
debug            = False
VAULT_ID_UNKNOWN_RC	= 2

def main():
  global token, url, verbose, debug
  rc_file = os.path.expanduser('~/.storedsafe-client.rc')

  try:
    opts, args = getopt.getopt(sys.argv[1:], "h?", \
      [ "verbose", "debug", "vault-id=", "help" ])

  except getopt.GetoptError as err:
    sys.stderr.write("%s\n" % str(err))
    usage()
    sys.exit(VAULT_ID_UNKNOWN_RC)

  if opts:
    for opt, arg in opts:
      if opt in ("--verbose"):
        verbose = True
      elif opt in ("--debug"):
        debug = True
        verbose = True
      elif opt in ("--vault-id"):
        vault_id = arg
      elif opt in ("-?", "-h", "--help"):
        usage()
        sys.exit(VAULT_ID_UNKNOWN_RC)
      else:
        assert False, "Unrecognized option"
  else:
    usage()
    sys.exit(VAULT_ID_UNKNOWN_RC)

  (storedsafe, token) = readrc(rc_file)
  url = "https://" + storedsafe + "/api/1.0"
  
  if not authCheck():
    sys.exit(VAULT_ID_UNKNOWN_RC)

  try:
    object_id = int(vault_id)
    secret = getPassword(vault_id)
  except ValueError:
    secret = searchForCredentials(vault_id)
  
  if secret:
    sys.stdout.write('%s\n' % secret)
  else:
    sys.exit(VAULT_ID_UNKNOWN_RC)

  sys.exit(0)

def usage():
  print("Usage: %s --vault-id <object-id|search-string>" % sys.argv[0])
  print(" --verbose                  (Boolean) Enable verbose output.")
  print(" --debug                    (Boolean) Enable debug output.")
  print(" --vault-id <Object-ID>     Obtain the decrypted password from the object with the matching Object-ID (integer).")
  print(" --vault-id <String>        Search for the string, return decrypted password field from last matching object.")
  print("\nObtain the decrypted password for the specified Object-ID (919) from StoredSafe.")
  print("\n$ %s --vault-id 919" % sys.argv[0])
  print("\nSearch all available vaults for hostname or user matching the search string and return decrypted password from last matching object.")
  print("\n$ %s --vault-id prod-sweden-vars" % sys.argv[0])

def readrc(rc_file):
  if os.path.isfile(rc_file):
    f = open(rc_file, 'r')
    for line in f:
      if "token" in line:
        token = re.sub('token:([a-zA-Z0-9]+)\n$', r'\1', line)
        if token == 'none':
          sys.stderr.write("ERROR: No valid token found in \"%s\". Have you logged in?\n" % rc_file)
          sys.exit(VAULT_ID_UNKNOWN_RC)
      if "mysite" in line:
        server = re.sub('mysite:([a-zA-Z0-9.]+)\n$', r'\1', line)
        if server == 'none':
          sys.stderr.write("ERROR: No valid server specified in \"%s\". Have you logged in?\n" % rc_file)
          sys.exit(VAULT_ID_UNKNOWN_RC)
    f.close()
    if not token:
      sys.stderr.write("ERROR: Could not find a valid token in \"%s\"\n" % rc_file)
      sys.exit(VAULT_ID_UNKNOWN_RC)
    if not server:
      sys.stderr.write("ERROR: Could not find a valid server in \"%s\"\n" % rc_file)
      sys.exit(VAULT_ID_UNKNOWN_RC)
    return (server, token)
  else:
    sys.stderr.write("ERROR: Can not open \"%s\".\n" % rc_file)
    sys.exit(VAULT_ID_UNKNOWN_RC)

def authCheck():
  global token, url, verbose, debug

  payload = { 'token': token }
  try:
    r = requests.post(url + '/auth/check', data=json.dumps(payload))
  except:
    sys.stderr.write("ERROR: Can not reach \"%s\"\n" % url)
    return(False)

  if not r.ok:
    sys.stderr.write("Not logged in to StoredSafe.\n")
    return(False)

  data = json.loads(r.content)
  if data['CALLINFO']['status'] == 'SUCCESS':
    if debug: sys.stderr.write("DEBUG: Authenticated using token \"%s\".\n" % token)
  else:
    sys.stderr.write("ERROR: Session not authenticated with server. Token invalid?\n")
    return(False)
  
  return(True)

def searchForCredentials(search):
  secret = False
  payload = { 'token': token, 'needle': search }
  r = requests.get(url + '/find', params=payload)
  data = json.loads(r.content)
  if not r.ok:
    return(False)
  
  if (len(data['OBJECT'])): # Unless result is empty
    for object in data["OBJECT"]:
      if (search == object['public']['host']) or (search == object['public']['username']):
        if verbose: sys.stderr.write("Found match for \"%s\" (Object-ID %s in Vault-ID %s)\n" % (search, object['id'], object['groupid']))
        secret = getPassword(object['id'])
  
  if secret:
    return(secret)
  else:
    sys.stderr.write("WARNING: Could not find credentials matching the search string \"%s\".\n" % search)
    return(False)

def getPassword(id):
  payload = { 'token': token, 'decrypt': 'true' }
  r = requests.get(url + '/object/' + str(id), params=payload)
  data = json.loads(r.content)
  if not r.ok:
    return(False)

  try:
    if (len(data['OBJECT'][0]['crypted']['password'])):
      return(data['OBJECT'][0]['crypted']['password'])
  except:
    sys.stderr.write("WARNING: Could not find any credentials in Object-ID \"%s\".\n" % id)
    return(False)

if __name__ == '__main__':
  main()
