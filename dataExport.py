# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 10:33:33 2020

@author: louis

This is the primary script for this data extractor tool.  In each loop in the code below,
the dataDict (from dataDefinitions.py) is looped through, and the script downloads
the following items to separate CSV files for each table:
    
    1) the table records
    2) the work notes and comments (from sys_journal_field)
    3) the assignment history (from sys_audit - you may need to increase your SN REST timeout setting for this)
    4) mappings of user names and their sys_ids, and group names and their sys_ids
    5) for the sc_req_item table, all variables and their values will be downloaded
        NOTE: you must have the exportItemVariables processor for this, which is included in this repository
    6) for some tables, approval history from sysapproval_approver will be downloaded
    7) all attachments
        NOTE:  you must have the exportAttachmentsToZip processor for this, which is included in this repository


Here is how it works:
    
    a) Modify exportConfig.cfg to point to your instance with an admin user/pass
    b) Modify the dataDefinitions.py file's dataDict to have the tables/fields you want to export
    c) Run this script

"""

import configparser
import os
import sys
import attachmentExport
import variableExport
import dataDefinitions as data
import fetchData as fetch
import traceback

try:

    #read in values from config file
    Config = configparser.ConfigParser()
    Config.read("exportConfig.cfg")
    user = Config.get('main', 'user')
    pwd = Config.get('main', 'pwd')
    env = Config.get('main', 'environment')
    
    
    #create output folder with name of environment
    os.chdir("C:\\")
    try:
        os.mkdir(env)
        print("\nDirectory " , env ,  " created ")     
    except FileExistsError:
        pass
    
    os.chdir(env)
    
    
    #loop through each table and begin exporting the data
    for key in data.tableDict:
        try:
            os.mkdir(key)
            print("\nDirectory ", key, " created ")
        except FileExistsError:
            pass
        
        os.chdir(key)
        
        #export table records to csv
        fetch.fetchData(user, pwd, env, key, key, 'sys_id', '', data.tableDict[key], key + ' records')
            
        #export work notes and comments for this table to csv
        fetch.fetchData(user, pwd, env, key, 'sys_journal_field', 'element_id', 'name=' + key + '^ORname=task', 'element_id,element,value,sys_created_by,sys_created_on', 'comments and work notes')        
            
        #export assignment history for this table to csv
        fetch.fetchData(user, pwd, env, key, 'sys_audit', 'documentkey', 'tablename=' + key + '^fieldname=assignment_group^ORfieldname=assigned_to', 'documentkey,sys_created_on,user,fieldname,oldvalue,newvalue', 'assignment history')
        
        #export user mapping of sys_ids to user names
        fetch.fetchData(user, pwd, env, key, 'sys_user', 'sys_id', '', 'sys_id,user_name', 'user name to ID mapping')        
        
        #export group mapping of sys_ids to user names
        fetch.fetchData(user, pwd, env, key, 'sys_user_group', 'sys_id', '', 'sys_id,name', 'group name to ID mapping')
            
        #if requested items, export variable values
        if key == "sc_req_item":
            print("Exporting requested item variables...")
            variableExport.downloadVariableFile(user, pwd, env)

        
        #if table is one that gets approvals, download approver history
        if key in ['change_request', 'idea', 'sc_req_item']:
            fetch.fetchData(user, pwd, env, key, 'sysapproval_approver', 'sys_id', 'source_table=' + key, 'sysapproval.sys_id,approval_column,approval_journal_column,approval_source,approver,comments,document_id,due_date,expected_start,group,iteration,order,process_step,source_table,state,state_binding,sysapproval,sys_created_by,sys_created_on,sys_id,sys_mod_count,sys_updated_by,sys_updated_on,wf_activity', 'approval history')
        
        #export attachments
        print("Exporting " + key + " attachments...")
        try:
            os.mkdir('attachments')
        except FileExistsError:
            pass
        
        os.chdir('attachments')
        attachmentExport.downloadAttachments(user, pwd, env, key)
        
        os.chdir('../..')
        
    os.chdir('..')


except Exception:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    traceback.print_exc()