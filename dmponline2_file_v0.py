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

# Simple script for dowloading DMP:s from DMP Online using the API v.0 (which does not comply with the RDA json scheme).
# Example: ./python3 dmponline2file.py -i 135516
#
# / matves29@kth.se
#

# Settings
load_dotenv()
dmpurl = os.getenv("DMPONLINE_API_URL_V0")
dmpuser = os.getenv("DMPONLINE_USER")
dmppw = os.getenv("DMPONLINE_PW")
dmp_id_prefix = os.getenv("DMP_ID_PREFIX")
logfile = os.getenv("LOGFILE")
dmpAPIkey = os.getenv("DMPONLINE_AUTH_CODE")

# Input params
parser = ArgumentParser(
    description="Script for downloading a specific DMP from the DMPonline API.",
    formatter_class=ArgumentDefaultsHelpFormatter,
)
parser.add_argument("-v", "--verbose", action="store_true", help="increase verbosity")
parser.add_argument("-i", "--planid", default="", help="DMP online ID", required=True)
args = parser.parse_args()

dmpid = args.planid


# Go ahead and create dowload from DMPOnline from here...
print(
    "Should I download a plan through the v0 API and save it as a JSON? (y/n)"
)
yes = {"yes", "y", "ye", "j", "ja", ""}
no = {"no", "n", "nej"}
choice = input().lower()
if choice in yes:
    # Get the plan
    
    plan_headers = {
    'Authorization': 'Token token='+ dmpAPIkey,
    'Content-Type': 'application/json',
    }

    plan_params = {
    'plan': dmpid,
    }
    dmp_plan_url = os.getenv("DMPONLINE_API_URL_V0") + "plans?plan="+dmpid

    

    try:
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
        filename = dmpid + "_API_V0_dmp.json"
        path = os.path.join('Downloaded_plans', filename) 
 
        out_file = open(path, "w") 
        out_file.write(plandata) 
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
