# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 08:59:45 2020

@author: louis

The downloadAttachments function downloads all attachments for the
given instance and table.  Each record with an attachment has all its attachments downloaded
as a zip file, named with the sys_id of the record.  The lastSysId parameter is optional, and it comes
in handy when downloading large amounts of attachments and you get disconnected.

When this is running, for each set of records processed (the limit variable below
fetches 1000 at a time by default, but you can modify it if you're brave), it will print
to the console the lastSysId value.  So, if your download gets cut off, you can resume
basically where you started by calling this function and passing in the lastSysId value.

Note that you MUST have the exportAttachmentsToZip processor in your environment, and that
is included in this repository.


"""

import requests

def downloadAttachments(user, pwd, instance, table, lastSysId='0'):

    limit = 1000
    
    url = 'https://' + instance + '.service-now.com/api/now/attachment?sysparm_query=ORDERBYsys_id^table_name=' + table + '^sys_id>' + lastSysId + '&sysparm_limit=' + str(limit)
    #print(url)
    r = requests.get(url, auth=(user, pwd))
    
    data = r.json()
    attachList = data['result']
    numRecs = len(attachList)
    
    
    while numRecs == limit:
        print("Processing " + str(numRecs) + " records, last sys_id is " + lastSysId + "...")
        lastSysId = attachList[-1]['sys_id'] #get the last sys_id value
    
        #get unique list of incident sys_id values that have attachments
        ticketIdSet = {}
        ticketIdSet = set()
        for i in attachList:
            ticketIdSet.add(i['table_sys_id'])
            
        
        #call the custom processor to get a zip file for each incident ticket
        procUrl = 'https://' + instance + '.service-now.com/exportAttachmentsToZip.do'
        
        for val in ticketIdSet:
            r = requests.get(procUrl + "?sysparm_sys_id=" + val + "&sysparm_table=" + table, auth=(user, pwd))
            with open(val + '.zip', 'wb') as f:
                f.write(r.content)
                
        url = 'https://' + instance + '.service-now.com/api/now/attachment?sysparm_query=ORDERBYsys_id^table_name=' + table + '^sys_id>' + lastSysId + '&sysparm_limit=' + str(limit)
        #print("\n" + url + "\n")
        r = requests.get(url, auth=(user, pwd))
        data = r.json()    
        attachList = data['result']
        numRecs = len(attachList)
        
    #if we're here, we're on the last set of records - process just like we did in the loop
    print("Processing " + str(numRecs) + " records, last sys_id is " + lastSysId + "...")
    
    #get unique list of incident sys_id values that have attachments
    ticketIdSet = {}
    ticketIdSet = set()
    for i in attachList:
        ticketIdSet.add(i['table_sys_id'])
        
    
    #call the custom processor to get a zip file for each incident ticket
    procUrl = 'https://' + instance + '.service-now.com/exportAttachmentsToZip.do'
    
    for val in ticketIdSet:
        r = requests.get(procUrl + "?sysparm_sys_id=" + val + "&sysparm_table=" + table, auth=(user, pwd))
        with open(val + '.zip', 'wb') as f:
            f.write(r.content)