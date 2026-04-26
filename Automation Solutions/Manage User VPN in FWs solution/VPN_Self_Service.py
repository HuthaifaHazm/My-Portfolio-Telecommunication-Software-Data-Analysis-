import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import time
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

App_Host = os.getenv("App_Host")
App_Port = os.getenv("App_Port")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")  
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SUBJECT_EMAIL = os.getenv("SUBJECT_EMAIL")
BASE_URL_1 = os.getenv("BASE_URL_1")
BASE_URL_2 = os.getenv("BASE_URL_2")
BASE_URL_21 = os.getenv("BASE_URL_21")
BASE_URL_22 = os.getenv("BASE_URL_22")
BASE_URL_23 = os.getenv("BASE_URL_23")
BASE_URL_3 = os.getenv("BASE_URL_3")
BASE_URL_33 = os.getenv("BASE_URL_33")
API_KEY_1 = os.getenv("API_KEY_1")
API_KEY_2 = os.getenv("API_KEY_2")
API_KEY_3 = os.getenv("API_KEY_3")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

otp_store = {}
user_status = {}

CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"]
)


headers = {
    "Authorization": f"Bearer {API_KEY_1}",
    "Content-Type": "application/json"
}

headers2 = {
    "Authorization": f"Bearer {API_KEY_2}",
    "Content-Type": "application/json"
}

headers3 = {
    "Authorization": f"Bearer {API_KEY_3}",
    "Content-Type": "application/json"
}

def get_email(username):
  key = "{:06d}".format(secrets.randbelow(10**20))

  try:
    get_response = requests.get(BASE_URL_1, headers=headers, verify=False)
    get_response.raise_for_status()
    data = get_response.json()
    otp_store[username] = {"username": username , "email": data["results"][0]["email"],"otp": key, "time": time.time(), "newVal": '' ,"FW":1}
    return get_response.json()
  except requests.exceptions.RequestException as e:
    x = 0

  try:
    get_response2 = requests.get(BASE_URL_2, headers=headers2, verify=False)
    get_response2.raise_for_status()
    data = get_response2.json()
    otp_store[username] = {"username": username , "email": data["results"][0]["email"],"otp": key, "time": time.time(), "newVal": '' ,"FW":2}
    return get_response2.json()
  except requests.exceptions.RequestException as e:
    x = 0

  try:
    get_response22 = requests.get(BASE_URL_22, headers=headers2, verify=False)
    get_response22.raise_for_status()
    data = get_response22.json()
    otp_store[username] = {"username": username , "email": data["results"][0]["email"],"otp": key, "time": time.time(), "newVal": '' ,"FW":22}
    return get_response22.json()
  except requests.exceptions.RequestException as e:
    x = 0

  try:
    get_response23 = requests.get(BASE_URL_23, headers=headers2, verify=False)
    get_response23.raise_for_status()
    data = get_response23.json()
    otp_store[username] = {"username": username , "email": data["results"][0]["email"],"otp": key, "time": time.time(), "newVal": '' ,"FW":23}
    return get_response23.json()
  except requests.exceptions.RequestException as e:
    x = 0    


  try:
    get_response3 = requests.get(BASE_URL_3, headers=headers3, verify=False)
    get_response3.raise_for_status()
    data = get_response3.json()
    otp_store[username] = {"username": username , "email": data["results"][0]["email"],"otp": key, "time": time.time(), "newVal": '' ,"FW":3}
    return get_response3.json()
  except requests.exceptions.RequestException as e:
    pass


  return 'Username Not Found'
def take_action(userData):
    
    payload = {
        "field": userData['newVal'] 
    }

    payload2 = {
        "field1": userData['username'],
        "field2": userData['newVal'] 
    }
    try:
     if userData['FW'] == 1:
      put_response = requests.put(BASE_URL_1, headers=headers, json=payload, verify=False)
      put_response.raise_for_status()


     elif userData['FW'] == 2:
      put_response = requests.post(BASE_URL_2, headers=headers2, json=payload2, verify=False)
      put_response.raise_for_status()

     elif userData['FW'] == 22:
      put_response = requests.post(BASE_URL_22, headers=headers2, json=payload2, verify=False)
      put_response.raise_for_status()


     elif userData['FW'] == 23:
      put_response = requests.post(BASE_URL_23, headers=headers2, json=payload2, verify=False)
      put_response.raise_for_status()


     elif userData['FW'] == 3:   
      put_response = requests.post(BASE_URL_3, headers=headers3, json=payload2, verify=False)
      put_response.raise_for_status()

     
     return "success"

    except requests.exceptions.RequestException as e:
     return "failed"



@app.before_request
def check_auth():
    if request.method == 'OPTIONS':
        return '', 200

    if request.path == '/action':
        auth_header = request.headers.get("Authorization")
        if not auth_header or auth_header != f"Bearer {AUTH_TOKEN}":
            return jsonify({"status": "unauthorized"}), 401
        

@app.route('/action', methods=['POST'])
def handle_action():
    data = request.json
    action = data.get('action')
    username = data.get('username')
    otp = data.get('otp')
    newVal = data.get('newVal')
    if username in user_status:
       if time.time() - user_status[username]["time"] <= 3600 and user_status[username]["otp_count"] > 4:
          return jsonify({'status': 'You have reached the maximum number of attempts. Try again in an hour'})
       elif time.time() - user_status[username]["time"] <= 3600 and user_status[username]["otp_count"] < 5:
          user_status[username]["otp_count"] = user_status[username]["otp_count"] + 1
       elif time.time() - user_status[username]["time"] > 3600:
          user_status[username]["otp_count"] = 1   
          user_status[username]["time"] =  time.time()
    else:
       user_status[username] = {"username": username , "otp_count": 1, "time": time.time()}   
    
    if action == 'action1':
        result = get_email(username)
        if result == 'Username Not Found':
           return jsonify({'status': 'The request send successfully'})
        else:
           msg = MIMEMultipart()
           msg["From"] = SENDER_EMAIL 
           msg["To"] = otp_store[username]['email']
           msg["Subject"] = SUBJECT_EMAIL
           msg.attach(MIMEText("Your authentication code is " + otp_store[username]['otp'], "plain"))
          
           try:
              server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
              server.sendmail(SENDER_EMAIL, otp_store[username]['email'], msg.as_string())
              server.quit()
           except Exception as e:
              return jsonify({'status': 'Username Not Found'})
           return jsonify({'status': 'The request send successfully'})
        




    elif action == 'action2':
        if username not in otp_store:
            return jsonify({'status': 'Invalid OTP'})
        stored = otp_store[username]
        if otp == stored["otp"]:
            if time.time() - stored["time"] <= 60:
                return jsonify({'status': 'success'})
            else:
                return jsonify({'status': 'OTP expired', 'reason': 'OTP expired'})
        else:
            return jsonify({'status': 'Invalid OTP', 'reason': 'Invalid OTP'})
        




    elif action == 'action2':
        stored = otp_store[username]
        if otp == stored["otp"]:
            if time.time() - stored["time"] <= 120:
                otp_store[username]['newVal'] = newVal
                result2 = take_action(otp_store[username])
                if result2 == "failed":
                    return jsonify({'status': "error"})
                elif result2 == "success":   
                   return jsonify({'status': 'Done Successfully'})
            else:
                return jsonify({'status': 'OTP expired', 'reason': 'OTP expired'})
        
    


    return jsonify({'status': 'error'}), 400

if __name__ == '__main__':
    app.run(host=App_Host, port=App_Port)