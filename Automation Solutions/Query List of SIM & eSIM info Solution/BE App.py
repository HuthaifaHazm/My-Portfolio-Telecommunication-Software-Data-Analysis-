from flask import Flask, request, jsonify, abort
from dotenv import load_dotenv
import os
from ldap3 import Server, Connection, ALL
import psycopg2
import logging
import time

load_dotenv()

app = Flask(__name__)

App_Host = os.getenv("App_Host")
App_Port = os.getenv("App_Port")
API_KEY_DB = os.getenv("API_KEY_DB")
LDAP_SERVER = os.getenv("LDAP_SERVER")
BASE_DN = os.getenv("BASE_DN")
BIND_DN = os.getenv("BIND_DN")
BIND_PASSWORD = os.getenv("BIND_PASSWORD")
API_KEY_DB = os.getenv("API_KEY_DB")
API_KEY_DB = os.getenv("API_KEY_DB")
DB_Host = os.getenv("DB_Host")
DB_Port = os.getenv("DB_Port")
DB_Name = os.getenv("DB_Name")
DB_User = os.getenv("DB_User")
DB_Pass = os.getenv("DB_Pass")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__) 


ALLOWED_USERS = [
    "user1@domain.com",
    "user2@domain.com",
    "user3@domain.com"
]

def get_db_connection():
    return psycopg2.connect(
        host=DB_Host,
        port=DB_Port,
        database=DB_Name,
        user=DB_User,
        password=DB_Pass
    )


auth_status = {}

def authenticate_user(email, password):
    try:
        logger.debug(f"Attempting to authenticate user: {email}")
        server = Server(LDAP_SERVER, use_ssl=False, connect_timeout=5, get_info=ALL)

        conn = Connection(
            server,
            user=BIND_DN,
            password=BIND_PASSWORD,
            auto_bind=True
        )

        conn.search(
            search_base=BASE_DN,
            search_filter=f"(mail={email})",
            attributes=["distinguishedName", "memberOf"]
        )

        if len(conn.entries) == 0:
            logger.warning(f"User not found: {email}")
            return False, "User not found"
        
        user_dn = conn.entries[0].distinguishedName.value
        logger.debug(f"User DN found: {user_dn}")

        if ALLOWED_USERS and email.lower() not in [u.lower() for u in ALLOWED_USERS]:
            logger.warning(f"User not in allowed list: {email}")
            return False, "You are not authorized"

        user_conn = Connection(
            server,
            user=user_dn,
            password=password,
            auto_referrals=False
        )

        if not user_conn.bind():
            logger.warning(f"Invalid password for user: {email}")
            return False, "Invalid email or password"

        logger.info(f"Successfully authenticated user: {email}")
        return True, "Authenticated"

    except Exception as e:
        logger.error(f"Authentication error for {email}: {str(e)}")
        return False, f"Authentication error: {str(e)}"

@app.before_request
def authenticate():
    if request.path == '/check_number':
        key = request.headers.get('x-api-key') or request.args.get('x-api-key')        
        if key != API_KEY_DB:
            abort(401, description="Unauthorized: Invalid API Key")




@app.route('/check_number', methods=['POST'])
def check_number():
    data = request.get_json()
    number = data.get('number')
    if number is None:
        return jsonify({"error": "Invalid input"}), 400

    if  number[0][:12] == '000123456789' or number[0][:12] == '000123456789' or number[0][:12] == '000123456789':
         query = """
    SELECT *
    FROM "Table1"
    WHERE "A" = ANY(%s)
    """

    else:
         query = """
    SELECT *
    FROM "Table2"
    WHERE "A" = ANY(%s)
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, (number,))
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return jsonify({"list": rows})



@app.route('/login', methods=['POST'])
def check_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    global auth_status

    if username in auth_status:
        if time.time() - auth_status[username]["time"] <= 300 and auth_status[username]["attempt_count"] > 9:
            return jsonify({'message': 'You have reached the maximum number of attempts. Try again in an hour'}), 400
        elif time.time() - auth_status[username]["time"] <= 300 and auth_status[username]["attempt_count"] < 10:
            auth_status[username]["attempt_count"] = auth_status[username]["attempt_count"] + 1
        elif time.time() - auth_status[username]["time"] > 300:
            auth_status[username] = {"attempt_count": 1, "time": time.time(), 'Authenticated': False} 
    else:
          auth_status[username] = {"attempt_count": 1, "time": time.time(), 'Authenticated': False} 

    auth_status = {n: auth_status[n] for n in auth_status if time.time() - auth_status[n]['time'] < 300}
    success, message = authenticate_user(username, password)
    if success:
            auth_status[username]["Authenticated"] = True
            logger.info(f"User logged in successfully: {username}")
            return jsonify({"status": 'success', 'message': message})
    else:
            logger.warning(f"Login failed for {username}: {message}")
            return jsonify({"status": 'failure', 'message': message}), 400

    
if __name__ == '__main__':
    app.run(host=App_Host, port=App_Port)
