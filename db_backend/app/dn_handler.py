from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token,jwt_required, get_jwt_identity
from .google_drive import delete_file_from_drive
import mysql.connector
import os
import re
import ast
from datetime import datetime
from collections import OrderedDict
import json

dn_bp = Blueprint('dn', __name__)


def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # no password
        database='menarini'
    )

def get_dn_data_with_role(role, email):
  
  conn = get_db_connection()
  cursor = conn.cursor()
  
  doc_type_map = {
    "DN":"DN",
    "INV":"INV",
    "COA":"COA",
    "BOL":"BOL",
    "AWB":"AWB",
    "Certificate of Analysis":"COA",
    "Bill of Lading":"BOL",
    "Air Waybill":"AWB"
  }
  if role == 1:
    cursor.execute("SELECT `DN#`,`DN`,`INV`,`Bill of Lading`,`Air Waybill`,`COA`,`complete`,`Supplier ID`,`date`,`final_complete`,`id` FROM attachment_table")
    results = cursor.fetchall()
  else:
    cursor.execute("SELECT `DN#`,`DN`,`INV`,`Bill of Lading`,`Air Waybill`,`COA`,`complete`,`Supplier ID`,`date`,`final_complete`,`id` FROM attachment_table WHERE admin_email=%s",(email,))
    results = cursor.fetchall()
  final_result = []
  if results:
    for result in results:
        dn_number = result[0]
        cursor.execute("SELECT `id` FROM coa_table WHERE `DN#`=%s",(dn_number,))
        count_result = cursor.fetchall()
        dn = result[1]
        inv = result[2]
        bol = result[3]
        awb = result[4]
        coa = result[5]
        complete = result[6]
        supplier_id = result[7]
        date = result[8]
        parsed_date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")
        formatted_date = f"{parsed_date.month}/{parsed_date.day}/{parsed_date.year}"
        supplier_name = ""
        cursor.execute("SELECT `vendor_name` FROM supplier_table WHERE id = %s" , (supplier_id,))
        supplier = cursor.fetchone()
        
        if supplier:
          supplier_name = supplier[0]

        final_complete = result[9]
        id = result[10]
        entry = {
          "id":id,
          "DN#":dn_number,
          "DN":dn,
          "INV":inv,
          "COA":coa,
          "BOL":bol,
          "AWB":awb,
          "Date":formatted_date,
          "Supplier":supplier_name,
          "coa_count":len(count_result),
          "Status":"Incomplete",
          "Progress":0
        }
        
        cursor.execute("SELECT `attachment_error`,`reference` FROM error_table WHERE `DN#` = %s" , (dn_number,))
        error_list = cursor.fetchall()
        if error_list:
          for error in error_list:
            # if error[0] == -1:
            #   if entry.get(doc_type_map[error[1]]):
            #     entry[doc_type_map[error[1]]] = -1
            #     entry["Status"] = "Error"
            if error[0] == -2:
              entry["DN"] = -2
              entry["Status"] = "Error"
        
        progress = 0
        if entry["DN"] == 1:
          progress = progress + 20
        if entry["INV"] == 1:
          progress = progress + 20
        if entry["COA"] == 1:
          progress = progress + 20
        if entry["BOL"] == 1 or entry["AWB"] == 1:
          progress = progress + 20
        if final_complete == 1:
          progress = progress + 20
          entry["Status"] = "Posted"
        if progress == 80:
          entry["Status"] = "Complete"
        entry["Progress"] = progress
        final_result.append(entry)
  return final_result

  
@dn_bp.route('/all_dn', methods=['POST'])
def all_dn_data():
  data = request.get_json()
  email = data.get("email")
  role = data.get("role")
  
  conn = get_db_connection()
  cursor = conn.cursor()
  cursor.execute("SELECT `admin_email` FROM user WHERE email = %s", (email,))
  emails = cursor.fetchone()
  admin_email = emails[0]

  cursor.execute("SELECT `role` FROM admin_table WHERE email = %s", (admin_email,))
  result = cursor.fetchone()
  if result:
    if result[0] == 1 or result[0] == '1':
      result = get_dn_data_with_role(1,email)
    else:
      result = get_dn_data_with_role(2,email)
  # print(result)
  return result


