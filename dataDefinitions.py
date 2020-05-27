# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 15:23:40 2020

@author: louis


Define the tables and fields to export. 

"""


tableDict = {
            'incident': 'sys_id,number,short_description,description,sys_updated_on',
            'change_request': 'sys_id,number,short_description',
            'sc_req_item': 'sys_id,number,short_description'
            }

