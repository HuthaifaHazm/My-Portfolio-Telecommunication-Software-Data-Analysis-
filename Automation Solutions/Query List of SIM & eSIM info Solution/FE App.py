from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
import pandas as pd
import re
from werkzeug.utils import secure_filename
import os
import tempfile
import requests
from io import BytesIO
import uuid
import sys
from functools import wraps
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask( __name__)

App_Host = os.getenv("App_Host")
App_Port = os.getenv("App_Port")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
BE_SERVER_URL = os.getenv("BE_SERVER_URL")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

headers = {
    'x-api-key': AUTH_TOKEN
}


app.secret_key = os.urandom(24).hex()
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)

app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls'}


# Valid ICCID prefixes
VALID_PREFIXES = [
    '1234567890000',
    '1234567800000',
    '1234567000000',
    '1234560000000',
    '1234500000000',
    '1234000000000',
    '1230000000000',
    '1200000000000',
    '1000000000000',
    '0000000000000',
    '00000123456789',
    '00000023456789',
    '00000003456789',
    '00000000456789',
    '00000000056789',
    '00000000006789',
    '00000000000789',
    '00000000000089',
    '00000000000009',
]

SIM_group = [
    '1234567890000',
    '1234567800000',
    '1234567000000',
    '1234560000000',
    '1234500000000',
    '1234000000000',
    '1230000000000',
    '1200000000000',
    '1000000000000',
    '0000000000000',
]

eSIM_group = [
    '00000123456789',
    '00000023456789',
    '00000003456789',
    '00000000456789',
    '00000000056789',
    '00000000006789',
    '00000000000789',
    '00000000000089',
    '00000000000009',
]


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session or not session['authenticated']:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def detect_iccid_group(iccids):
    is_sim = False
    is_esim = False

    for iccid in iccids:
        if any(iccid.startswith(p) for p in SIM_group):
            is_sim = True
        elif any(iccid.startswith(p) for p in eSIM_group):
            is_esim = True

    if is_sim and is_esim:
        return "MIXED"
    elif is_sim:
        return "SIM"
    elif is_esim:
        return "eSIM"
    else:
        return "UNKNOWN"

  

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def validate_iccid(iccid):
    """Validate individual ICCID"""
    if not isinstance(iccid, (str, int)):
        return False
    
    iccid_str = str(iccid)
    if len(iccid_str) != 19:
        return False
    valid_prefix = False
    for prefix in VALID_PREFIXES:
        if iccid_str.startswith(prefix):
            valid_prefix = True
            break
    
    if not valid_prefix:
        return False
    
    return True

def validate_iccid_range(from_iccid, to_iccid):
    """Validate ICCID range"""
    from_str = str(from_iccid)
    to_str = str(to_iccid)
    
    if len(from_str) != 19 or len(to_str) != 19:
        return False, "ICCID must contain exactly 19 digits"
    
    if int(to_iccid) <= int(from_iccid):
        return False, "'To ICCID' must be greater than 'From ICCID'"
    
    from_valid = any(from_str.startswith(prefix) for prefix in VALID_PREFIXES)
    to_valid = any(to_str.startswith(prefix) for prefix in VALID_PREFIXES)
    
    if not from_valid or not to_valid:
        return False, "ICCID must start with valid prefix"
    
    from_prefix = next((prefix for prefix in VALID_PREFIXES if from_str.startswith(prefix)), None)
    to_prefix = next((prefix for prefix in VALID_PREFIXES if to_str.startswith(prefix)), None)
    
    if from_prefix != to_prefix:
        return False, "Both ICCIDs must have the same starting digits"
    
    return True, "Valid ICCID range"

def extract_iccids_from_excel(filepath):
    """Extract all ICCIDs from all sheets in Excel file"""
    all_iccids = []
    
    try:
        excel_file = pd.ExcelFile(filepath)
        
        for sheet_name in excel_file.sheet_names:
            try:
                df = pd.read_excel(filepath, sheet_name=sheet_name, header=None, engine='openpyxl')
                for cell in df.values.flatten():
                    if pd.notna(cell):
                        cell_str = str(cell).strip()
                        digits_only = re.sub(r'\D', '', cell_str)
                        
                        if digits_only and validate_iccid(digits_only):
                            all_iccids.append(digits_only)
                            
            except Exception as e:
                continue
        all_iccids = sorted(list(set(all_iccids)))
        
    except Exception as e:
        return []
    
    return all_iccids

