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

# Simple script for dowloading DMP:s from DMP Online using the API V1 (which does comply with the RDA json scheme).
# Example: ./python3 dmponline2file.py -i 135516
#
# / matves29@kth.se
#

# Settings
load_dotenv()
dmpurl = os.getenv("DMPONLINE_API_URL_V1")
dmpuser = os.getenv("DMPONLINE_USER")
dmppw = os.getenv("DMPONLINE_PW")
dmp_id_prefix = os.getenv("DMP_ID_PREFIX")
logfile = os.getenv("LOGFILE")

# Input params
parser = ArgumentParser(
    description="est script for downloading a specific DMP from the DMPonline API V1.",
    formatter_class=ArgumentDefaultsHelpFormatter,
)
parser.add_argument("-v", "--verbose", action="store_true", help="increase verbosity")
parser.add_argument("-i", "--planid", default="", help="DMP online ID", required=False)
args = parser.parse_args()

dmpid = args.planid

# Go ahead and create DMP in DMPOnline from here...
print(
    "Should I download a plan through the v1 API and save it as a JSON? (y/n)"
)
yes = {"yes", "y", "ye", "j", "ja", ""}
no = {"no", "n", "nej"}
choice = input().lower()
if choice in yes:
    # Authorize
    dmp_auth_bearer = ""
    dmp_auth_url = os.getenv("DMPONLINE_API_URL") + "authenticate"
    auth_headers = {"Accept": "application/json", "Content-Type": "application/json"}
    auth_body = {
        "grant_type": "authorization_code",
        "email": os.getenv("DMPONLINE_USER"),
        "code": os.getenv("DMPONLINE_AUTH_CODE"),
    }
    try:
        authdata = requests.post(
            url=dmp_auth_url, json=auth_body, headers=auth_headers
        ).text

        print(authdata)
        
        if "Internal server error" in authdata:
            print("Authentication request failed! Exiting.")
            exit()

        authdata = json.loads(authdata)
        
        print(authdata)
        
        dmp_auth_bearer = authdata["access_token"]

        print("Authorized! Access token: " + dmp_auth_bearer)

    except requests.exceptions.HTTPError as e:
        print("Failed! authdata: " + authdata)
        exit()

   

    # Request a specific plan using the authentication token 
    print("")
    print(
        "###############################################################################################################"
    )
    print("Now I will try to download a specific plan from dmp.kth.se")
    print("")
    try:
        dmp_plan_url = os.getenv("DMPONLINE_API_URL") + "plans/" + dmpid
        
        plan_headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + dmp_auth_bearer,
        }

        plandata = requests.get(url=dmp_plan_url, headers=plan_headers).text
        
        if "Internal server error" in plandata:
            print("Authentication request failed! Exiting.")
            exit()
        else:    
            print("Success! Retireved the following:")
            print(plandata)
            print("#######################")
            print("Plan retrieved from: " + dmp_plan_url)

        

        if not os.path.exists('Downloaded_plans'):
            os.makedirs('Downloaded_plans') 
        filename = dmpid + "_API_V1_dmp.json"
        path = os.path.join('Downloaded_plans', filename) 

        plandata = json.loads(plandata)
        plan_items = plandata['items']
                      
        jd=json.dumps(plan_items, indent =2)

        out_file = open(path, "w") 
        out_file.write(jd) 
        out_file.close()

        print("Stored as: " + path)
            

    except requests.exceptions.HTTPError as e:
        print("Failed! plandata: " + plandata)
        exit()

   
elif choice in no:
    print("OK. Will exit then.")
    exit()


else:
    sys.stdout.write("Please respond with 'y'(es) or 'n'(o)")


exit()