@dn_bp.route('/attachment_info', methods=['POST'])
def dn_attachment_data():
    data = request.get_json()
    doc_type = data.get("Doc Type")
    dn = data.get("DN#")
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Initialize query and columns
    query = ""
    columns = []

    if doc_type == "DN":
        columns = [
            "PO#", "Item Code",
            "Packing Slip#", "Quantity", "Batch#", "Manufacturing Date",
            "Expiry Date", "Document Date", "Incoterms", "Item Description","Document","id"
        ]
        query = f"""
            SELECT {', '.join([f'`{col}`' for col in columns])}
            FROM dn_table
            WHERE `DN#`=%s
        """
    elif doc_type == "INV":
        columns = [
            "PO#",  "Packing Slip#", "Quantity", "Batch#",
            "Manufacturing Date", "Item Code", 
            "Expiry Date", "Document Date", "INV NO#", "Incoterms", "Item Description","Document","id"
        ]
        query = f"""
            SELECT {', '.join([f'`{col}`' for col in columns])}
            FROM inv_table
            WHERE `DN#`=%s
        """
    elif doc_type == "COA":
        columns = [
            "Item Description", "Manufacturing Date", "Expiry Date","Document","id","Batch#","flag"
        ]
        query = f"""
            SELECT {', '.join([f'`{col}`' for col in columns])}
            FROM coa_table
            WHERE `DN#`=%s
        """
    elif doc_type in ["BOL", "AWB"]:
        columns = ["Incoterms", "Posting Date","Document","id"]
        query = f"""
            SELECT {', '.join([f'`{col}`' for col in columns])}
            FROM bol_table
            WHERE `DN#`=%s
        """

    if query:
        cursor.execute(query, (dn,))
        rows = cursor.fetchall()  # Fetch only one result (since we expect only one row)
        
        # Check if any row was returned, and process it
        response = []
        if rows:
          for row in rows:
            result_dict = {}
            for i in range(len(columns)):
                result_dict[columns[i]] = row[i]  # Maintain the order in which they appear
            response.append(result_dict)

        # cursor.fetchall()  # Ensure all results are processed before closing the cursor

        cursor.close()
        conn.close()

        # Manually construct the JSON response
        
        # print(response)
        # Return the result as JSON with the original field order
        return response
      

@dn_bp.route('/check_coa_flag', methods=['POST'])
def check_coa_flag():
    data = request.get_json()
    id = data.get("id")
    conn = get_db_connection()
    cursor = conn.cursor()
    print("---------------------------")
    flag_status = 0
    
    query  = "SELECT `flag` FROM coa_table WHERE `id`=%s"
    cursor.execute(query, (id,))
    flag_status_result = cursor.fetchone() 

    if flag_status_result:
      flag_status = flag_status_result[0]
    
    if flag_status == 0:
      flag_status = 1
    else:
      flag_status = 0
    cursor.execute("UPDATE coa_table SET `flag`=%s WHERE id = %s",(flag_status,id,))
    conn.commit()
    
    cursor.close()
    conn.close()
    return []


@dn_bp.route('/coa_attachment_info', methods=['POST'])
def coa_attachment_info():
    data = request.get_json()
    doc_type = data.get("Doc Type")
    dn = data.get("DN#")
    index = data.get("index")
    index = int(index)
    index = index - 1
    conn = get_db_connection()
    cursor = conn.cursor()
    
    columns = [
            "Item Description", "Manufacturing Date", "Expiry Date","Document","id","Batch#"
    ]
    query = f"""
        SELECT {', '.join([f'`{col}`' for col in columns])}
        FROM coa_table
        WHERE `DN#`=%s
    """
    cursor.execute(query, (dn,))
    rows = cursor.fetchall() 

    response = []
    if rows:
      for (ind,row) in enumerate(rows):
        if ind == index:
          result_dict = {}
          for i in range(len(columns)):
              result_dict[columns[i]] = row[i]  # Maintain the order in which they appear
          response.append(result_dict)
    
    cursor.close()
    conn.close()
    return response

@dn_bp.route('/error_info', methods=['POST'])
def dn_error_info():
    data = request.get_json()
    doc_type = data.get("Doc Type")
    dn = data.get("DN#")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT `message`,`email_id` FROM error_table WHERE `DN#` = %s", (dn,))
    results = cursor.fetchall()

    final = []
    if results:
      for result in results:
        entry = {"message":result[0], "emailID":result[1]}
        final.append(entry)
    
    cursor.close()
    conn.close()
    return final


