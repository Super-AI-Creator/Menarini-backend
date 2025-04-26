import mysql.connector
import re
from app.config.env import database_host, database_user, database_password, database_name 
from datetime import datetime
def new_turn(emailID, DN,amdin_email,date):
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host=database_host,
            user=database_user,
            password=database_password,  # No password as per your setup
            database=database_name
        )

        cursor = connection.cursor()

        # SQL query to update the DN field
        update_query = """UPDATE email_check SET `DN#` = %s WHERE email_id = %s;"""  
        cursor.execute(update_query, (DN, emailID))
        connection.commit()

        update_query = """INSERT INTO email_attachment (`email_id`,`DN#`) VALUES (%s,%s)"""  
        cursor.execute(update_query, (emailID, DN))
        connection.commit()
        
        # Check if the DN exists in attachment_table
        count_query = """SELECT COUNT(*) FROM attachment_table WHERE `DN#` = %s;"""  
        cursor.execute(count_query, (DN,))
        count_result = cursor.fetchone()[0]

        vendor_domain = ""
        vendor_name = ""
        if count_result == 0:
            insert_query = """INSERT INTO attachment_table (`DN#`, `admin_email`,`date`) VALUES (%s,%s,%s);"""  
            cursor.execute(insert_query, (DN,amdin_email,date,))  # Correct single-value tuple format
            connection.commit()
        else:
            # Get Supplier ID (fetchone returns a tuple or None)
            count_query = """SELECT `Supplier ID` FROM attachment_table WHERE `DN#` = %s;"""  
            cursor.execute(count_query, (DN,))
            result = cursor.fetchone()
            
            if result:  # Check if a row was returned
                supplier_id = result[0]  # Extract first column value from the tuple

                # Get vendor details using the extracted supplier_id (now a scalar value)
                vendor_query = """SELECT `domain`, `vendor_name` FROM supplier_table WHERE `id` = %s;"""  
                cursor.execute(vendor_query, (supplier_id,))
                vendor_result = cursor.fetchone()
                
                if vendor_result:  # Check if vendor exists
                    vendor_domain, vendor_name = vendor_result
        return vendor_domain, vendor_name
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    
    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")
def new_attachment(doc_type, DN):
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host=database_host,
            user=database_user,
            password=database_password,  # No password as per your setup
            database=database_name
        )

        cursor = connection.cursor()

        # Initialize update_query with a default value to prevent undefined variable error
        update_query = None  

        # Assign the correct SQL update query based on doc_type
        if doc_type == "DN":
            update_query = """UPDATE attachment_table SET DN = %s WHERE `DN#` = %s;"""
        elif doc_type == "INV":
            update_query = """UPDATE attachment_table SET INV = %s WHERE `DN#` = %s;"""
        elif doc_type == "COA":
            update_query = """UPDATE attachment_table SET COA = %s WHERE `DN#` = %s;"""
        elif doc_type == "Bill of Lading":
            update_query = """UPDATE attachment_table SET `Bill of Lading` = %s WHERE `DN#` = %s;"""
        elif doc_type == "Air Waybill":
            update_query = """UPDATE attachment_table SET `Air Waybill` = %s WHERE `DN#` = %s;"""

        # Ensure an update_query is selected before executing
        if update_query:
            cursor.execute(update_query, (1, DN))
            connection.commit()
        else:
            print(f"Error: Invalid doc_type '{doc_type}' provided.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    
    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")  


def email_new_attachment(doc_type, DN, emailID):
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host=database_host,
            user=database_user,
            password=database_password,  # No password as per your setup
            database=database_name
        )

        cursor = connection.cursor()

        # Initialize update_query with a default value to prevent undefined variable error
        update_query = None  

        # Assign the correct SQL update query based on doc_type
        if doc_type == "DN":
            update_query = """UPDATE email_attachment SET DN = %s WHERE `email_id` = %s;"""
        elif doc_type == "INV":
            update_query = """UPDATE email_attachment SET INV = %s WHERE `email_id` = %s;"""
        elif doc_type == "COA":
            update_query = """UPDATE email_attachment SET COA = %s WHERE `email_id` = %s;"""
        elif doc_type == "Bill of Lading":
            update_query = """UPDATE email_attachment SET `Bill of Lading` = %s WHERE `email_id` = %s;"""
        elif doc_type == "Air Waybill":
            update_query = """UPDATE email_attachment SET `Air Waybill` = %s WHERE `email_id` = %s;"""

        # Ensure an update_query is selected before executing
        if update_query:
            cursor.execute(update_query, (1, emailID))
            connection.commit()
        else:
            print(f"Error: Invalid doc_type '{doc_type}' provided.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    
    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")  

def start_ocr(DN):
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host=database_host,
            user=database_user,
            password=database_password,  # No password as per your setup
            database=database_name
        )

        cursor = connection.cursor()

        # SQL query to fetch values from attachment_table
        query = """SELECT DN, INV, COA, `Bill of Lading`, `Air Waybill` FROM attachment_table WHERE `DN#` = %s;"""
        cursor.execute(query, (DN,))
        result = cursor.fetchone()

        if result:
            dn_value, inv_value, coa_value, bol_value, awb_value = result

            # Check conditions
            if dn_value == 1 and inv_value == 1 and coa_value == 1 and (bol_value == 1 or awb_value == 1):
                return 1
            else:
                return 0
        else:
            print("No matching DN# found in the table.")
            return 0  # Return 0 if no matching record is found

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return 0  # Return 0 if there's a database error
    
    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")  


