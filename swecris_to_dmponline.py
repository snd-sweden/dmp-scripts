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

# Simple cript for creating new DMP:s (projects) in DMP Online using basic data
# from SweCRIS. Work in progress, use as is.
# Example: ./python3 swecris2dmponlineV2.py -i 2021-04241 -f vr -n "Albert Einstein" -e aeinstein@example.com -o 0000-0001-1234-567x -t 439
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
affiliation = os.getenv("DEFAULT_AFF")
affiliation_abbrev = os.getenv("DEFAULT_AFF_ABBREV")

# Input params
parser = ArgumentParser(description="Create new DMP using data from Swecris.", formatter_class=ArgumentDefaultsHelpFormatter,)
parser.add_argument("-v", "--verbose", action="store_true", help="increase verbosity")
parser.add_argument("-i", "--grantid", default="", help="Grant ID, i.e. 2023-012345", required=True)
parser.add_argument("-f", "--funder", default="vr", help="Funder acronym. Allowed values: vr, energimyndigheten, "
                                                         "formas, forte, rj, rymdstyrelsen, vinnova", required=True,)
parser.add_argument("-l", "--lang", default="eng", help="Language used in DMP, possible values: swe, eng", required=False,)
parser.add_argument("-n", "--name", default="", help="Full name of contact person for DMP", required=True,)
parser.add_argument("-e", "--email", default="", help="Contact person e-mail", required=True)
parser.add_argument("-o", "--orcid", default="", help="Contact person ORCID (if available)", required=False,)
parser.add_argument("-t", "--template", default="", help="DMP Online template ID", required=True)
args = parser.parse_args()

# Create Swecris ID and look up corresponding project in Swecris API
swecrisid = ""
funder_ror = ""
grantid = args.grantid
funder = args.funder
lang = args.lang
contact_name = args.name
contact_email = args.email
contact_orcid = args.orcid
templateid = args.template

# Funder specific params
if funder == "vr":
    swecrisid = grantid + "_VR"
    funder_ror = "https://ror.org/03zttf063"
elif funder == "energimyndigheten":
    swecrisid = grantid + "_Energi"
    funder_ror = "https://ror.org/0359z7n90"
elif funder == "formas":
    swecrisid = grantid + "_Formas"
    funder_ror = "https://ror.org/03pjs1y45"
elif funder == "forte":
    swecrisid = grantid + "_Forte"
    funder_ror = "https://ror.org/02d290r06"
elif funder == "rj":
    swecrisid = grantid + "_RJ"
    funder_ror = "https://ror.org/02jkbm893"
elif funder == "rymdstyrelsen":
    swecrisid = grantid + "_SNSB"
    funder_ror = "https://ror.org/04t512h04"
elif funder == "vinnova":
    swecrisid = grantid + "_Vinnova"
    funder_ror = "https://ror.org/01kd5m353"
else:
    print("Invalid Funder. Allowed values are: vr, energimyndigheten, formas, forte, rj, rymdstyrelsen, "
          "vinnova. Exiting.")
    exit()

