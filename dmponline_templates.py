#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from dotenv import load_dotenv
from datetime import datetime
import os
import uuid
import time

# Simple script that harvests all templates from DMPonline in order to get correct template ids.
# Todo: currently only get up to 100 entries (1 page). At the moment this is sufficient.
# Example: ./python3 dmponline_export_templates.py 
#
# / urban.andersson@chalmers.se
# // matves29@kth.se

# Settings
load_dotenv()  # loads the .env file which contains login-information 
dmpurl = os.getenv("DMPONLINE_API_URL")
dmpuser = os.getenv("DMPONLINE_USER")
dmppw = os.getenv("DMPONLINE_PW")
dmp_id_prefix = os.getenv("DMP_ID_PREFIX")
logfile = os.getenv("LOGFILE")

# Input params
parser = ArgumentParser(description="Create new DMP using data from Swecris.",
                        formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-v", "--verbose", action="store_true", help="increase verbosity")
#parser.add_argument("-i", "--grantid", default="", help="Grant ID, i.e. 2023-012345", required=True)
args = parser.parse_args()

# Create Swecris ID and look up corresponding project in Swecris API
#grantid = args.grantid


# Go ahead and create DMP in DMPOnline from here...
print('Should I fetch all templates from DMPonline? (y/n)')
yes = {'yes', 'y', 'ye', 'j', 'ja', ''}
no = {'no', 'n', 'nej'}
choice = input().lower()
if choice in yes:

    # Authorize
    dmp_auth_bearer = ""
    dmp_auth_url = os.getenv("DMPONLINE_API_URL") + "authenticate"
    auth_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    auth_body = {
        "grant_type": "authorization_code",
        "email": os.getenv("DMPONLINE_USER"),
        "code": os.getenv("DMPONLINE_AUTH_CODE"),
    }
    try:
        authdata = requests.post(
            url=dmp_auth_url, json=auth_body, headers=auth_headers
        ).text
            
        if "Internal server error" in authdata:
            print("Authentication request failed! Exiting.")
            exit()

        authdata = json.loads(authdata)
        dmp_auth_bearer = authdata["access_token"]
            
        print("Authorized! Access token: " + dmp_auth_bearer)

    except requests.exceptions.HTTPError as e:
        print("Failed! authdata: " + authdata)
        exit()

        # Request templates using the authentication token (mainly as a test)
    try:
        dmp_template_url = os.getenv("DMPONLINE_API_URL") + 'templates'
        template_headers = {'Accept': 'application/json','Authorization': 'Bearer ' + dmp_auth_bearer}
                
        templatedata = requests.get(url=dmp_template_url, headers=template_headers).text
        print(templatedata)
        if not os.path.exists('Templates'):
            os.makedirs('Templates')
        
        timestr = time.strftime("%Y%m%d-%H%M%S") 
        filename = "Templates_from_DMPonline_" + timestr + ".json"
        path = os.path.join('Templates', filename)
        out_file = open(path, "w",encoding="utf-8") 
        out_file.write(templatedata) 
        out_file.close()
        print("Stored as: " + path)
       
                  
    except requests.exceptions.HTTPError as e:
        print('Failed! templatedata: ' + templatedata)          
        exit()

elif choice in no:
    print('OK. Will exit then.')
    exit()
else:
    sys.stdout.write("Please respond with 'y'(es) or 'n'(o)")

exit()
