from flask import Blueprint, jsonify
import mysql.connector
import os
import re
import ast
from datetime import datetime
from pathlib import Path

def complete_flag(dn):
    
  conn = get_db_connection()
  cursor = conn.cursor()
  query = """SELECT `complete` FROM attachment_table WHERE `DN#` = %s;""" 
  cursor.execute(query, (dn,))
  results = cursor.fetchone()
  if results:
    results = results[0]
  cursor.close()
  conn.close()
  
  return results

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # no password
        database='menarini'
    )
    
def get_all_emailId():
  conn = get_db_connection()
  cursor = conn.cursor()
  
  cursor.execute("SELECT `email_id`, `DN#` FROM email_check")  # adjust column/table name as needed
  results = cursor.fetchall()
  
  cursor.close()
  conn.close()
  
  email_dn_check = {}
  for row in results:
      email_dn_check[row[0]] = row[1]
  return email_dn_check

def get_email_data_with_role(role,email):
  conn = get_db_connection()
  cursor = conn.cursor()
  
  total = []
  results = []
  if role == 1:    
    cursor.execute("SELECT `email_id`,`DN#`,`subject`,`body`,`attachments`,`sender`,`date` FROM email_check")
    results = cursor.fetchall()
  else:
    cursor.execute("SELECT `email_id`,`DN#`,`subject`,`body`,`attachments`,`sender`,`date` FROM email_check WHERE admin_email = %s", (email,))
    results = cursor.fetchall()
  if results:
    for result in results:
      if result:
        email_id = result[0]
        dn = result[1]
        subject = result[2]
        body = result[3]
        raw_attachments = result[4]  # e.g., your weird character list
        joined = ''.join(raw_attachments)  # Join into one string
        print(joined)
        attachments_list = ast.literal_eval(joined)  # Parse as actual list
        attachments = [os.path.basename(a) for a in attachments_list]
        raw_sender = result[5]
        match = re.search(r'<(.+?)>', raw_sender)
        sender = match.group(1) if match else raw_sender
        date = result[6]
        excerpt = body[:30] + '...' if len(body) > 30 else body
        if dn:
          entry =  {"id":email_id,"subject":subject,"sender":sender,"body":body,"attachments":attachments, "date":date,"excerpt":excerpt, "status":complete_flag(dn)}
          total.append(entry)
  return total

def get_all_email(email):
  conn = get_db_connection()
  cursor = conn.cursor()
  cursor.execute("SELECT `admin_email` FROM user WHERE email = %s", (email,))
  emails = cursor.fetchone()
  admin_email = emails[0]
  cursor.execute("SELECT `role` FROM admin_table WHERE email = %s", (admin_email,))
  result = cursor.fetchone()
  if result:
    if result[0] == 1 or result[0] == '1':
      result = get_email_data_with_role(1,email)
    else:
      result = get_email_data_with_role(2,email)
  
  return result
  

def get_gmail_password(email):
  conn = get_db_connection()
  cursor = conn.cursor()
  
  cursor.execute("SELECT `gmail_password` FROM user WHERE `email` = %s",(email,))  # adjust column/table name as needed
  result = cursor.fetchone()[0]
  
  cursor.close()
  conn.close()
  
  return result

def get_dn_from_emailID(emailID):
  conn = get_db_connection()
  cursor = conn.cursor()
  query = """SELECT `DN#` FROM email_check WHERE `email_id` = %s;""" 
  cursor.execute(query, (emailID,))
  results = cursor.fetchone()[0]
  
  cursor.close()
  conn.close()
  
  return results

def get_attachment_list_from_dn(dn):

  conn = get_db_connection()
  cursor = conn.cursor()
  query = """SELECT `DN`, `INV`, `Bill of Lading`, `Air Waybill`, `COA` FROM attachment_table WHERE `DN#` = %s;"""
  cursor.execute(query, (dn,))
  dn,inv,bill_of_lading,air_waybill,coa = cursor.fetchone()
  
  cursor.close()
  conn.close()
  return dn,inv,bill_of_lading,air_waybill,coa