def get_supplier(domain):
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host=database_host,
            user=database_user,
            password=database_password,  # No password as per your setup
            database=database_name
        )
        cursor = connection.cursor()
        cursor.execute("SELECT vendor_domain, vendor_name FROM email_domain WHERE domain = %s", (domain,))
        result = cursor.fetchone()
        
        if result:
            vendor_domain, vendor_name = result  # Safe unpacking
        else:
            vendor_domain, vendor_name = '', ''
        
        return vendor_domain, vendor_name # Extract string from tuple or return None if no result
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None  # Ensure function always returns a value
    
    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")
  
def get_supplier_list():
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host=database_host,
            user=database_user,
            password=database_password,  # No password as per your setup
            database=database_name
        )
        cursor = connection.cursor()
        cursor.execute("SELECT vendor_name FROM supplier_table")
        result = cursor.fetchall()
        # print(result)
        return result if result else None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None  # Ensure function always returns a value
    
    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")
  
def get_exist_attachment(dn, doc_type):
    try:
        connection = mysql.connector.connect(
            host=database_host,
            user=database_user,
            password=database_password,
            database=database_name
        )

        # Use buffered cursor to prevent "Unread result found"
        cursor = connection.cursor(buffered=True)

        query_map = {
            "DN": "SELECT DN FROM attachment_table WHERE `DN#` = %s;",
            "INV": "SELECT INV FROM attachment_table WHERE `DN#` = %s;",
            "COA": "SELECT COA FROM attachment_table WHERE `DN#` = %s;",
            "Bill of Lading": "SELECT `Bill of Lading` FROM attachment_table WHERE `DN#` = %s;",
            "Air Waybill": "SELECT `Air Waybill` FROM attachment_table WHERE `DN#` = %s;"
        }

        query = query_map.get(doc_type)

        if query:
            cursor.execute(query, (dn,))
            result = cursor.fetchone()
            print(result)

            if result is not None:
                return result[0]
            else:
                return -1
        else:
            print(f"Error: Invalid doc_type '{doc_type}' provided.")
            return -1

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return -1

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

def exist_supplier_domain_and_name(supplier_domain, supplier_name):
    try:
        connection = mysql.connector.connect(
            host=database_host,
            user=database_user,
            password=database_password,  # No password as per your setup
            database=database_name
        )
        cursor = connection.cursor()
        
        count_query = """SELECT COUNT(*) FROM supplier_table WHERE `domain` = %s and `vendor_name` = %s;"""  
        cursor.execute(count_query, (supplier_domain,supplier_name,))
        count_result = cursor.fetchone()[0]
        
        # print(result)
        return count_result
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None  # Ensure function always returns a value

    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

def new_supplier_domain_and_name(supplier_domain, supplier_name):
    try:
        connection = mysql.connector.connect(
            host=database_host,
            user=database_user,
            password=database_password,
            database=database_name
        )
        # Use buffered cursor to ensure result is fully read
        cursor = connection.cursor(buffered=True)

        # Check if supplier already exists
        cursor.execute(
            "SELECT `id` FROM supplier_table WHERE `domain` = %s AND `vendor_name` = %s",
            (supplier_domain, supplier_name)
        )
        result = cursor.fetchone()

        if result:
            return  # Already exists
        else:
            # Insert new supplier domain and name
            insert_query = """INSERT INTO supplier_table (`domain`, `vendor_name`) VALUES (%s, %s);""" 
            cursor.execute(insert_query, (supplier_domain, supplier_name))
            connection.commit()

        return

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")