def create_excel_from_api_response(api_data, iccid_group="UNKNOWN"):
    """Create Excel file from API response data - handles both 7 and 8 column data"""
    try:
        if not api_data:
            return None
        
        first_row = api_data[0]
        num_columns = len(first_row)
        if num_columns == 7:
            columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        elif num_columns == 8:
            columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'F']
        else:
            columns = [f'Column {i+1}' for i in range(num_columns)]
    
        df = pd.DataFrame(api_data, columns=columns)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Full Info', index=False)
            worksheet = writer.sheets['Full Info']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        return output
        
    except Exception as e:
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'GET':
        return render_template('login.html')
    
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        auth_response = requests.post(
            f"{BE_SERVER_URL}/login",
            json={"username": username, "password": password},
            timeout=10
        )
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            session.permanent = True
            session['authenticated'] = True
            session['username'] = username
            session['auth_token'] = auth_data.get('token', str(uuid.uuid4()))
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'token': session['auth_token'],
                'user': {'username': username}
            })
        else:
            error_msg = 'Invalid credentials'
            try:
                error_data = auth_response.json()
                error_msg = error_data.get('message', error_data.get('error', error_msg))
            except:
                pass
            
            return jsonify({'error': error_msg}), auth_response.status_code
            
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Cannot connect to authentication server'}), 503
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Authentication server timeout'}), 504
    except Exception as e:
        return jsonify({'error': 'Authentication failed'}), 500

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Main page - protected by login"""
    return render_template('index.html', username=session.get('username'))

@app.route('/submit', methods=['POST'])
@login_required
def submit():
    try:
        from_iccid = request.form.get('from_iccid', '').strip()
        to_iccid = request.form.get('to_iccid', '').strip()
        excel_file = request.files.get('excel_file')
        if ((not from_iccid or not to_iccid) and not excel_file):
            return jsonify({
                'status': 'failed',
                'message': 'Both ICCID fields are required when no Excel file is uploaded'
            })
        
        if (from_iccid and to_iccid and excel_file and excel_file.filename):
            return jsonify({
                'status': 'failed',
                'message': 'Cannot provide both ICCID range and Excel file. Use one method only.'
            })
        
        if (from_iccid and to_iccid and (not excel_file or not excel_file.filename)):
            if not from_iccid.isdigit() or not to_iccid.isdigit():
                return jsonify({
                    'status': 'failed',
                    'message': 'ICCID must contain only digits'
                })
            
            is_valid, message = validate_iccid_range(from_iccid, to_iccid)
            if not is_valid:
                return jsonify({
                    'status': 'failed',
                    'message': message
                })
            
            try:
                from_int = int(from_iccid)
                to_int = int(to_iccid)
                
                iccids_in_range = []
                for iccid in range(from_int, to_int + 1):
                    iccid_str = str(iccid).zfill(19)
                    if validate_iccid(iccid_str):
                        iccids_in_range.append(iccid_str)
                
                if not iccids_in_range:
                    return jsonify({
                        'status': 'failed',
                        'message': 'No valid ICCIDs found in the specified range'
                    })
                
                iccid_group = detect_iccid_group(iccids_in_range)
                
                if iccid_group == "MIXED":
                    return jsonify({
                        'status': 'failed',
                        'message': 'Please separate the eSIM and SIM batches'
                    })
                
                try:
                    response = requests.post(
                        f"{BE_SERVER_URL}/check_number",
                        json={"number": iccids_in_range},
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        search_results = result.get('list', [])
                        
                        if not search_results:
                            return jsonify({
                                'status': 'failed',
                                'message': 'No data returned from API'
                            })
                        excel_buffer = create_excel_from_api_response(search_results, iccid_group)
                        if excel_buffer:
                            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"full_info_{iccid_group}_{timestamp}.xlsx"
                            temp_dir = tempfile.gettempdir()
                            temp_file_path = os.path.join(temp_dir, filename) 
                            with open(temp_file_path, 'wb') as f:
                                f.write(excel_buffer.getvalue())
                            
                            return jsonify({
                                'status': 'success',
                                'message': f'Found {len(search_results)} {iccid_group} records. Download will start automatically.',
                                'download_url': f'/download/{filename}',
                                'temp_file_path': temp_file_path,
                                'data': search_results,
                                'count': len(search_results),
                                'iccid_group': iccid_group
                            })
                        else:
                            return jsonify({
                                'status': 'failed',
                                'message': 'Error creating Excel file'
                            })
                    else:
                        error_msg = f"API Error: {response.status_code}"
                        if response.text:
                            error_msg += f" - {response.text[:100]}"
                        return jsonify({
                            'status': 'failed',
                            'message': error_msg
                        })
                        
                except requests.exceptions.RequestException as e:
                    return jsonify({
                        'status': 'failed',
                        'message': f'Error connecting to API: {str(e)}'
                    })
                
            except ValueError as e:
                return jsonify({
                    'status': 'failed',
                    'message': 'Invalid ICCID numbers'
                })
        
        if (not from_iccid and not to_iccid and excel_file and excel_file.filename):
            if not allowed_file(excel_file.filename):
                return jsonify({
                    'status': 'failed',
                    'message': 'Invalid file type. Only Excel files (.xlsx, .xls) are allowed.'
                })
            
            filepath = None
            try:
                filename = secure_filename(excel_file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                excel_file.save(filepath)
                iccids = extract_iccids_from_excel(filepath)
                
                if not iccids:
                    return jsonify({
                        'status': 'failed',
                        'message': 'No valid ICCIDs found in the Excel file'
                    })
                
                iccid_group = detect_iccid_group(iccids)
                
                if iccid_group == "MIXED":
                    return jsonify({
                        'status': 'failed',
                        'message': 'Please separate the eSIM and SIM batches in the Excel file'
                    })
                
                try:
                    response = requests.post(
                        f"{BE_SERVER_URL}/check_number",
                        json={"number": iccids},
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        search_results = result.get('list', [])
                        
                        if not search_results:
                            return jsonify({
                                'status': 'failed',
                                'message': 'No data returned from API for Excel ICCIDs'
                            })
                        
                        excel_buffer = create_excel_from_api_response(search_results, iccid_group)
                        
                        if excel_buffer:
                            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"full_info_{iccid_group}_excel_{timestamp}.xlsx"
                            temp_dir = tempfile.gettempdir()
                            temp_file_path = os.path.join(temp_dir, filename)
                            with open(temp_file_path, 'wb') as f:
                                f.write(excel_buffer.getvalue())
                            return jsonify({
                                'status': 'success',
                                'message': f'Found {len(search_results)} {iccid_group} records from Excel file. Download will start automatically.',
                                'download_url': f'/download/{filename}',
                                'temp_file_path': temp_file_path,
                                'data': search_results,
                                'count': len(search_results),
                                'iccid_group': iccid_group
                            })
                        else:
                            return jsonify({
                                'status': 'failed',
                                'message': 'Error creating Excel file'
                            })
                    else:
                        error_msg = f"API Error: {response.status_code}"
                        if response.text:
                            error_msg += f" - {response.text[:100]}"
                        return jsonify({
                            'status': 'failed',
                            'message': error_msg
                        })
                        
                except requests.exceptions.RequestException as e:
                    return jsonify({
                        'status': 'failed',
                        'message': f'Error connecting to API: {str(e)}'
                    })
                
            except Exception as e:
                error_msg = str(e)
                return jsonify({
                    'status': 'failed',
                    'message': f'Error processing Excel file: {error_msg}'
                })
                
            finally:
                if filepath and os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except Exception as e:
                        pass
        
        return jsonify({
            'status': 'failed',
            'message': 'Invalid input combination'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        })

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    """Endpoint to download generated Excel file"""
    try:
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        if os.path.exists(file_path):
            return send_file(
                file_path,
                as_attachment=True,
                download_name=filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            return jsonify({
                'status': 'failed',
                'message': 'File not found or expired. Please generate the file again.'
            })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Download error: {str(e)}'
        })

if __name__ == '__main__':
    app.run(host=App_Host, port=App_Port)