@dn_bp.route('/ocr_info', methods=['POST'])
def ocr_info():
    data = request.get_json()
    doc_type = data.get("Doc Type")
    dn = data.get("DN#")
    print("------------")
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT `index`,`key`,`x`,`y`,`width`,`height`,`page_width`,`page_height`,`page`,`pdf_path`,`id` FROM ocr_table WHERE `DN#` = %s and `doc_type` = %s", (dn,doc_type,))
    results = cursor.fetchall()

    final = []
    if results:
      for result in results:
        entry = {
          "index":result[0],
          "key":result[1],
          "x":result[2],
          "y":result[3],
          "width":result[4],
          "height":result[5],
          "page_width":result[6],
          "page_height":result[7],
          "page":result[8],
          "pdf_path":result[9],
          "id":result[10],
        }
        final.append(entry)
    cursor.close()
    conn.close()
    return final


@dn_bp.route('/coa_ocr_info', methods=['POST'])
def coa_ocr_info():
    data = request.get_json()
    doc_type = data.get("Doc Type")
    dn = data.get("DN#")
    file_path = data.get("document")
    print("------------")
    document = os.path.basename(file_path)
    print(document)
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT `index`,`key`,`x`,`y`,`width`,`height`,`page_width`,`page_height`,`page`,`pdf_path`,`id` FROM ocr_table WHERE `DN#` = %s and `doc_type` = %s and `pdf_path`=%s", (dn,doc_type,document,))
    results = cursor.fetchall()

    final = []
    if results:
      for result in results:
        entry = {
          "index":result[0],
          "key":result[1],
          "x":result[2],
          "y":result[3],
          "width":result[4],
          "height":result[5],
          "page_width":result[6],
          "page_height":result[7],
          "page":result[8],
          "pdf_path":result[9],
          "id":result[10],
        }
        final.append(entry)
    cursor.close()
    conn.close()
    print("((((((()))))))")
    print(final)
    return final

