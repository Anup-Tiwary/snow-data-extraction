# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 08:59:45 2020

@author: louis

The function defined below gets variables and values for all
sc_req_item tickets in ServiceNow.  

In order for this to work, you
MUST have the exportItemVariables processor in your instance, and that is
included in this repository.

"""

import requests


#for a given instance, this downloads all variable questions and
#answers for each sc_req_item ticket
def downloadVariableFile(user, pwd, instance):

    sysIdVals = ""
    url = 'https://' + instance + '.service-now.com/api/now/table/sc_req_item?sysparm_fields=sys_id&sysparm_orderby=sys_id&sysparm_limit=50000'
    r = requests.get(url, auth=(user, pwd))
    data = r.json()
    
    itemList = data['result']
    
    #iterate through the list, get the comma-separated string, and write it to a CSV file
    with open('variables.csv', 'wb') as f:
        for index, i in enumerate(itemList):
            sysIdVals += i['sys_id'] + ","

            if (index % 100 == 0 and index != 0) or ((index+1) == len(itemList)):
                procUrl = 'https://' + instance + '.service-now.com/exportItemVariables.do?sysparm_sysIdList=' + sysIdVals
                r = requests.get(procUrl, auth=(user, pwd))
                f.write(r.content)
                sysIdVals = ""
            
            if index % 1000 == 0 and index != 0:
                print("Processing item " + str(index) + " of " + str(len(itemList)) + "...")