def set_supplier_for_attachments(DN, supplier_domain, supplier_name):
        
    try:
        connection = mysql.connector.connect(
            host=database_host,
            user=database_user,
            password=database_password,  # No password as per your setup
            database=database_name
        )
        cursor = connection.cursor()
        
        cursor.execute("SELECT id FROM supplier_table WHERE domain = %s and vendor_name = %s", (supplier_domain,supplier_name))
        vendor_table_id = cursor.fetchone()
        if vendor_table_id:
            vendor_table_id = vendor_table_id[0]
        update_query = """UPDATE attachment_table SET `Supplier ID` = %s WHERE `DN#` = %s;""" 
        cursor.execute(update_query, (vendor_table_id,DN,))
        connection.commit() 
        
        # print(result)
        return
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None  # Ensure function always returns a value

    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")
            

def get_supplier_from_logo(logo):
    try:
        connection = mysql.connector.connect(
            host=database_host,
            user=database_user,
            password=database_password,  # No password as per your setup
            database=database_name
        )
        vendor_domain  = ''
        vendor_name = ''
        cursor = connection.cursor()
        
        cursor.execute("SELECT domain, vendor_name FROM supplier_table WHERE id = %s ", (logo,))
        result = cursor.fetchone()
        
        if result:
            vendor_domain, vendor_name = result  # Safe unpacking
        else:
            vendor_domain, vendor_name = '', ''
        
        return vendor_domain, vendor_name # Extract string from tuple or return None if no result
        # print(result)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None  # Ensure function always returns a value

    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")
            
            

def set_item_count_for_attachments(DN, item_count, coa_item_count):
        
    try:
        connection = mysql.connector.connect(
            host=database_host,
            user=database_user,
            password=database_password,  # No password as per your setup
            database=database_name
        )
        cursor = connection.cursor()
        update_query = """UPDATE attachment_table SET `Item Count` = %s, `COA Count` = %s  WHERE `DN#` = %s;""" 
        cursor.execute(update_query, (item_count,coa_item_count,DN,))
        connection.commit() 
        
        # print(result)
        return
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None  # Ensure function always returns a value

    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")
            
            
def set_complete_flag(DN):
    try:
        connection = mysql.connector.connect(
            host=database_host,
            user=database_user,
            password=database_password,  # No password as per your setup
            database=database_name
        )
        cursor = connection.cursor()
        update_query = """UPDATE attachment_table SET  `complete` = %s  WHERE `DN#` = %s;""" 
        cursor.execute(update_query, (1,DN,))
        connection.commit() 
        
        # print(result)
        return
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None  # Ensure function always returns a value

    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

def email_no_domain(email_id, message, error_type):
    try:
        connection = mysql.connector.connect(
            host=database_host,
            user=database_user,
            password=database_password,  # No password as per your setup
            database=database_name
        )
        cursor = connection.cursor()
        cursor.execute("SELECT `id` FROM email_error_table WHERE `email_id` = %s and `error` = %s", (email_id, message, ))
        result = cursor.fetchone()
        
        if result:
            return
        else:
            cursor.execute("INSERT INTO email_error_table (`email_id`, `error`, `type`) VALUES (%s, %s, %s)",(email_id,message,error_type,))
            connection.commit()  # Make sure to commit INSERTs
            return
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None  # Ensure function always returns a value

    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")
        

def attatchment_error(dn, message, error_type, email_id, attachment_error, reference):
    try:
        connection = mysql.connector.connect(
            host=database_host,
            user=database_user,
            password=database_password,  # No password as per your setup
            database=database_name
        )
        cursor = connection.cursor()
        cursor.execute("SELECT `id` FROM error_table WHERE `DN#` = %s and `email_id` = %s and `message` = %s", (dn, email_id, message, ))
        result = cursor.fetchone()
        
        if result:
            return
        else:
            cursor.execute("INSERT INTO error_table (`DN#`, `message`, `type`,`email_id`,`attachment_error`,`reference`) VALUES (%s, %s, %s, %s, %s, %s)",(dn,message,error_type, email_id,attachment_error,reference,))
            connection.commit()  # Make sure to commit INSERTs
            return
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None  # Ensure function always returns a value

    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")
        
