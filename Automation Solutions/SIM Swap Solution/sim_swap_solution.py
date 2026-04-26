import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import os
from xml.etree import ElementTree as ET
import re
from datetime import datetime
from openpyxl import load_workbook
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
case_store = {}
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"]
)
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
SOAP_URL = os.getenv("SOAP_URL")
SOAP_URL2 = os.getenv("SOAP_URL2")
file_path_excel = os.getenv("file_path_excel")
file_path_txt = os.getenv("file_path_txt")
group_a_prefixes = ("1234", "1235")
group_b_prefixes = ("1236", "1237", "1238", "1239")

def is_valid_value(value):
    return value.isdigit() and len(value) == 15 and value.startswith("123")



def SendSoapCmd(value1, value2, type):
    headers = {'Content-Type': 'text/xml'}

    if type == 'action1':
       soap_envelope = """
            #### soap cmd1 ###
       """
    if type == 'action2':
       soap_envelope = """
            #### soap cmd2 ###
       """
    if type == 'action3':
       soap_envelope = """
            #### soap cmd3 ###
       """
    if type == 'action4':
       soap_envelope = """
            #### soap cmd4 ###
       """
    if type == 'action5':
       soap_envelope = """
            #### soap cmd5 ###
       """

    value1 = ''.join(c for c in value1 if c.isnumeric())
    value2 = ''.join(c for c in value2 if c.isnumeric())
    if type == 'action3' or type == 'action5':
       soap_envelope = soap_envelope.format(value1, value2)
    else:
       soap_envelope = soap_envelope.format(value1)   

    if type == 'action4' or type == 'action5':
       response = requests.post(SOAP_URL2, data=soap_envelope, headers=headers)
    else:
       response = requests.post(SOAP_URL, data=soap_envelope, headers=headers)   
    
    if response.status_code == 200:
     response_xml = ET.fromstring(response.content)
     response2 = ET.tostring(response_xml).decode('utf-8')
     return response2
    else:
     return 'error'



@app.before_request
def check_auth():
    if request.method == 'OPTIONS':
        return '', 200

    if request.path == '/action':       
        auth_header = request.headers.get("Authorization")
        if not auth_header or auth_header != AUTH_TOKEN:
            return jsonify({"status": "unauthorized"}), 401       
        


@app.route('/action', methods=['POST'])
def handle_action():
    data = request.json
    TKT_Num = data.get('tktnum')
    value1 = data.get('val1')
    value2 = data.get('val2')
    value3 = ''
    value4 = ''
    
    if is_valid_value(value1) and is_valid_value(value2) and ((value1.startswith(group_a_prefixes) and value2.startswith(group_a_prefixes)) or \
       (value1.startswith(group_b_prefixes) and value2.startswith(group_b_prefixes))):
        case_store[TKT_Num] = {"TKT_Num": TKT_Num , "value3": value3 , "value4": value4, "value1": value1, "value2": value2, "time": datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")}
    else:
        return jsonify({'status': 'Invalid Input'}), 400


    try:
     
     response = SendSoapCmd(case_store[TKT_Num]['value1'], '', 'action1')
     if response == 'error':
        return jsonify({'status': 'Somthing Error, please forward the Ticket to Back Office'}), 400
     match = re.search(r"xxxx(\d+)xxxxx", response)
     case_store[TKT_Num]['value3'] = match.group(1)

     response = SendSoapCmd(case_store[TKT_Num]['value2'], '', 'action1')
     if response == 'error':
        return jsonify({'status': 'Somthing Error, please forward the Ticket to Back Office'}), 400
     match = re.search(r"xxxx(\d+)xxxxx", response)
     case_store[TKT_Num]['value4'] = match.group(1)
    except Exception as e:

        return jsonify({'status': 'Somthing Error, please forward the Ticket to Back Office'}), 400
    
 

    try:
       
       response3 = SendSoapCmd(case_store[TKT_Num]['value2'], '', 'action2')
       response4 = SendSoapCmd(case_store[TKT_Num]['value1'], case_store[TKT_Num]['value2'], 'action3')
       response5 = SendSoapCmd(case_store[TKT_Num]['value1'], '', 'action4')
       response6 = SendSoapCmd(case_store[TKT_Num]['value2'], case_store[TKT_Num]['value3'], 'action5')
       
       if response3 != 'error' and response4 != 'error' and response5 != 'error' and response6 != 'error':
          
          try: 
           new_row = {
             "A": case_store[TKT_Num]['TKT_Num'],
             "B": case_store[TKT_Num]['time'],
             "C": case_store[TKT_Num]['value3'],
             "D": case_store[TKT_Num]['value1'],
             "E": case_store[TKT_Num]['value2']
           }

           wb = load_workbook(file_path_excel)
           ws = wb.active
           ws.append(new_row)
           wb.save(file_path_excel)

           
          except Exception as e:
            pass
          
          with open(file_path_txt, 'a') as file:
                    file.write(case_store[TKT_Num]['TKT_Num'] + ' ' + case_store[TKT_Num]['value3'] + ' ' + case_store[TKT_Num]['value4'] + ' ' + case_store[TKT_Num]['time'] + "\n")  

          return jsonify({'status': 'The SIM Swap Done Successfully', 'val1': case_store[TKT_Num]['value3'], 'val2': case_store[TKT_Num]['value4']}), 200
       else:
          return jsonify({'status': 'Somthing Error, please forward the Ticket to Back Office'}), 400
          

    except Exception as e:
        return jsonify({'status': 'Somthing Error, please forward the Ticket to Back Office'}), 400



if __name__ == '__main__':
    app.run(host='x.x.x.x', port=yy)


