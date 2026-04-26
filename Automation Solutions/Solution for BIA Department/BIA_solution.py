import time
from flask import Flask, jsonify, request
import time
import paramiko
from dotenv import load_dotenv
import os
import re

load_dotenv()

app = Flask(__name__)

App_Host = os.getenv("App_Host")
App_Port = os.getenv("App_Port")
server1_ip = os.getenv("server1_ip")
server1_port = os.getenv("server1_port")
server1_username = os.getenv("server1_username")
server1_password = os.getenv("server1_password")
server2_ip = os.getenv("server2_ip")
server2_port = os.getenv("server2_port")
server2_username = os.getenv("server2_username")
server2_password = os.getenv("server2_password")

def execute_command(shell, command):
    shell.send(command + '\n')
    time.sleep(0.7)

def deactivate(value):
    cmd = '-----------'+value+'-----------'    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server1_ip, port=server1_port, username=server1_username, password=server1_password)
    try:
        shell = ssh.invoke_shell()
        execute_command(shell, '---------')
        execute_command(shell, '---------')
        execute_command(shell, '---------')
        execute_command(shell, '---------')
        execute_command(shell, cmd)
        s = shell.recv(65535).decode('utf-8')
       
    finally:
        ssh.close()



def info(value):  
    IP = "" 
    if value.isdigit():
         if len(value) >= 14:
          cmd = '---------'+value+'---------'
         else:
          if value[:3] == "123":
             cmd = '---------'+value+'---------'
          else :   
             value = "123" + value[-9:]
             cmd = '---------'+value+'---------'
    else:
        cmd = '---------' + value + '---------' 


   
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server2_ip, port=server2_port, username=server2_username, password=server2_password)
    try:
        shell = ssh.invoke_shell()
        execute_command(shell, cmd)

        s = shell.recv(65535).decode('utf-8')

        matches = re.findall(r'(AAA(\d{12})|BBB(\d{15})|CCC(\d{17})|DDD(\d{65})|EEE(\d{30}))', s)
        for m in matches:
            if m[1]:  
               MSISDN = m[1]
            elif m[2]:  
               IMSI = m[2]
            elif m[3]:  
               IP = int(m[3],16)
            elif m[4]:  
               return {'MSISDN': 0, 'IMSI': 0, 'IP': 0} 
            elif m[5]:  
               return {'MSISDN': 0, 'IMSI': 0, 'IP': 0}  
   
    finally:
        ssh.close()   
        return {'MSISDN': MSISDN, 'IMSI': IMSI, 'IP': IP} 



@app.route('/api.php')
def handle_api_request():
 data = request.args.get('ip')

 if data is not None:   
    info_list = info(data)
    if info_list['MSISDN'] != 0:        
     deactivate(info_list['IMSI'])   
     time.sleep(3)
     info_list = info(data)
     return jsonify({'New IP': str(info_list['IP']),'mdn': str(info_list['MSISDN'])}), 200
    else:
      return jsonify({'error': 'there is an error or the user does not online'}), 400
    
if __name__ == '__main__':
    app.run(host=App_Host, port=App_Port)   