def supplier_name_intervention(email, domain, name, dn):
    
    try:
        connection = mysql.connector.connect(
            host=database_host,
            user=database_user,
            password=database_password,  # No password as per your setup
            database=database_name
        )
        cursor = connection.cursor()
        cursor.execute("SELECT `id` FROM supplier_name_intervention WHERE `DN#` = %s ", (dn, ))
        result = cursor.fetchone()
        
        if result:
            return
        else:
            cursor.execute("SELECT id FROM supplier_table WHERE domain = %s and vendor_name = %s", (domain,name))
            vendor_table_id = cursor.fetchone()
            if vendor_table_id:
                vendor_table_id = vendor_table_id[0]
            cursor.execute("INSERT INTO supplier_name_intervention (`email_id`, `DN#`, `vendor_id`) VALUES (%s, %s, %s)",(email, dn, vendor_table_id,))
            connection.commit()  # Make sure to commit INSERTs
            return
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None  # Ensure function always returns a value

    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")
            
def multi_doc_intervention(email,vendor_domain, vendor_name, dn, attachment_type, file_name):
    try:
        connection = mysql.connector.connect(
            host=database_host,
            user=database_user,
            password=database_password,  # No password as per your setup
            database=database_name
        )
        cursor = connection.cursor()
        cursor.execute("SELECT `id` FROM multi_doc_intervention WHERE `email_id` = %s AND `file_name` = %s", (dn, file_name , ))
        result = cursor.fetchone()
        
        if result:
            return
        else:
            cursor.execute("SELECT id FROM supplier_table WHERE domain = %s and vendor_name = %s", (vendor_domain,vendor_name))
            vendor_table_id = cursor.fetchone()
            if vendor_table_id:
                vendor_table_id = vendor_table_id[0]
            cursor.execute("INSERT INTO multi_doc_intervention (`email_id`, `DN#`, `doc_list`, `vendor_id`,`file_name`) VALUES (%s, %s, %s, %s,%s)",(email, dn, attachment_type, vendor_table_id,file_name,))
            connection.commit()  # Make sure to commit INSERTs
            return
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None  # Ensure function always returns a value

    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")
            
def domain_name_from_emailId(emailID):
    try:
        connection = mysql.connector.connect(
            host=database_host,
            user=database_user,
            password=database_password,  # No password as per your setup
            database=database_name
        )
        vendor_domain = ""
        vendor_name = ""
        cursor = connection.cursor()
        vendor_query = """SELECT `domain`, `vendor_name` FROM supplier_table WHERE `id` = %s;"""  
        cursor.execute(vendor_query, (emailID,))
        vendor_result = cursor.fetchone()
        
        if vendor_result:  # Check if vendor exists
            vendor_domain, vendor_name = vendor_result
        return vendor_domain, vendor_name
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None  # Ensure function always returns a value

    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")
            
def get_supplier_domain(sender):
    
    try:
        connection = mysql.connector.connect(
            host=database_host,
            user=database_user,
            password=database_password,  # No password as per your setup
            database=database_name
        )
        email = re.search(r'[\w\.-]+@[\w\.-]+', sender).group()
        vendor_domain = ""
        cursor = connection.cursor()
        vendor_query = """SELECT `domain` FROM user WHERE `email` = %s;"""  
        cursor.execute(vendor_query, (email,))
        vendor_result = cursor.fetchone()
        
        if vendor_result:  # Check if vendor exists
            vendor_domain = vendor_result[0]
        return vendor_domain
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None  # Ensure function always returns a value

    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")
            
def get_all_admin_info():
    try:
        connection = mysql.connector.connect(
            host=database_host,
            user=database_user,
            password=database_password,  # No password as per your setup
            database=database_name
        )
        cursor = connection.cursor()
        vendor_query = """SELECT `email`,`password`,`imap_server` FROM admin_table"""  
        cursor.execute(vendor_query)
        vendor_result = cursor.fetchall()
        
        result = []
        if vendor_result: 
            for vendor in vendor_result:
                if vendor:
                    entry = {
                        "email":vendor[0],
                        "password":vendor[1],
                        "server":vendor[2],
                    }
                    result.append(entry)
        return result
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None  # Ensure function always returns a value

    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")
            

def flatten_data(data):
    """
    Flattens the data if it's a 2-level array.
    Returns a 1-level dictionary from the first value.
    """
    if isinstance(data, list):  # It's either a 1-level or 2-level array
        if isinstance(data[0], list):  # 2-level array
            return data[0][0]  # Flatten it by accessing the first item
        else:  # 1-level array
            return data[0]  # Access the first item of the 1-level array
    return data

