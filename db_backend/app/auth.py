from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token,jwt_required, get_jwt_identity
import mysql.connector
bp = Blueprint('auth', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # no password
        database='menarini'
    )
    
    
@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    gmail_password = data.get('gmail_password')
    domain = data.get('domain')
    if not username or not email or not password:
        return jsonify({'msg': 'Missing fields'}), 400

    hashed_password = generate_password_hash(password)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """UPDATE `user` SET `password`=%s, `gmail_password`=%s, `domain`=%s WHERE `email`=%s"""   
    cursor.execute(query, (hashed_password,gmail_password,domain,email, ))
    conn.commit()

    cursor.close()
    conn.close()
    # return 
    # user = User(username=username, email=email, password=hashed_password)
    # db.session.add(user)
    # db.session.commit()

    return jsonify({'msg': 'User created'}), 201


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # user = User.query.filter_by(email=email).first()
    # if user and check_password_hash(user.password, password):
        # access_token = create_access_token(identity=user.id)
        # return jsonify(access_token=access_token), 200
    
    print(email)
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """SELECT `password`,`role`,`username` FROM user WHERE `email` = %s"""   
    cursor.execute(query, (email,))
    result = cursor.fetchone()
    print(result)    
    
    if result:
        if result[0]:
            if check_password_hash(result[0], password):
                access_token = create_access_token(identity=email)
                if result[1] == 1:           
                    return jsonify({"token":access_token,"user":{"role":"admin","email":email,"name":result[2]}})
                
                else:              
                    return jsonify({"token":access_token,"user":{"role":"user","email":email,"name":result[2]}})
        
    cursor.close()
    conn.close()
    
    return jsonify({'msg': 'Invalid credentials'}), 401

@bp.route('/verify', methods=['Get'])
@jwt_required()
def verify():
    email = get_jwt_identity()
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """SELECT `password`,`role`,`username` FROM user WHERE `email` = %s"""   
    cursor.execute(query, (email,))
    result = cursor.fetchone()
    print(result)    
    
    if result:
        access_token = create_access_token(identity=email)
        if result[1] == 1:           
            return jsonify({"token":access_token,"user":{"role":"admin","email":email,"name":result[2]}})
        
        else:              
            return jsonify({"token":access_token,"user":{"role":"user","email":email,"name":result[2]}})

    cursor.close()
    conn.close()
    
    return jsonify({'msg': 'Invalid credentials'}), 401


def get_user_info(email, firstname,lastname):
    full_name = firstname+lastname
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """SELECT `password`,`role`,`username` FROM user WHERE `email` = %s"""   
    cursor.execute(query, (email,))
    result = cursor.fetchone()
    
    if result:
        access_token = create_access_token(identity=email)
        if result[1] == 1:           
            return jsonify({"success":"login success" , "token":access_token,"user":{"role":"admin","email":email,"name":result[2]}})
        
        else:              
            return jsonify({"success":"login success" , "token":access_token,"user":{"role":"user","email":email,"name":result[2]}})
    else:
        role = 2
        
        query = """SELECT `id` FROM admin_table WHERE `email` = %s """
        cursor.execute(query, (email,))
        result = cursor.fetchone()
    
        if result:
            role = 1
        query = """INSERT INTO user (`email`,`username`,`role`) VALUES (%s,%s,%s)"""
        cursor.execute(query, (email, full_name, role,))   
        conn.commit()
        return jsonify({"success":"pre-register success","email":email,"name":full_name }) 
       


@bp.route('/change_password', methods=['Post'])
def change_password():
    data = request.get_json()
    currentPassword = data.get('currentPassword')
    newPassword = data.get('newPassword')
    email = data.get('email')
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """SELECT `password` FROM user WHERE `email` = %s"""   
    cursor.execute(query, (email,))
    result = cursor.fetchone()
    print(result)    
    
    if result:
        if check_password_hash(result[0], currentPassword):
            
            hashed_password = generate_password_hash(newPassword)
            query = """UPDATE `user` SET password = %s  WHERE `email` = %s"""   
            cursor.execute(query, (hashed_password,email,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'msg': 'Password Updated'}), 201