def get_attachment_list_from_email(emailID):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """SELECT `DN`, `INV`, `Bill of Lading`, `Air Waybill`, `COA` FROM email_attachment WHERE `email_id` = %s;"""
    cursor.execute(query, (emailID,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        return result  # returns (dn, inv, bill_of_lading, air_waybill, coa)
    else:
        return None  # or return default values like (0, 0, 0, 0, 0)

def get_email_error(emailID):
  conn = get_db_connection()
  cursor = conn.cursor()
  query = """SELECT `error`, `type` FROM email_error_table WHERE `email_id` = %s;""" 
  cursor.execute(query, (emailID,))
  results = cursor.fetchall()
  json_result = []
  for result in results:
    new_entry = {
      "error":result[0],
      "error_type" : result[1]
    }
    json_result.append(new_entry)
  cursor.close()
  conn.close()
  return json_result


def get_document_error_with_email(emailID):
  conn = get_db_connection()
  cursor = conn.cursor()
  query = """SELECT `message`, `type` FROM error_table WHERE `email_id` = %s;""" 
  cursor.execute(query, (emailID,))
  results = cursor.fetchall()
  json_result = []
  for result in results:
    new_entry = {
      "error":result[0],
      "error_type" : result[1]
    }
    json_result.append(new_entry)
  cursor.close()
  conn.close()
  return json_result

def get_multi_doc(emailID):
  conn = get_db_connection()
  cursor = conn.cursor()
  query = """SELECT `vendor_id`,`doc_list`, `DN#`,`file_name` FROM multi_doc_intervention WHERE `email_id` = %s;""" 
  cursor.execute(query, (emailID,))
  results = cursor.fetchall()
  json_result = []
  for result in results:
    new_entry = {
      "vendor_id":result[0],
      "doc_list" : result[1],
      "DN#" : result[2],
      "file_name" : result[3]
    }
    json_result.append(new_entry)
  cursor.close()
  conn.close()
  return json_result

def get_supplier_from_email(emailID):
  conn = get_db_connection()
  cursor = conn.cursor()
  
  query = """SELECT `DN#` FROM email_check WHERE `email_id` = %s;""" 
  cursor.execute(query, (emailID,))
  results = cursor.fetchone()[0]
  
  query = """SELECT `vendor_id`, `DN#` FROM supplier_name_intervention WHERE `DN#` = %s;""" 
  cursor.execute(query, (results,))
  result = cursor.fetchone()
   
  vendor_id = ""
  dn = ""
  if result:
      vendor_id = result[0] 
      dn = result[1] 
  query = """SELECT `domain`,`vendor_name` FROM supplier_table WHERE `id` = %s;""" 
  cursor.execute(query, (vendor_id,))
  result = cursor.fetchone()
  
  domain = ""
  vendor_name = ""
  if result:
    domain = result[0]
    vendor_name = result[1]
  cursor.close()
  conn.close()
  return domain, vendor_name, dn
  
  
def update_multi_doc(old_doc_list,new_doc_list, emailID, dn):
  conn = get_db_connection()
  cursor = conn.cursor()
  update_query = """UPDATE `multi_doc_intervention` SET `doc_list` = %s WHERE email_id = %s and `doc_list` = %s"""  
  cursor.execute(update_query, (new_doc_list, emailID,old_doc_list ))
  conn.commit()

  doc_types = [doc.strip() for doc in new_doc_list.split("&")]

    # Map shorthand doc types to actual column names
  column_map = {
      "DN": "DN",
      "INV": "INV",
      "COA": "COA",
      "BOL": "`Bill of Lading`",
      "AWB": "`Air Waybill`"
  }

  old_doc_types = [doc.strip() for doc in old_doc_list.split("&")]
  new_doc_types = [doc.strip() for doc in new_doc_list.split("&")]
  for doc_type in old_doc_types:
      column = column_map.get(doc_type)
      if column:
          update_query = f"UPDATE email_attachment SET {column} = %s WHERE `email_id` = %s"
          cursor.execute(update_query, (0, emailID))

# Set only the ones in new_doc_list to 1
  for doc_type in doc_types:
      column = column_map.get(doc_type)
      if column:
          update_query = f"UPDATE email_attachment SET {column} = %s WHERE `email_id` = %s"
          cursor.execute(update_query, (1, emailID))
  conn.commit()
  

  # Set old doc fields to 0
  for doc_type in old_doc_types:
      column = column_map.get(doc_type)
      if column:
          update_query = f"UPDATE attachment_table SET {column} = %s WHERE `DN#` = %s"
          cursor.execute(update_query, (0, dn))

  # Set new doc fields to 1
  for doc_type in new_doc_types:
      column = column_map.get(doc_type)
      if column:
          update_query = f"UPDATE attachment_table SET {column} = %s WHERE `DN#` = %s"
          cursor.execute(update_query, (1, dn))

  conn.commit()
  
  
  cursor.close()
  conn.close()
  return 
  
def update_supplier_name(vendor_domain, old_vendor_name, new_vendor_name,dn):
  conn = get_db_connection()
  cursor = conn.cursor()
  query = """SELECT `id` FROM supplier_table WHERE `domain` = %s AND `vendor_name` = %s"""
  cursor.execute(query, (vendor_domain,new_vendor_name, ))
  result = cursor.fetchone()

  supplier_id = ""
  if result:
    supplier_id = result[0]
  else:
    print("No supplier found for given domain and vendor name.")
    supplier_id = None
      
  
  if supplier_id:
    query = """UPDATE `attachment_table` SET `Supplier ID` = %s WHERE `DN#` = %s"""  
    cursor.execute(query, (supplier_id, dn, ))
    conn.commit()
    
    
    query = """UPDATE `multi_doc_intervention` SET `vendor_id` = %s WHERE `DN#` = %s"""  
    cursor.execute(query, (supplier_id, dn, ))
    conn.commit()
    
    query = """UPDATE `supplier_name_intervention` SET `vendor_id` = %s WHERE `DN#` = %s"""  
    cursor.execute(query, (supplier_id, dn, ))
    conn.commit()
  else:
    update_query = """UPDATE `supplier_table` SET `vendor_name` = %s WHERE `domain` = %s AND `vendor_name` = %s"""  
    cursor.execute(update_query, (new_vendor_name, vendor_domain,old_vendor_name ))
    conn.commit()

  
  cursor.close()
  conn.close()
  return 
  
def get_all_supplier_name(email):
  
  conn = get_db_connection()
  cursor = conn.cursor()
  
  query = """SELECT `DN#` FROM email_check WHERE `email_id` = %s;""" 
  cursor.execute(query, (email,))
  results = cursor.fetchone()[0]
  
  query = """SELECT `vendor_id` FROM supplier_name_intervention WHERE `DN#` = %s;""" 
  cursor.execute(query, (results,))
  result = cursor.fetchone()
   
  vendor_id = ""
  if result:
      vendor_id = result[0] 
  query = """SELECT `domain` FROM supplier_table WHERE `id` = %s;""" 
  cursor.execute(query, (vendor_id,))
  result = cursor.fetchone()
  
  vendor_domain = ""
  if result:
    vendor_domain = result[0] 
  
  # if vendor_domain == "":
  #   results = []
  #   return results
  
  cursor.execute("SELECT `vendor_name` FROM supplier_table WHERE domain = %s" , (vendor_domain,))  # adjust column/table name as needed
  results = cursor.fetchall()
  
  cursor.close()
  conn.close()
  
  return results

def new_logsheet(log_type, email,detail):
  conn = get_db_connection()
  cursor = conn.cursor()
  
  log_subject = log_type
  log_detail = ""
  email = email
  now = datetime.now()
  date = now.strftime("%Y-%m-%d %H:%M:%S")
  color = ""
  if log_type == "New DN# Case":
    log_detail = f"The new DN# - {detail} has created."
    color = "primary"
  elif log_type == "Multi Document Intervention":
    color = "warning"
    if detail:
      log_detail = "DN - " + detail[0].get("DN#") + "\n"
      for multi_doc in detail:
        old_doc_list = multi_doc.get("old_doc_list")
        new_doc_list = multi_doc.get("doc_list")
        dn = multi_doc.get("DN#")
        log_detail = log_detail + old_doc_list + "=>" + new_doc_list + "\n"
  elif log_type == "Update Supplier Name":
    color = "warning"
    old_vendor_name = detail.get("old_vendor_name", "")  # Example field
    new_vendor_name = detail.get("vendor_name", "")  # Example field
    dn = detail.get("DN#", "")  # Example field
    log_detail = "DN - " + dn +"\n" + old_vendor_name + "=>" + new_vendor_name
    
  query = """INSERT INTO logsheet (`log`,`email`,`color`,`date`,`detail`) VALUES (%s,%s,%s,%s,%s)"""  
  cursor.execute(query, (log_type, email, color,date, log_detail,))
  conn.commit()
  
  cursor.close()
  conn.close()
  return []

def get_all_data(email):
  conn = get_db_connection()
  cursor = conn.cursor()
  
  cursor.execute("SELECT `admin_email` FROM user WHERE email = %s", (email,))
  emails = cursor.fetchone()
  admin_email = emails[0]

  cursor.execute("SELECT `role` FROM admin_table WHERE email = %s", (admin_email,))
  result = cursor.fetchone()
  final = []
  if result:
    if result[0] == 1 or result[0] == '1':
      cursor.execute("SELECT `id`,`log`,`email`,`color`,`date`,`detail` FROM logsheet ORDER BY `id` DESC")
      final = cursor.fetchall()
    else:
      cursor.execute("SELECT `id`,`log`,`email`,`color`,`date`,`detail` FROM logsheet WHERE `email`=%s ORDER BY `id` DESC",(email,))
      final = cursor.fetchall()
  
  final_data = []
  if final:
    for data in final:
      entry = {
        "id":data[0],
        "color":data[3],
        "title":data[1],
        "email":data[2],
        "datef":data[4],
        "detail":data[5],
        "deleted":False,
      }
      final_data.append(entry)
  print(final_data)
  return final_data
  # {
  #   id: 4,
  #   color: 'success',
  #   title:
  #     'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
  #   datef: '2023-06-03T23:28:56.782Z',
  #   deleted: false,
  # },
  
def get_logo_with_email(email):
  
  conn = get_db_connection()
  cursor = conn.cursor()
  
  cursor.execute("SELECT `email_id`,`logo`,`img`,`DN#` FROM logo_table WHERE `email_id`=%s",(email,))
  results = cursor.fetchall()
  print(results)
  final_result = []
  if results:
    for result in results:
      if result:
        id = result[1]
        cursor.execute("SELECT `domain`, `vendor_name` FROM supplier_table WHERE `id`=%s",(id,))
        supplier = cursor.fetchone()
        supplier_domain = ''
        supplier_name = ''
        if supplier:
          supplier_domain = supplier[0] 
          supplier_name = supplier[1]
        entry = {
          "img":result[2],
          "supplier_domain":supplier_domain,
          "supplier_name":supplier_name,
          "logo":result[1]
        }
        final_result.append(entry)
  cursor.close()
  conn.close()
  return final_result

def get_logo_filenames(LOGO_DIR):
    p = Path(LOGO_DIR)
    if not p.is_dir():
        return []
    return [f.name for f in p.iterdir() if f.suffix.lower() in {'.png', '.jpg', '.jpeg', '.svg', '.gif'}]
  
def get_all_logo_info():
  
  conn = get_db_connection()
  cursor = conn.cursor()
  
  BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
  LOGO_DIR = os.path.join(BASE_DIR, 'logo')
  results = get_logo_filenames(LOGO_DIR)
  final_result = []
  if results:
    for result in results:
      if result:
        id = os.path.splitext(result)[0]
        cursor.execute("SELECT `domain`, `vendor_name` FROM supplier_table WHERE `id`=%s",(id,))
        supplier = cursor.fetchone()
        supplier_domain = ''
        supplier_name = ''
        if supplier:
          supplier_domain = supplier[0] 
          supplier_name = supplier[1]
          entry = {
            "img":result,
            "supplier_domain":supplier_domain,
            "supplier_name":supplier_name,
            "logo":id
          }
          final_result.append(entry)
  cursor.close()
  conn.close()
  return final_result

def update_logo_info(data, email):
  
  conn = get_db_connection()
  cursor = conn.cursor()
  
  update_query = """UPDATE `logo_table` SET `logo` = %s, `img` = %s WHERE email_id = %s"""  
  cursor.execute(update_query, (data["logo"], data["img"],email ))
  conn.commit()
  cursor.close()
  conn.close()
  return []

def get_all_supplier():
  conn = get_db_connection()
  cursor = conn.cursor()
  
  query = """SELECT `domain`,`vendor_name` FROM supplier_table"""  
  cursor.execute(query)
  results = cursor.fetchall()
  final_info = []
  if results:
    for result in results:
      entry = {
        "domain":result[0],
        "name":result[1]
      }
      final_info.append(entry)
  cursor.close()
  conn.close()
  return final_info

def get_supplier_id_with_vendor_name(domain,name):
  conn = get_db_connection()
  cursor = conn.cursor()
  query = """SELECT `id` FROM supplier_table WHERE `domain` = %s AND `vendor_name` = %s"""
  cursor.execute(query, (domain,name, ))
  result = cursor.fetchone()

  supplier_id = ""
  if result:
    supplier_id = result[0]
  else:
    print("No supplier found for given domain and vendor name.")
    supplier_id = None
  
  cursor.close()
  conn.close()
  
  return supplier_id


def get_all_notification(email):
  conn = get_db_connection()
  cursor = conn.cursor()
  
  cursor.execute("SELECT `admin_email` FROM user WHERE email = %s", (email,))
  emails = cursor.fetchone()
  admin_email = emails[0]

  cursor.execute("SELECT `role` FROM admin_table WHERE email = %s", (admin_email,))
  result = cursor.fetchone()
  final = []
  role = 1
  if result:
    if result[0] == 1 or result[0] == '1':
      role = 1
    else:
      role = 2
  cursor.execute("SELECT `id`,`header`,`message`,`key`,`type`,`date` FROM notification_table ORDER BY `id` DESC")
  final = cursor.fetchall()
  final_data = []
  print(final)
  if final:
    for data in final:
      if role == 2:
        if data[4] == 'date-format' or data[4] == "incoterms":
          query = """SELECT `id` FROM attachment_table WHERE admin_email=%s AND `DN#`=%s"""
          cursor.execute(query,(email,data[3], ))
          result = cursor.fetchone()
          if result:
            entry = {
              "_id":data[0],
              "id":data[3],
              'type':data[4],
              'header':data[1],
              'color':'error',
              'message':data[2],
              'date':data[5],
            }
        else:
          query = """SELECT `id` FROM email_check WHERE admin_email=%s AND `email_id`=%s"""
          cursor.execute(query,(email,data[3], ))
          result = cursor.fetchone()
          if result:
            entry = {
              "_id":data[0],
              "id":data[3],
              'type':data[4],
              'header':data[1],
              'color':'warning',
              'message':data[2],
              'date':data[5],
            }
        final_data.append(entry)
      else:
        if data[4] == 'date-format' or data[4] == "incoterms":
          entry = {
            "_id":data[0],
            "id":data[3],
            'type':data[4],
            'header':data[1],
            'color':'error',
            'message':data[2],
            'date':data[5],
          }
        else:
          entry = {
            "_id":data[0],
            "id":data[3],
            'type':data[4],
            'header':data[1],
            'color':'warning',
            'message':data[2],
            'date':data[5],
          }
        final_data.append(entry)
  print(final_data)
  return final_data

def update_notification(dn,type,incoterm,dateFormat):
  print(dn)
  conn = get_db_connection()
  cursor = conn.cursor()
  if type == "incoterms":
    query = """UPDATE `attachment_table` SET `incoterms` = %s WHERE `DN#` = %s"""  
    cursor.execute(query, (incoterm, dn, ))
  else:
    query = """UPDATE `attachment_table` SET `date_format` = %s WHERE `DN#` = %s"""  
    cursor.execute(query, (dateFormat, dn, ))
  conn.commit()
  cursor.close()
  conn.close()
  return []
  