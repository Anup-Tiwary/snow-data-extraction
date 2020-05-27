# Overview

This is a data extraction tool that exports data from ServiceNow.  It was created with a specific use case in mind,
but contains all of the tools needed to get most data out of ServiceNow.

The primary file is dataExport.py.  Inside this file, the code reads in the tables configured in dataDefinitions.py, loops
through each, and downloads the following to CSV files:

    1) the table records
    2) the work notes and comments (from sys_journal_field)
    3) the assignment history (from sys_audit - you may need to increase your SN REST timeout setting for this)
    4) mappings of user names and their sys_ids, and group names and their sys_ids
    5) for the sc_req_item table, all variables and their values will be downloaded
        NOTE: you must have the exportItemVariables processor for this, which is included in this repository
    6) for some tables, approval history from sysapproval_approver will be downloaded
    7) all attachments
        NOTE:  you must have the exportAttachmentsToZip processor for this, which is included in this repository
        
# Getting started

To use this for yourself, do the following:

    a) Modify exportConfig.cfg to point to your instance with an admin user/pass
    b) Modify the dataDefinitions.py file's dataDict to have the tables/fields you want to export
    c) Run dataExport.py
