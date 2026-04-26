from pywebio.output import*
from pywebio.input import*
from pywebio.session import*
from pywebio.pin import*
import time
import paramiko
import time
from pywebio.platform.flask import wsgi_app as pywebio_wsgi_app
from dotenv import load_dotenv
import os
import re

load_dotenv()

server_ip = os.getenv("server_ip")
server_port = os.getenv("server_port")
server_username = os.getenv("server_username")
server_password = os.getenv("server_password")


html_entry_text1 = """
<!DOCTYPE html>
<html lang="en">
<head>
 <meta charset="UTF-8">
 <meta name="viewport" content="width=device-width, initial-scale=1.0">
 <title>HTML Entry Text Example</title>
 <style>
    #text-input {
        width: 100%; /* Set the width to 100% of its container (the screen) */
        font-size: 18px;
        padding: 8px;
        margin-bottom: 20px;
    }
 </style>
</head>
<body>
<input type="text" id="text-input" name="text_input" placeholder="Enter Number here" required>
</body>
</html>
"""


def execute_command(shell, command):
    shell.send(command + '\n')
    time.sleep(0.7)



def submit(button_tex):
   popup('Loading . . .')
   Exist = 0
   data = html_entry_text1
   script = """
        new Promise((resolve, reject) => {
        let inputElement = document.getElementById("text-input");
        if (inputElement) {
            let inputValue = parseInt(inputElement.value);
            if (!isNaN(inputValue)) {
                resolve(inputValue);
            } else {
                reject("Invalid input. Please enter a valid integer.");
            }
        } else {
            reject("Input element not found");
        }
        });
        """

   data = str(eval_js(script))
   if data == "None" :
      popup("Please Enter The Number !")
   else :
    if data.isdigit():
      if len(data) >= 14:
          cmd = '------------'+data+''
      else:
          if data[:3] == "123":
             cmd = '----------'+data+''
          else :  
             data = "123" + data[-9:]
             cmd = '----------------'+data+''

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server_ip, port=server_port, username=server_username, password=server_password)
    try:
        shell = ssh.invoke_shell()
        execute_command(shell, '---------')
        execute_command(shell, '---------')
        execute_command(shell, '---------')
        execute_command(shell, '---------')
        execute_command(shell, cmd)
        s = shell.recv(65535).decode('utf-8')

        matches = re.findall(r'(AAA(\d{12})|BBB(\d{7})|CCC(\d{8})|DDD(\d{13})|EEE(\d{9})|FFF(\d{21}))', s)
        for m in matches:
            if m[1]:  
               MSISDN = m[1]
            elif m[2]:  
               EMM = m[2]
            elif m[3]:  
               TMSI = int(m[3],16)
            elif m[4]:  
               eNBID = int(m[4],16)
            elif m[5]:  
               sector = m[5]
            elif m[6]:  
               if m[6] == "Record does not exist":
                   Exist = 1                              

    finally:
        ssh.close()
        if Exist == 0:
         put_text(str(MSISDN) + str(EMM) + str(TMSI,16) + str(eNBID) + str(sector))
         html_Line = "<h1 style='text-align: center;'></h1>"  
         put_html(html_Line)    
        else :
         put_text(str(data) + "Not Found")
         html_Line = "<h1 style='text-align: center;'></h1>"  
         put_html(html_Line)

   close_popup()    




def app():
    html_table = "<h1 style='text-align: center;'>AccountNo.;Status;TMSI;SiteID;Cell_ID</h1>"
    html_header = "<h1 style='text-align: center;'>FL Core</h1>"
    set_html_header = html_header.replace(
    "style='text-align: center;'",
    "style='text-align: left; font-size: 42px; color: darkblue;'"
    )
    html_Info = "<h1 style='text-align: center;'>MDN or IMSI :</h1>"
    set_html_info = html_Info.replace(
    "style='text-align: center;'",
    "style='text-align: left; font-size: 20px; color: black;'"
    )
    set_html_table = html_table.replace(
    "style='text-align: center;'",
    "style='text-align: center; font-size: 20px; color: black; font-weight: bold;'"
    )
    html_Line = "<h1 style='text-align: center;'></h1>"
    put_html(set_html_header)
    put_html(set_html_info)
    put_html(html_entry_text1)
    put_buttons(['Submit Task'], onclick=submit)
    put_html(html_Line)
    put_html(set_html_table)

application = pywebio_wsgi_app(app)