# Fetch data from SweCRIS
swecris_url = os.getenv("SWECRIS_URL") + swecrisid
swecris_headers = {
    "Accept": "application/json",
    "Authorization": "Bearer " + os.getenv("SWECRIS_API_KEY"),
}
try:
    swecrisdata = requests.get(url=swecris_url, headers=swecris_headers).text
    if "Internal server error" in swecrisdata:
        print("No data for id: " + swecrisid + " was found in SweCRIS!")
        exit()
    swecrisdata = json.loads(swecrisdata)
    project_name = ""
    project_desc = ""
    project_title = swecrisdata["projectTitleEn"]
    if lang == "swe":
        project_title = swecrisdata["projectTitleSv"]
    project_desc = swecrisdata["projectAbstractEn"]
    if lang == "swe":
        project_desc = swecrisdata["projectAbstractSv"]
    if project_desc == "":
        project_desc = "(missing)"
        if lang == "swe":
            project_desc = "(saknas)"
    project_start = swecrisdata["projectStartDate"]  # replaced fundingStartDate
    project_end = swecrisdata["projectEndDate"]  # replaced fundingEndDate

    funder_name = swecrisdata["fundingOrganisationNameEn"]
    if lang == "swe":
        funder_name = swecrisdata["fundingOrganisationNameSv"]

    if lang == "swe":
        print(
            'Hittade information om projektet "'
            + project_title
            + '" i Swecris API! Ska vi skapa en DHP? (j/n)'
        )
    else:
        print(
            'Got data for project "'
            + project_title
            + '" from Swecris API! Create DMP? (y/n)'
        )

    yes = {"yes", "y", "ye", "j", "ja", ""}
    no = {"no", "n", "nej"}
    choice = input().lower()

    if choice in yes:
        # Create maDMP
        dmp = {}
        madmp_schema = (
            "https://github.com/RDA-DMP-Common/RDA-DMP-Common-Standard/tree/master/examples/JSON/JSON"
            "-schema/1.0"
        )  # will be changed by DMPonline nonetheless.

        d = dict()

        # Basic data
        d["schema"] = madmp_schema
        created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        d["title"] = project_title  # actually project tile
        d["description"] = project_desc  # actually project description
        d["language"] = lang
        d["created"] = created_at
        d["ethical_issues_exist"] = "unknown"

        # Contact person
        # This is handled by the script params. Please note that if the user exists in DMPonline, DMPonline will add information to the system.
        # At the moment Orcid is problematic and thus commented out.
        # Contact
        cnt = {
            "name": contact_name,
            "mbox": contact_email,
            "affiliation": {"name": affiliation, "abbreviation": affiliation_abbrev},
        }
        # if contact_orcid:
        #    cnt["contact_id"] = {"identifier": "https://orcid.org/" + contact_orcid, "type": "orcid"}
        d["contact"] = cnt

        # Contributors
        cs = []
        for persons in swecrisdata["peopleList"]:
            ct = {}
            orcid = ""
            ct["name"] = persons['fullName']
            # Role
            ct["role"] = ["other"]  # uneditable and not considered, but can be included
            if lang == "swe":
                ct["role"] = ["other"]
            ct["affiliation"] = {
                "name": affiliation,
                "abbreviation": affiliation_abbrev,
            }
            # Orcid - this is currently to problematic to use
            # if "orcId" in persons:
            #    orcid = "https://orcid.org/" + persons['orcId']
            # ct["contributor_id"] = {"identifier": orcid, "type": "orcid"}   #MASSIVE HEADACHE keeps changing to some default orcid.
            cs.append(ct)

        d["contributor"] = cs
        

        # Project info
        ps = []
        pt = {
            "title": project_title,
            "description": project_desc,
            "start": project_start,
            "end": project_end,
        }
        # Funder
        pfl = []
        pfn = {
            "name": funder,
            "funder_id": {"type": "ror", "identifier": funder_ror}, # keeps getting changed to "https://ror.org/123abc45y" cannot figure out why.
            "grant_id": {"identifier": swecrisid, "type": "other"},
            "funding_status": "granted",
        }  # Please note that grantIDs need to be unique. if they already exist then the field will become blank.
        pfl.append(pfn)
        pt["funding"] = pfl
        ps.append(pt)
        d["project"] = ps

        # Dataset (dummy, standard compliance)
        dsts_empty = []
        dset_empty = {
            "type": "dataset",
            "title": "Generic dataset",
            "description": "No individual datasets have been defined for this DMP.",
        }
        dsts_empty.append(dset_empty)
        d["dataset"] = dsts_empty

        # DMP template
        extension = [
            {
                "dmproadmap": {
                    "template": {
                        "id": templateid,
                        "title": "",
                    }
                }
            }
        ]

        d["extension"] = extension

        # Create (and print) maDMP record
        dmp["dmp"] = d
        jsondmp = {"total_items": 1, "items": [dmp]}
        print(json.dumps(jsondmp, indent=2))

        

    # Go ahead and create DMP in DMPOnline from here...
    print("Should I create a new DMP using these data in DMP Online? (y/n)")
    yes = {"yes", "y", "ye", "j", "ja", ""}
    no = {"no", "n", "nej"}
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

        # Create DMP
        try:

            dmp_postplan_url = os.getenv("DMPONLINE_API_URL") + "plans"
            postplan_headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Server-Agent": "Your Application Name",
                "Authorization": "Bearer " + dmp_auth_bearer,
            }
            
            postdata = requests.post(
                url=dmp_postplan_url, json=jsondmp, headers=postplan_headers
            ).text
            print(postdata) # contains API url for the created plan
            
            if not os.path.exists('Uploaded_plans'):
                os.makedirs('Uploaded_plans') 
            filename = grantid + contact_name + "dmp.json"
            path = os.path.join('Uploaded_plans', filename)
            out_file = open(path, "w") 
            out_file.write(postdata) 
            out_file.close()
            print("Stored as: " + path)

            # Link to new DMP

            postdata = json.loads(postdata)
            Linktonewplan = postdata['items'][0]['dmp']['dmp_id']['identifier']
            GUIlink = dmp_postplan_url[:-12]+"plans" + Linktonewplan[-7:]
            print("A new plan has been created! You can access it through API: " + Linktonewplan + 
                  "\nor a browser: " + GUIlink)

        except requests.exceptions.HTTPError as e:
            print("Failed! postdata: " + postdata)
            exit()

        # Link to new DMP
        

    elif choice in no:
        print("OK. Will exit then.")
        exit()

    elif choice in no:
        print("OK. Will exit then.")
        exit()
    else:
        sys.stdout.write("Please respond with 'y'(es) or 'n'(o)")


except requests.exceptions.HTTPError as e:
    print("No data for id: " + swecrisid + " was found in SweCRIS!")
    print("\n")
    with open(os.getenv("LOGFILE"), "a") as lf:
        lf.write("No data for id: " + swecrisid + " was found in SweCRIS! Skipping.")
exit()