def insert_ocr_result(dn, dn_data, inv_data, coa_data, bill_of_lading,dn_attachment,inv_attachment,coa_attachment,bol_attachment):
    connection = mysql.connector.connect(
        host=database_host,
        user=database_user,
        password=database_password,  # No password as per your setup
        database=database_name
    )
    cursor = connection.cursor()

    # Insert into dn_table
    if dn_data:
        for data in dn_data:
            data = flatten_data(data)  # Flatten the data if it's in a 2-level array
            query = """
                INSERT INTO dn_table 
                (`DN#`, `PO#`, `Vendor Part Code`, `Customer Part Code`, `GIC Code`, `Packing Slip#`, `Quantity`, `Batch#`, `Manufacturing Date`, `Expiry Date`, `Document Date`, `Incoterms`, `Item Description`,`Document`) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                dn,
                data.get('PO#'),
                data.get('Vendor Part Code'),
                data.get('Customer Part Code'),
                data.get('GIC Code'),
                data.get('Packing Slip#'),
                data.get('Quantity'),
                data.get('Batch#'),
                data.get('Manufacturing Date'),
                data.get('Expiry Date'),
                data.get('Document Date'),
                data.get('Incoterm'),
                data.get('Item Description'),
                dn_attachment,
            ))

    # Insert into inv_table
    if inv_data:
        for data in inv_data:
            data = flatten_data(data)  # Flatten the data if it's in a 2-level array
            query = """
                INSERT INTO inv_table 
                (`DN#`, `PO#`, `Vendor Part Code`, `Packing Slip#`, `Quantity`, `Batch#`, `Manufacturing Date`, `Customer Part Code`, `GIC Code`, `Expiry Date`, `Document Date`, `INV NO#`, `Incoterms`, `Item Description`, `Document`)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                dn,
                data.get('PO#'),
                data.get('Vendor Part Code'),
                data.get('Packing Slip#'),
                data.get('Quantity'),
                data.get('Batch#'),
                data.get('Manufacturing Date'),
                data.get('Customer Part Code'),
                data.get('GIC Code'),
                data.get('Expiry Date'),
                data.get('Document Date'),
                data.get('Invoice Number'),
                data.get('Incoterm'),
                data.get('Item Description'),
                inv_attachment,
            ))

    # Insert into coa_table
    if coa_data:
        for data in coa_data:
            data = flatten_data(data)  # Flatten the data if it's in a 2-level array
            query = """
                INSERT INTO coa_table 
                (`DN#`, `Vendor Part Code`, `Customer Part Code`, `GIC Code`, `Item Description`, `Manufacturing Date`, `Expiry Date`,`Document`)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                dn,
                data.get('Vendor Part Code'),
                data.get('Customer Part Code'),
                data.get('GIC Code'),
                data.get('Item Description'),
                data.get('Manufacturing Date'),
                data.get('Expiry Date'),
                coa_attachment,
            ))

    # Insert into bol_table
    if bill_of_lading:
        data = flatten_data(bill_of_lading)  # Flatten the data if it's in a 2-level array
        query = """
            INSERT INTO bol_table 
            (`DN#`, `Incoterms`, `Posting Date`,`Document`)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (
            dn,
            data.get('Incoterm'),
            data.get('Posting Date'),
            bol_attachment,
        ))

    connection.commit()
    cursor.close()
    connection.close()
    
    
def new_log_sheet(log_type, email,detail):
    try:
        connection = mysql.connector.connect(
            host=database_host,
            user=database_user,
            password=database_password,  # No password as per your setup
            database=database_name
        )
        cursor = connection.cursor()
        
        now = datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        query = """INSERT INTO logsheet (`log`,`email`,`color`,`date`,`detail`) VALUES (%s,%s,%s,%s,%s)"""  
        cursor.execute(query, (log_type, email, 'error',date, detail,))
        connection.commit()
        return
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None  # Ensure function always returns a value

    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")
            
def logo_check(emailID,logo_id, logo_img, dn):
    try:
        connection = mysql.connector.connect(
            host=database_host,
            user=database_user,
            password=database_password,  # No password as per your setup
            database=database_name
        )
        cursor = connection.cursor()
        
        query = """SELECT `id` FROM logo_table WHERE `email_id`=%s and `img`=%s"""
        cursor.execute(query,(emailID, logo_img,))
        result = cursor.fetchone()
        
        flag = 0
        if result:
            flag = 1
        else:
            query = """INSERT INTO logo_table (`email_id`,`logo`,`img`,`DN#`) VALUES (%s,%s,%s,%s)"""  
            cursor.execute(query, (emailID, logo_id, logo_img, dn,))
            connection.commit()
        return
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None  # Ensure function always returns a value

    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")