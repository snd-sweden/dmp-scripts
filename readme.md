# Introduction
Full instructions on how to query the DMPonline API can be found at: https://github.com/DMPRoadmap/roadmap/wiki/API-documentation

### Requirements

[Python & pip](https://www.python.org/downloads/)  

### Install required python modules

`pip install -r requirements.txt`

### General info on API usage
In order to use these scripts a `.env` file is required where login information and URLs are stored. Use the .envexample file to create your own. 

Swecris has an open API key (can be found at: https://www.vr.se/english/swecris/swecris-api.html). 

DMPonline administrators need to state their login and API-key in the `.env` file in order to be able to authenticate with the DMPonline API.

### Query DMPonline about existing templates
The script `dmponline_templates.py` queries DMPonline about existing templates. Useful to identify specific templateids.

At the moment the script performs a simple query to DMPonline using login info from the `.env` file and downloads all accessible templates, prints them and stores them as a single JSON in a subfolder, `Templates`. 

Currently, the script only returns the first page (up to 100 entries).

### Download a specific DMP from DMPonline 
The script `dmponline2_file_v0.py`and `dmponline2_file_v0.py`both lookup and donwload a specified DMP and stores it as a JSON. The `v0`-script accesses the DMPonline API V0 while the `v1`-script aceesses the API V1. For details see: https://github.com/DMPRoadmap/roadmap/wiki/API-documentation

The main difference is that API V0 relays all the information stored in the DMP, while API V1 provides the metadata on the DMP in a RDA v1.0 schema compliant format. 

Downloaded plans are stored in a subfolder, `Downloaded_plans`.

Both scripts require input in the form of the ID of the specific plan. These are the 6 digits at the end of the DMP-URL (e.g. dmponline.dcc.ac.uk/plans/**123456**) 

Example call:  `./python3 dmponline2_file_v0.py -i 123456`

### Create a single DMP in DMPonline using data from SweCris
The script `swecris_to_dmponline.py` fetches data from SweCris for a given project/financed activity and genereates a basic DMP that can be uploaded to DMPonline. 

The script takes the following as input:
* Grantid, e.g. -i 2023-xxxxx (required, this is the grant id from the funder)
* Funder e.g. -f vr (required, necessary to locate data in SweCris)
* Language e.g. -l eng (optional, default is eng) 
* Name e.g. -n "Albert Einstein" (required, used to create the user)
* Email e.g. -e aeinstein@example.com (required, used to create the user)
* Orcid e.g. -0 0009-1234-5678-1234 (optional, currently disabled)
* Templatenumber e.g -t 439 (required, this can be found by running a template check with `dmponline_templates.py`)

Example call:  `./python3 swecris_to_dmponline.py -i 2012-12345 -f vr -n "Albert Einstein" -e aeinstein@example.com -t 439`

The script first tries to access the SweCris database to find the correct project. If found, it prompts the user for whether to create a DMP.

If yes then:

The script reorders data from SweCris into a json file compatible with the RDA JSONschema 1.0 (see: https://github.com/RDA-DMP-Common/RDA-DMP-Common-Standard). 
<details>
  <summary>The schema consists of the following sections (click me):</summary>
  
| Syntax | Description |  
| --------------- | ----------- |    
|`"dmp:"`|          main container/dictionary where additional containers are added. subheadings include:|  
|`"schema:"`|       cannot be changed. default is 1.0.|   
|`"title:"`|        **Fetched from SweCris.** This is the title of the research project.|   
|`"description:"`|  **Fetched from SweCris.** This is the abstract for the research project.|   
|`"language:"` |    default eng. Can be changed? |  
|`"created:"` |     added by DMPonline. Anything written here will be overwritten with a timestamp from the system. | 
|`"modified:"`|     added by DMPonline. Anything written here will be overwritten with a timestamp from the system. | 
| `"ethical_issues_exist:"`|    default unknown| 
|`"dmp_id:"`|       container created by DMPonline. subheadings include:|  
|<ul>`"type:"`</ul>|            default url|   
|<ul>`"identifier:"`</ul>|      this is the direct url to the plan. e.g. "https://dmponline.dcc.ac.uk/api/v1/plans/123456". The beginning of the url can be replaced with an institutional domain adress (e.g. https://dmp.kth.se/) |  
|`"contact:"`|       container for the contact/owner of the plan. subheadings include:|  
|<ul>`"name:"`</ul>|            Fetched from script params. But DMPonline will change this if the email exists in its system|   
|<ul>`"mbox:"`</ul>|            e-mail address from script params. This is checked in DMPonline internally to fetch additional data |
|<ul>`"affiliation:"`</ul>|     container with two subheadings: |   
|<ul>`"name:"`</ul>|            Institutional name, fetched from .env      |
|<ul>`"abbreviation:"`</ul>|    Institutional abbreviation. Fetched from .env |
|<ul>`"contact_id:"`</ul>|      optional container, created from script params if included. Autocreated by DMPonline if user and ORCID exists. Two subheadings: |   
|<ul>`"type:"`</ul>|            default orcid|
|<ul>`"identifier:"`</ul>|      orcid. id-format: https://orcid.org/0000-0001-2345-6789|
|`"contributor:"`|  container for the contributors to the plan, several can be added. DMPonline adds contact as an additional contributor here even if not included in SweCris. Subheadings include:|  
|<ul>`"name:"`</ul>|            **Fetched from SweCris.**|   
|<ul>`"mbox:"`</ul>|            E-mail. Not in Swecris and thus not included in data sent to DMPonline, but this is sometimes added by DMPonline if user exists.|
|<ul>`"role:"`</ul>|            default other. However DMPonline sometimes changes this to CRediT roles (e.g. http://credit.niso.org/contributor-roles//data-curation).  Unclear why and based on what. |
|<ul>`"affiliation:"`</ul>|     container with two subheadings: |   
|<ul>`"name:"`</ul>|            Institutional name, fetched from .env      |
|<ul>`"abbreviation:"`</ul>|    Institutional abbreviation. Fetched from .env |
|<ul>`"contributor_id:"`</ul>|     optional container, created from **SweCris data** if included. Autocreated by DMPonline if user and ORCID exists. Problematic if user exists without orcid in DMPonline but orcid exists in SweCris. Two subheadings: |   
|<ul>`"type:"`</ul>|            default orcid|
|<ul>`"identifier:"`</ul>|      orcid. id-format: https://orcid.org/0000-0001-2345-6789|
|`"project:"`|      container for the project. Subheadings include:|  
|<ul>`"title:"`</ul>|           **Fetched from SweCris.** Needs to be identical to the DMP title.|   
|<ul>`"description:"`</ul>|     **Fetched from SweCris.** Needs to be identical to the DMP description.|
|<ul>`"start:"`</ul>|           **Fetched from SweCris.**|
|<ul>`"end:"`</ul>|             **Fetched from SweCris.**|   
|<ul>`"funding:"`</ul>|         Container for funder information.|
|<ul>`"name:"`</ul>|            Funder name, from script params|
|<ul>`"funder_id:"`</ul>|       container with 2 subheadings. Created based on script params|   
|<ul>`"type:"`</ul>|            default ror|
|<ul>`"identifier:"`</ul>|      ror. id-format: https://ror.org/03zttfo63 **PROBLEM:** DMPonline changes correct rors to dummy ones (https://ror.org/123abc45y)|
|<ul>`"grant_id:"`</ul>|        container with two subheadings|
|<ul>`"identifier:"`</ul>|      grant number, genereated from script params. **NOTE:** this can only be used once and needs to be unique otherwise ignored by DMPonline.|
|<ul>`"type:"`</ul>|            default other|
|<ul>`"funding_status:"`</ul>|  default granted **PROBLEM:** DMPonline changes to planned|
|<ul>`"dmproadmap_funded_affiliations:"`</ul>|  container added by DMPonline. Two subheadings|
|<ul>`"name:"`</ul>|            Institutional name.|
|<ul>`"abbreviation:"`</ul>|    Institutional abbreviation.|
|`"dataset:"`|      container for an empty dataset. Subheadings include:|  
|<ul>`"type:"`</ul>|            default dataset|
|<ul>`"title:"`</ul>|           default Generic dataset|   
|<ul>`"description:"`</ul>|     default No individual datasets have been defined for this DMP.|
|`"extension:"`|      container for template definition. Subheadings include:|  
|<ul>`"dmproadmap:"`</ul>|      subcontainer|
|<ul>`"template:"`</ul>|        subcontainer|   
|<ul>`"id:"`</ul>|              Fetched from script params. id number for the template.|
|<ul>`"title:"`</ul>|           default "". Gets filled in by DMPonline with correct title based on id.|

</details>  


<br/>

The complete JSON is shown and the script prompts whether to upload to DMPonline.

If yes then the script uploads the plan to dmponline.
The postdata is printed in full and also stored as a json file combining grantid and name (from script parameters) in a subfolder `Uploaded_plans`. The link to the dmp is printed and then the script exits. 
