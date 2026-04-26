from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
import qrcode
from io import BytesIO
import requests
import os, sys
from dotenv import load_dotenv



load_dotenv()

app = Flask(__name__)


Cloud_URL = os.getenv("Cloud_URL")
secret_key = os.getenv("secret_key")
UserName = os.getenv("UserName")
Password = os.getenv("Password")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
Local_URL = os.getenv("Local_URL")
Cert_Path1 = os.getenv("Cert_Path1")
Cert_Path2 = os.getenv("Cert_Path2")
Verify_Path = os.getenv("Verify_Path")
App_Host = os.getenv("App_Host")
App_Port = os.getenv("App_Port")

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "----": "----"
}

@app.route('/')
def login():
    return render_template('login_page.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == UserName and password == Password:
        session['logged_in'] = True
        return redirect(url_for('search'))
    else:
        flash('Invalid username or password')
        return redirect(url_for('login'))

@app.route('/search')
def search():
    if not session.get('logged_in'):
        flash('You need to log in first.')
        return redirect(url_for('login'))
    
    return render_template('search-page.html', results=None)

@app.route('/search', methods=['POST'])
def search_post():
    if not session.get('logged_in'):
        flash('You need to log in first.')
        return redirect(url_for('login'))
  

    search_type = request.form.get("search_type")

    




    if search_type == "normal":

        global Info_Results
        Info_Results = []
        search_query = request.form.get('search_query')
        if len(search_query) == 12 and search_query[:3] == "123":
         search_query = search_query[3:]

        headers = {
          'x-api-key': AUTH_TOKEN
        }   
        response = requests.post(
          Local_URL,
          json={"number": search_query},
          headers=headers
        ) 

        result = response.json()
        if response.status_code == 200 and result['state'] == 'success':
          result = response.json()
          Info_Results = result['list']
          is_esim = True
          if Info_Results:
            if Info_Results[0][7] == "SIM":
                is_esim = False
            return render_template('search-page.html', results=Info_Results, query=search_query, is_esim=is_esim)
        else:
            return render_template('search-page.html', results=Info_Results, query=search_query, is_esim=is_esim)










    else:

        Status_Results = []
        search_query = request.form.get('search_query')
        if len(search_query) == 12 and search_query[:3] == "123":
         search_query = search_query[3:]

        headers = {
          'x-api-key': AUTH_TOKEN
        }   
        response = requests.post(
          Local_URL,
          json={"number": search_query},
          headers=headers
        ) 
        result = response.json()
        if response.status_code == 200 and result['state'] == 'success':
          
    
          Status_Results = Query_Status(result['iccid'])
          if Status_Results:
              if Status_Results[0][1] == 'Installed':
                  response2 = requests.post(
                   Local_URL,
                   json={"number": result['imsi']},
                   headers=headers
                 ) 
                  result2 = response2.json()
                  if response2.status_code == 200 and result2['state'] == 'success':
                      Status_Results[0][2] = result2['device_name']
                      Status_Results[0][4] = result2['TAC']

              return render_template('search-page.html', results2=Status_Results, query=search_query)    
          else:
                 return render_template('search-page.html', results2=Status_Results, query=search_query)
        else:
          return render_template('search-page.html', results2=Status_Results, query=search_query)
        

    
    



def Query_Status(full_iccid):

    result = [['','','','','']]
    payload = {
          "header": {
          "-----": "----",
          "-----": "----" 
          },
        "iccid": full_iccid
    }

    try:
        response = requests.post(
            Cloud_URL,
            headers=headers,
            json=payload,  
            cert=(Cert_Path1, Cert_Path2), 
            verify=Verify_Path,     
        )

        response.raise_for_status()


        if response.status_code == 200:
            data = response.json()
            result[0][0] = full_iccid[:-1]
            result[0][1] = ( 'Check with Core' if data['AA'] == 'X' and data['BB'] != '' 
                            else 'Ready to Use' if data['AA'] == 'X' else data['AA'])
            result[0][2] = ''
            result[0][3] = data['BB']
            result[0][4] = ''
            return result
        else:
            return False       

    except requests.exceptions.HTTPError as http_err:
           return False
    except Exception as err:
           return False


@app.route('/generate_qr', methods=['GET', 'POST'])
def generate_qr():
    if not session.get('logged_in'):
        flash('You need to log in first.')
        return redirect(url_for('login'))

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(Info_Results[0][7])
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=Info_Results[0][2] + '.png', mimetype='image/png')

@app.route('/logout')
def logout():
    session.pop('logged_in', None) 
    flash('You have been logged out.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host=App_Host, port=App_Port)