@dn_bp.route('/create_field_position', methods=['POST'])
def create_field_position():
    data = request.get_json()
    doc_type = data.get("Doc Type")
    dn = data.get("DN#")
    pdf_path = data.get("pdf_path")
    key = data.get("key")
    index = data.get("index")
    x = data.get("x")
    y = data.get("y")
    width = data.get("width")
    height = data.get("height")
    page = data.get("page")
    page_width = data.get("page_width")
    page_height = data.get("page_height")
    print("------------")
    print(data)
    conn = get_db_connection()
    cursor = conn.cursor()

    # cursor.execute(" `index`,`key`,`x`,`y`,`width`,`height`,`page_width`,`page_height`,`page`,`pdf_path`,`id` FROM ocr_table WHERE `DN#` = %s and `doc_type` = %s", (dn,doc_type,))
    cursor.execute("INSERT INTO ocr_table (`DN#`,`doc_type`,`index`,`key`,`x`,`y`,`width`,`height`,`page_width`,`page_height`,`page`,`pdf_path`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(dn,doc_type, index, key, x,y,width,height, page_width, page_height, page, pdf_path,))
    conn.commit()

    cursor.close()
    conn.close()
    return []
  
  
@dn_bp.route('/update_field_position', methods=['POST'])
def update_field_position():
    data = request.get_json()
    id = data.get("id")
    x = data.get("x")
    y = data.get("y")
    width = data.get("width")
    height = data.get("height")
    page = data.get("page")
    print("------------")
    print(data)
    conn = get_db_connection()
    cursor = conn.cursor()

    # cursor.execute(" `index`,`key`,`x`,`y`,`width`,`height`,`page_width`,`page_height`,`page`,`pdf_path`,`id` FROM ocr_table WHERE `DN#` = %s and `doc_type` = %s", (dn,doc_type,))
    cursor.execute("UPDATE ocr_table SET `x`=%s,`y`=%s,`width`=%s,`height`=%s,`page`=%s WHERE id = %s",(x,y,width,height,page,id))
    conn.commit()

    cursor.close()
    conn.close()
    return []
  
@dn_bp.route('/update_fields', methods=['POST'])
def update_fields():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    data = request.get_json()
    update_data = data.get("data")
    dn = data.get("DN#")
    doc_type = data.get("DocType")
    
    # [{'id': 37, 'changes': {'Document Date': '25/03/2521', 'Expiry Date': '10-May-202`129', 'GIC Code': '12312', 'Incoterms': 'FCA453', 'Quantity': '14,990jjj'}}]
    if update_data:
      for data in update_data:
        update_id = data.get("id")
        changed_data = data.get("changes")
        table_name = ""
        if doc_type == "DN":
          table_name = "dn_table"
        elif doc_type == "INV":
          table_name = "inv_table"
        elif doc_type == "COA":
          table_name = "coa_table"
        else:
          table_name = "bol_table"
        
        set_clause = ", ".join(f"`{key}` = %s" for key in changed_data.keys())
        values = list(changed_data.values())
        sql = f"UPDATE `{table_name}` SET {set_clause} WHERE id = %s"
        values.append(update_id)
        print(values)
        cursor.execute(sql, values)
        conn.commit()
    cursor.close()
    conn.close()
    return []

@dn_bp.route('/get_po_list', methods=['POST'])
def get_po_list():
    data = request.get_json()
    dn = data.get("DN#")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT `Supplier ID`,`date` FROM attachment_table WHERE `DN#` = %s",(dn,))
    result = cursor.fetchone()
    supplier_name = ""
    date = ""
    if result:
      dt = datetime.strptime(result[1], "%a, %d %b %Y %H:%M:%S %z")
      date = dt.strftime("%d-%m-%Y")
      cursor.execute("SELECT `vendor_name` FROM supplier_table WHERE `id` = %s",(result[0],))
      result = cursor.fetchone()
      if result:
        supplier_name = result[0]

    cursor.execute("SELECT `PO#`,`Document` FROM dn_table WHERE `DN#` = %s", (dn,))
    results = cursor.fetchall()

    final = []
    if results:
       for result in results:
          status = "Incomplete"
          cursor.execute("SELECT `id` FROM staging_table WHERE `PO#` = %s", (result[0],))
          flag = cursor.fetchone()
          if flag:
             status = "Complete"
          entry = {
             "PO#":result[0],
             "status":status,
             "supplier_name":supplier_name,
             "date":date,
             "document":result[1]
          }
          final.append(entry)
    cursor.close()
    conn.close()
    return final


@dn_bp.route('/update_dn_table', methods=['POST'])
def update_dn_table():
    data = request.get_json()
    data = data.get("data")
    dn_change = data.get("dn")
    inv_change = data.get("inv")
    coa_change = data.get("coa")
    bol_change = data.get("bol")
    conn = get_db_connection()
    cursor = conn.cursor()
    if dn_change:
       for data in dn_change.values():
          row_id = data['id']
          key_to_update = next(k for k in data if k != 'id')  # e.g., 'Expiry Date'
          new_value = data[key_to_update]
          query = f"UPDATE dn_table SET `{key_to_update}` = %s WHERE id = %s"
          cursor.execute(query, (new_value, row_id))

    if inv_change:
       for data in inv_change.values():
          row_id = data['id']
          key_to_update = next(k for k in data if k != 'id')  # e.g., 'Expiry Date'
          new_value = data[key_to_update]
          query = f"UPDATE inv_table SET `{key_to_update}` = %s WHERE id = %s"
          cursor.execute(query, (new_value, row_id))

    if coa_change:
       for data in inv_change.values():
          row_id = data['id']
          key_to_update = next(k for k in data if k != 'id')  # e.g., 'Expiry Date'
          new_value = data[key_to_update]
          query = f"UPDATE coa_table SET `{key_to_update}` = %s WHERE id = %s"
          cursor.execute(query, (new_value, row_id))

    conn.commit()
    cursor.close()
    conn.close()
    return []


@dn_bp.route('/duplicated_test', methods=['POST'])
def duplicated_test():
    data = request.get_json()
    doc_type = data.get("Doc Type")
    dn = data.get("DN#")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT `id`,`drive_file_id`,`source` FROM duplicated_attachment WHERE `DN#` = %s AND `doc_type`=%s", (dn,doc_type))
    results = cursor.fetchall()

    final = []
    if results:
      if doc_type!='COA':
        for result in results:
          entry = {
             'id':result[0],
             'DN#':dn,
             'doc_type':doc_type,
             'drive_file_id':result[1],
             'source':result[2]
          }
          final.append(entry)
    cursor.close()
    conn.close()
    return final

   
def delete_database_data(doc_type,dn):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if doc_type=="DN":
            query = """DELETE FROM dn_table WHERE `DN#` = %s""" 
            cursor.execute(query, (dn,))
        if doc_type=="INV":
            query = """DELETE FROM inv_table WHERE `DN#` = %s""" 
            cursor.execute(query, (dn,))
        if doc_type=="COA":
            query = """DELETE FROM coa_table WHERE `DN#` = %s""" 
            cursor.execute(query, (dn,))
        if doc_type=="BOL":
            query = """DELETE FROM bol_table WHERE `DN#` = %s""" 
            cursor.execute(query, (dn,))
        conn.commit() 


    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None  # Ensure function always returns a value

    finally:
        # Close the database connection
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection closed.")

def get_google_drive_document_info(dn, doc_type):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        result = []
        if doc_type=="DN":
            query = """SELECT `Document` FROM dn_table WHERE `DN#` = %s""" 
            cursor.execute(query, (dn,))
            result = cursor.fetchone()
        if doc_type=="INV":
            query = """SELECT `Document` FROM inv_table WHERE `DN#` = %s""" 
            cursor.execute(query, (dn,))
            result = cursor.fetchone()
        if doc_type=="COA":
            query = """SELECT `Document` FROM coa_table WHERE `DN#` = %s""" 
            cursor.execute(query, (dn,))
            result = cursor.fetchone()
        if doc_type=="BOL":
            query = """SELECT `Document` bol_table WHERE `DN#` = %s""" 
            cursor.execute(query, (dn,))
            result = cursor.fetchone()
        if result:
          path = result[0]
          parts = os.path.normpath(path).split(os.sep)
          # Extract desired parts
          ro = parts[0] if len(parts) > 0 else None
          supplier_name = parts[1] if len(parts) > 1 else None
          shipment_id = parts[2] if len(parts) > 2 else None
          return {"supplier_domain": ro, "supplier_name" :supplier_name, "dn":shipment_id}
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None  # Ensure function always returns a value

    finally:
        # Close the database connection
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection closed.")
   


def new_log_sheet(log_type, email,detail):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        query = """INSERT INTO logsheet (`log`,`email`,`color`,`date`,`detail`) VALUES (%s,%s,%s,%s,%s)"""  
        cursor.execute(query, (log_type, email, 'error',date, detail,))
        conn.commit()
        return
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None  # Ensure function always returns a value

    finally:
        # Close the database connection
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection closed.")
            

@dn_bp.route('/update_duplicated_state', methods=['POST'])
def update_duplicated_state():
    data = request.get_json()
    duplicatedDocument = data.get("duplicatedDocument")
    doc_type = data.get("Doc Type")
    dn = data.get("DN#")
    email = data.get("email")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT `id`,`drive_file_id`,`doc_type` FROM duplicated_attachment WHERE `doc_type`=%s and `DN#` = %s" ,(doc_type,dn,))
    results = cursor.fetchall()
    final = []
    id_list = []
    supplier_domain = ""
    supplier_name = ""
    drive_dn = ""
    if results:
      for result in results:
        if result[0] != duplicatedDocument:
            if supplier_domain == "":
              updated_supplier_info = get_google_drive_document_info(dn,doc_type)
              supplier_domain = updated_supplier_info["supplier_domain"]
              supplier_name = updated_supplier_info["supplier_name"]
              drive_dn = updated_supplier_info["dn"]
            id_list.append(result[0])
            delete_file_from_drive(result[1])  # Corrected line
            delete_database_data(doc_type, dn)
    if id_list:
      query = """INSERT INTO google_drive_change (`supplier_domain`,`supplier_name`,`dn`) VALUES (%s,%s,%s)"""  
      cursor.execute(query, (supplier_domain,supplier_name,drive_dn,))
      for id in id_list:
        query = """DELETE FROM duplicated_attachment WHERE `id` = %s""" 
        cursor.execute(query, (id,))
      conn.commit() 
          
    sheet_error = "The DN - "+dn+" updated "+ doc_type +"document. Check it."
    new_log_sheet("Attachment Error",email,sheet_error)
    cursor.close()
    conn.close()
    return final