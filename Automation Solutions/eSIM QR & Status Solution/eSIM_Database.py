from flask import Flask, request, jsonify, abort
from dotenv import load_dotenv
import os
import paramiko
import time
import pandas as pd
import psycopg2
import re

load_dotenv()

app = Flask(__name__)

secret_key = os.getenv("secret_key")
UserName = os.getenv("UserName")
Password = os.getenv("Password")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
Local_URL = os.getenv("Local_URL")
App_Host = os.getenv("App_Host")
App_Port = os.getenv("App_Port")
DB_Host = os.getenv("DB_Host")
DB_Port = os.getenv("DB_Port")
DB_Name = os.getenv("DB_Name")
DB_User = os.getenv("DB_User")
DB_Pass = os.getenv("DB_Pass")
server_ip = os.getenv("server_ip")
server_port = os.getenv("server_port")
server_username = os.getenv("server_username")
server_password = os.getenv("server_password")
TACs_File_Path = os.getenv("TACs_File_Path")





def get_connection():
    return psycopg2.connect(
        host=DB_Host,
        port=DB_Port,
        database=DB_Name,
        user=DB_User,
        password=DB_Pass
    )

def execute_command(shell, command):
    shell.send(command + '\n')
    time.sleep(0.7)


@app.before_request
def authenticate():
    if request.path == '/check_number':
        key = request.headers.get('x-api-key') or request.args.get('x-api-key')    
        if key != AUTH_TOKEN:
            abort(401, description="Unauthorized: Invalid API Key")





def calculate_luhn_check_digit(number: str) -> str:
    total = 0
    reverse_digits = number[::-1]

    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 0:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    check_digit = (10 - (total % 10)) % 10
    return str(check_digit)




def Get_TAC(value):
    cmd = '-------'+value+''
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server_ip, port=server_port, username=server_username  , password=server_password)
    IMEI = ''
    try:
        shell = ssh.invoke_shell()
        execute_command(shell, '---------')
        execute_command(shell, '---------')
        execute_command(shell, '---------')
        execute_command(shell, '---------')
        execute_command(shell, cmd)
        s = shell.recv(65535).decode('utf-8')

        match = re.search(r'AAA(\d{15})', s)
        if match:
          IMEI = match.group(1)
        
    finally:
        ssh.close()   

    return IMEI    
       

def Get_Device_Name(tac):
    df = pd.read_excel(TACs_File_Path)
    tac = int(tac)
    result = df.loc[df['TAC'] == tac, 'Device Name']
    if not result.empty:
      device_name = result.iloc[0]
    else:
      device_name = ''

    return device_name  







def check_number_in_DB(number, query_type):
    number_like = f"%{number}%"
    results = []

    conn = get_connection()
    cur = conn.cursor()

    query1 = """
    SELECT "A", "B", "C", "D", "E", "F", "G", "H"
    FROM "Table1"
    WHERE
        "A" ILIKE %s OR
        "B" ILIKE %s OR
        "C" ILIKE %s OR
        "D" ILIKE %s OR
        "E" ILIKE %s OR
        "F" ILIKE %s OR
        "G" ILIKE %s
    """

    cur.execute(query1, [number_like]*7)
    first_results = cur.fetchall()

    if first_results:
        cur.close()
        conn.close()
        return first_results
    elif first_results is None and query_type == 2:
        return [] 



   
    query2 = """
    SELECT "A", "B", "C", "D", "E", "F", "G"
    FROM "Table2"
    WHERE
        "A" ILIKE %s OR
        "B" ILIKE %s OR
        "C" ILIKE %s OR
        "D" ILIKE %s OR
        "E" ILIKE %s OR
        "F" ILIKE %s OR
        "G" ILIKE %s
    """

    cur.execute(query2, [number_like]*7)
    second_results = cur.fetchall()

    for row in second_results:
        row = list(row)
        if len(row) < 8:
            row.append("SIM")
        else:
            row[7] = "SIM"

        results.append(row[:8])

    cur.close()
    conn.close()

    return results



@app.route('/check_number', methods=['POST'])
def check_number():
    data = request.get_json()
    number = data.get('number')
    if number is None or len(number) < 9:
        return jsonify({"error": "Invalid input"}), 400


    
    exists = check_number_in_DB(number, 1)
    result = list(map(lambda row: row[:8], exists))
    if exists and exists != []:
        return jsonify({'state' : 'success', "list": result})
    else:
        return jsonify({'state' : 'failure'})   
    





@app.route('/check_status', methods=['POST'])
def check_status():
    data = request.get_json()
    number = data.get('number')
    if number is None or len(number) < 9:
        return jsonify({"error": "Invalid input"}), 400

    
    exists = check_number_in_DB(number, 2)
    
    if exists and exists != []:
        
        check_digit = calculate_luhn_check_digit(exists[0][0])
        full_iccid = exists[0][0] + check_digit
        return jsonify({'state' : 'success',"iccid": full_iccid, "imsi": exists[0][1]})  
    else:
        return jsonify({'state' : 'failure'})    






@app.route('/check_device', methods=['POST'])
def check_device():
    data = request.get_json()
    number = data.get('number')
    if number is None:
        return jsonify({"error": "Invalid input"}), 400

    
    IMEI = Get_TAC(number)
    
    if IMEI != '':
        device_name = Get_Device_Name(IMEI[:8])
        return jsonify({'state' : 'success',"device_name": device_name, "TAC": IMEI[:8]})
    else:
        return jsonify({'state' : 'failure'})       







if __name__ == '__main__':
    app.run(host=App_Host, port=App_Port)
