# -*- coding: utf-8 -*-
"""
Created on Fri May  1 15:15:48 2020

@author: louis

This is the code that gets the data from ServiceNow and writes it to 
a CSV file.  The limit variable below can be modified to fetch more records at a time,
but in my testing, 1000 at a time seemed to work best to avoid strange errors.  It is called from dataExport.py.


"""
import requests

def fetchData(user, pwd, instance, module, table, orderBy, query, fields, fileName):
    print("Exporting " + table + " records...")
    
    fieldOrderList = fields.split(",") #needed to get fields in correct order
    limit = 1000
    lastSysId = '0'
    url = 'https://' + instance + '.service-now.com/api/now/table/' + table + '?sysparm_fields=' + fields + '&sysparm_exclude_reference_link=true&sysparm_display_value=true&sysparm_limit=' + str(limit) + '&sysparm_query=ORDERBY'+ orderBy + '^' + orderBy + '>' + lastSysId + '^' + query
    #print(url)
 
    #get the first batch of records
    r = requests.get(url, auth=(user, pwd))
    #print(r.content)
    data = r.json()    
    recordList = data['result']
    numRecs = len(recordList)
    
    if numRecs == 0:
        with open(module + ' - ' + table + '.csv', 'w', encoding='utf-8') as f:
            f.write("No records found")
        return
    
    #this modifies the order of the fields to match what is in dataDefinitions.py 
    for y in fieldOrderList:
        recordList[0][y] = recordList[0].pop(y)
    
    #get label value of column headings
    colLabelList = []
    for key in recordList[0].keys():
        
        if '.' in key:            
            url = 'https://' + instance + '.service-now.com/api/now/table/sys_dictionary?sysparm_fields=element,column_label&sysparm_query=name=' + table + '^ORname=task^element=' + key.split('.')[0]
        else:
            url = 'https://' + instance + '.service-now.com/api/now/table/sys_dictionary?sysparm_fields=element,column_label&sysparm_query=name=' + table + '^ORname=task^element=' + key
        
        #print("\n" + url + "\n")
        r = requests.get(url, auth=(user, pwd))
        data = r.json()
        try:
            if '.' in key:
                colLabelList.append(data['result'][0]['column_label'] + '.' + key.split('.')[1])
            else:
                colLabelList.append(data['result'][0]['column_label'])
        except:
            continue
    headings = ",".join(colLabelList)
    
    #write record values to file
    with open(module + ' - ' + fileName + '.csv', 'w', encoding='utf-8') as f:
        f.write(headings + "\n")
        lastSysId = recordList[-1][orderBy] #get the last value of whatever we are ordering by
        while numRecs == limit:
            print("Processing " + str(numRecs) + " records...")
            for rec in recordList:
                
                #convert all values to strings and strip quotes, newlines, carriage returns
                for key in rec:
                    rec[key] = '"' + str(rec[key]).replace("\"", "'").replace("\n", "").replace("\r", "") + '"'
                
                #this modifies the order of the fields to match what is in dataDefinitions.py           
                for x in fieldOrderList:
                    rec[x] = rec.pop(x)
                    
                #write to file
                f.write(",".join(rec.values()) + "\n")
        
            url = 'https://' + instance + '.service-now.com/api/now/table/' + table + '?sysparm_fields=' + fields + '&sysparm_exclude_reference_link=true&sysparm_display_value=true&sysparm_limit=' + str(limit) + '&sysparm_query=ORDERBY'+ orderBy + '^' + orderBy + '>' + lastSysId + '^' + query
            #print("\n" + url + "\n")
            r = requests.get(url, auth=(user, pwd))
            data = r.json()    
            recordList = data['result']
            lastSysId = recordList[-1][orderBy] #get the last sys_id value
            numRecs = len(recordList)
            
        #for the last set of records, write to the file
        for rec in recordList:
        
            #convert all values to strings and strip quotes
            for key in rec:
                rec[key] = '"' + str(rec[key]).replace("\"", "'") + '"'
            
            #this modifies the order of the fields to match what is in dataDefinitions.py            
            for x in fieldOrderList:
                rec[x] = rec.pop(x)
            
            #write to file
            f.write(",".join(rec.values()) + "\n")
