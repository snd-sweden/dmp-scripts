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

# Simple cript for creating new DMP:s (projects) in DMP Online (or other maDMP compatible tools), using basic data
# from SweCRIS.
# Todo: lots of things...
# Example: ./python3 swecris2dmp.py -i 2021-04241 -f vr -n "Albert Einstein" -e aeinstein@example.com -o 0000-0001-1234-567x
#
# / urban.andersson@chalmers.se
#

# Settings
load_dotenv()
dmpurl = os.getenv("DMPONLINE_API_URL")
dmpuser = os.getenv("DMPONLINE_USER")
dmppw = os.getenv("DMPONLINE_PW")
dmp_id_prefix = os.getenv("DMP_ID_PREFIX")
logfile = os.getenv("LOGFILE")

# Input params
parser = ArgumentParser(description="Create new DMP using data from Swecris.",
                        formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-v", "--verbose", action="store_true", help="increase verbosity")
parser.add_argument("-i", "--grantid", default="", help="Grant ID, i.e. 2023-012345", required=True)
parser.add_argument("-f", "--funder", default="vr", help="Funder acronym. Allowed values: vr, energimyndigheten, "
                                                         "formas, forte, rj, rymdstyrelsen, vinnova",
                    required=True)
parser.add_argument("-l", "--lang", default="eng", help="Language used in DMP, possible values: swe, eng",
                    required=False)
parser.add_argument("-n", "--name", default="", help="Full name of contact person for DMP", required=True)
parser.add_argument("-e", "--email", default="", help="Contact person e-mail", required=True)
parser.add_argument("-o", "--orcid", default="", help="Contact person ORCID (if available)", required=False)
args = parser.parse_args()

# Create Swecris ID and look up corresponding project in Swecris API
swecrisid = ''
funder_ror = ''
grantid = args.grantid
funder = args.funder
lang = args.lang
contact_name = args.name
contact_email = args.email
contact_orcid = args.orcid

# Funder specific params
if funder == 'vr':
    swecrisid = grantid + '_VR'
    funder_ror = 'https://ror.org/03zttf063'
elif funder == 'energimyndigheten':
    swecrisid = grantid + '_Energi'
    funder_ror = 'https://ror.org/0359z7n90'
elif funder == 'formas':
    swecrisid = grantid + '_Formas'
    funder_ror = 'https://ror.org/03pjs1y45'
elif funder == 'forte':
    swecrisid = grantid + '_Forte'
    funder_ror = 'https://ror.org/02d290r06'
elif funder == 'rj':
    swecrisid = grantid + '_RJ'
    funder_ror = 'https://ror.org/02jkbm893'
elif funder == 'rymdstyrelsen':
    swecrisid = grantid + '_SNSB'
    funder_ror = 'https://ror.org/04t512h04'
elif funder == 'vinnova':
    swecrisid = grantid + '_Vinnova'
    funder_ror = 'https://ror.org/01kd5m353'
else:
    print('Invalid Funder. Allowed values are: vr, energimyndigheten, formas, forte, rj, rymdstyrelsen, '
          'vinnova. Exiting.')
    exit()

# Fetch data from SweCRIS
swecris_url = os.getenv('SWECRIS_URL') + swecrisid
swecris_headers = {'Accept': 'application/json',
                   'Authorization': 'Bearer ' + os.getenv("SWECRIS_API_KEY")}
try:
    swecrisdata = requests.get(url=swecris_url, headers=swecris_headers).text
    if 'Internal server error' in swecrisdata:
        print('No data for id: ' + swecrisid + ' was found in SweCRIS!')
        exit()
    swecrisdata = json.loads(swecrisdata)
    project_name = ''
    project_desc = ''
    project_title = swecrisdata['projectTitleEn']
    if lang == 'swe':
        project_title = swecrisdata['projectTitleSv']
    project_desc = swecrisdata['projectAbstractEn']
    if lang == 'swe':
        project_desc = swecrisdata['projectAbstractSv']
    if project_desc == '':
        project_desc = '(missing)'
        if lang == 'swe':
            project_desc = '(saknas)'
    project_start = swecrisdata['fundingStartDate']
    project_end = swecrisdata['fundingEndDate']
    funder_name = swecrisdata['fundingOrganisationNameEn']
    dmp_desc = 'This data management plan has been automatically initiated, using metadata from Swecris.'
    if lang == 'swe':
        dmp_desc = 'Denna datahanteringsplan har initierats automatiskt med hjälp av metadata från Swecris.'
    if lang == 'swe':
        funder_name = swecrisdata['fundingOrganisationNameSv']
    if lang == 'swe':
        print('Hittade information om projektet "' + project_title + '" i Swecris API! Ska vi skapa en DHP? (j/n)')
    else:
        print('Got data for project "' + project_title + '" from Swecris API! Create DMP? (y/n)')
    yes = {'yes', 'y', 'ye', 'j', 'ja', ''}
    no = {'no', 'n', 'nej'}
    choice = input().lower()
    if choice in yes:
        # Create maDMP
        dmp = {}
        madmp_schema = "https://github.com/RDA-DMP-Common/RDA-DMP-Common-Standard/tree/master/examples/JSON/JSON" \
                       "-schema/1.1"
        d = dict()

        # Basic data
        d['schema'] = madmp_schema
        created_at = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        d['title'] = project_title
        d['created'] = created_at
        d['dmp_id'] = dmp_id_prefix + ':' + str(uuid.uuid4())
        d['description'] = dmp_desc
        d['language'] = lang
        d['ethical_issues_exist'] = 'unknown'

        # Contributors
        cs = []
        cc = {}
        for persons in swecrisdata['peopleList']:
            ct = {}
            orcid = ''
            ct["name"] = persons['fullName']
            # Orcid
            if 'orcId' in persons:
                orcid = persons['orcId']
                ct["contributor_id"] = {"identifier": orcid, "type": "orcid"}
            # Role
            ct["role"] = persons['roleEn']
            if lang == 'swe':
                ct["role"] = persons['roleSv']
            # Contact person
            # Handle in script params for now
            cs.append(ct)
        d["contributor"] = cs

        # Contact
        cnt = {'name': contact_name, 'mbox': contact_email}
        if contact_orcid:
            cnt['contact_id'] = {"identifier": contact_orcid, "type": "orcid"}
        d['contact'] = cnt

        # Project info
        ps = []
        pt = {"title": project_title, "description": project_desc, "start": project_start, "end": project_end}
        # Funder
        pfl = []
        pfn = {'funder_name': funder_name, 'funder_id': {'identifier': funder_ror, 'type': 'ror'},
               'grant_id': {'identifier': grantid, 'type': 'other'}}
        pfl.append(pfn)
        pt['funding'] = pfl
        ps.append(pt)
        d['project'] = ps

        # Dataset (dummy, standard compliance)
        dsts_empty = []
        dset_empty = {"type": 'dataset', "title": 'Generic dataset',
                      "description": 'No individual datasets have been defined for this DMP.',
                      "dataset_id": {'identifier': str(uuid.uuid4()), 'type': 'other'}, "sensitive_data": 'unknown',
                      "personal_data": 'unknown'}
        dsts_empty.append(dset_empty)
        d['dataset'] = dsts_empty

        # Create (and print) maDMP record
        dmp['dmp'] = d
        print(json.dumps(dmp, indent=4))

        # Go ahead and create DMP in DMPOnline from here...?

    elif choice in no:
        print('OK. Will exit then.')
        exit()
    else:
        sys.stdout.write("Please respond with 'y'(es) or 'n'(o)")
except requests.exceptions.HTTPError as e:
    print('No data for id: ' + swecrisid + ' was found in SweCRIS!')
    print('\n')
    with open(os.getenv("LOGFILE"), 'a') as lf:
        lf.write('No data for id: ' + swecrisid + ' was found in SweCRIS! Skipping.')
exit()
