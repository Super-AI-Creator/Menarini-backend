from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token,jwt_required, get_jwt_identity
from .ocr_handler import extract_matching_values_with_positions
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
        dn = result[1]
        inv = result[2]
        bol = result[3]
        awb = result[4]
        coa = result[5]
        complete = result[6]
        supplier_id = result[7]
        date = result[8]
        parsed_date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")
        formatted_date = parsed_date.strftime("%a, %d %b %Y")
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
          "Status":"Incomplete",
          "Progress":0
        }
        
        cursor.execute("SELECT `attachment_error`,`reference` FROM error_table WHERE `DN#` = %s" , (dn_number,))
        error_list = cursor.fetchall()
        if error_list:
          for error in error_list:
            if error[0] == -1:
              if entry.get(doc_type_map[error[1]]):
                entry[doc_type_map[error[1]]] = -1
                entry["Status"] = "Error"
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
  cursor.execute("SELECT `role` FROM admin_table WHERE email = %s", (email,))
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
            "PO#", "Vendor Part Code", "Customer Part Code", "GIC Code",
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
            "PO#", "Vendor Part Code", "Packing Slip#", "Quantity", "Batch#",
            "Manufacturing Date", "Customer Part Code", "GIC Code",
            "Expiry Date", "Document Date", "INV NO#", "Incoterms", "Item Description","Document","id"
        ]
        query = f"""
            SELECT {', '.join([f'`{col}`' for col in columns])}
            FROM inv_table
            WHERE `DN#`=%s
        """
    elif doc_type == "COA":
        columns = [
            "Vendor Part Code", "Customer Part Code", "GIC Code",
            "Item Description", "Manufacturing Date", "Expiry Date","Document","id"
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
    input_json = data.get("data")
    dn = data.get("DN#")
    pdf_path = data.get("pdf_path")
    
    result = extract_matching_values_with_positions(pdf_path, input_json)
    # print(result)
    return result
  
  
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
# [{'page': 1, 'matches': [{'key': 'Packing Slip#', 'value': '191370', 'x': 1798, 'y': 645, 'width': 136, 'height': 26}, {'key': 'Vendor Part Code', 'value': '4262A', 'x': 646, 'y'
# : 1125, 'width': 116, 'height': 26}, {'key': 'Quantity', 'value': '1', 'x': 70, 'y': 1125, 'width': 1408, 'height': 25}, {'key': 'Batch#', 'value': '64512', 'x': 70, 'y': 1125, 'width': 1
# 600, 'height': 26}, {'key': 'Expiry Date', 'value': '31/08/2028', 'x': 526, 'y': 1243, 'width': 232, 'height': 30}, {'key': 'PO#', 'value': 'P0O1-006812', 'x': 1603, 'y': 1285, 'width': 2
# 35, 'height': 26}, {'key': 'GIC Code', 'value': 'F00008511', 'x': 331, 'y': 1285, 'width': 211, 'height': 26}, {'key': 'Customer Part Code', 'value': 'RBMENFASSGOOO0O1', 'x': 595, 'y': 13
# 25, 'width': 331, 'height': 26}, {'key': 'Document Date', 'value': '18-OCT-2024', 'x': 526, 'y': 2365, 'width': 256, 'height': 26}, {'key': 'Incoterms', 'value': 'CIP', 'x': 524, 'y': 260
# 7, 'width': 66, 'height': 24}]}]