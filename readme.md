# Introduction

### General info on API usage
Additionally the a .env file is required where login information and URLs are stored. Use the .envexample file to create your own. 

Swecris has an open API key (can be found at: https://www.vr.se/english/swecris/swecris-api.html). 
For DMPonline administrators

### Create a single DMP in DMPonline using data from SweCris

The script `swecris_to_dmponline.py` fetches data from SweCris for a given project/financed activity and genereates a basic DMP that can be uploaded to DMPonline. 

The script takes the following as input:
* ..
* ..
* ..

Thes script reorders data from SweCris into a json file compatible with the RDA JSONschema 1.0 (see: ). The schema consists of the following sections:  
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


