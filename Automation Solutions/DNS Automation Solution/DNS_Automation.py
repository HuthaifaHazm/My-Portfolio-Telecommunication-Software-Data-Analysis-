from flask import Flask, request, jsonify
import paramiko
from flask_cors import CORS
import dns.resolver
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

AUTH_TOKEN = os.getenv("AUTH_TOKEN")
App_Host = os.getenv("App_Host")
App_Port = os.getenv("App_Port")
DNS1_Name = os.getenv("DNS1_Name")
DNS1_Host = os.getenv("DNS1_Host")
DNS1_User = os.getenv("DNS1_User")
DNS1_Password = os.getenv("DNS1_Password")
DNS1_ZoneFile = os.getenv("DNS1_ZoneFile")
DNS1_DataIP = os.getenv("DNS1_DataIP")
DNS2_Name = os.getenv("DNS2_Name")
DNS2_Host = os.getenv("DNS2_Host")
DNS2_User = os.getenv("DNS2_User")
DNS2_Password = os.getenv("DNS2_Password")
DNS2_ZoneFile = os.getenv("DNS2_ZoneFile")
DNS2_DataIP = os.getenv("DNS2_DataIP")
DNS3_Name = os.getenv("DNS3_Name")
DNS3_Host = os.getenv("DNS3_Host")
DNS3_User = os.getenv("DNS3_User")
DNS3_Password = os.getenv("DNS3_Password")
DNS3_ZoneFile = os.getenv("DNS3_ZoneFile")
DNS3_DataIP = os.getenv("DNS3_DataIP")
DNS4_Name = os.getenv("DNS4_Name")
DNS4_Host = os.getenv("DNS4_Host")
DNS4_User = os.getenv("DNS4_User")
DNS4_Password = os.getenv("DNS4_Password")
DNS4_ZoneFile = os.getenv("DNS4_ZoneFile")
DNS4_DataIP = os.getenv("DNS4_DataIP")

CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization", "X-API-Key"]
)

DNS_SERVERS = [
    {
        "name": DNS1_Name,
        "host": DNS1_Host,
        "user": DNS1_User,
        "password": DNS1_Password,
        "zone_file": DNS1_ZoneFile,
        "style": "IN",
        "data_ip": DNS1_DataIP
    },
    {
        "name": DNS2_Name,
        "host": DNS2_Host,
        "user": DNS2_User,
        "password": DNS2_Password,
        "zone_file": DNS2_ZoneFile,
        "style": "IN",
        "data_ip": DNS2_DataIP
    },
    {
        "name": DNS3_Name,
        "host": DNS3_Host,
        "user": DNS3_User,
        "password": DNS3_Password,
        "zone_file": DNS3_ZoneFile,
        "style": "TAB",
        "data_ip": DNS3_DataIP
    },
    {
        "name": DNS4_Name,
        "host": DNS4_Host,
        "user": DNS4_User,
        "password": DNS4_Password,
        "zone_file": DNS4_ZoneFile,
        "style": "TAB",
        "data_ip": DNS4_DataIP
    }
]




def local_nslookup(domain, dns_ip, timeout=5):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [dns_ip]
    resolver.timeout = timeout
    resolver.lifetime = timeout
    try:
        answers = resolver.resolve(domain, 'A')
        return {
            "success": True,
            "addresses": [str(a) for a in answers]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def run_ssh_command(command, host, user, password):
    """Execute SSH command and return output or error message."""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=user, password=password)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        ssh.close()
        if error.strip():
            return f"Error: {error.strip()}"
        return output
    except Exception as e:
        return f"SSH Error: {e}"


def query_records(dns, domain=None, ip=None):
    """Fetch and parse A records from a single DNS server (optionally filter by domain or IP)."""
    zone_file = dns['zone_file']
    if domain:
        cmd = f"grep '{domain}' {zone_file}"
    elif ip:
        cmd = f"grep '{ip}' {zone_file}"
    else:
        cmd = f"cat {zone_file}"
    raw_data = run_ssh_command(cmd, dns['host'], dns['user'], dns['password'])
    if "Error" in raw_data or "SSH Error" in raw_data:
        return {"server": dns['name'], "host": dns['host'], "error": raw_data}

    records = []
    for line in raw_data.splitlines():
        line = line.strip()
        if not line or line.startswith(';'):
            continue
        if "\tA" in line or " A " in line:
            parts = line.split()
            try:
                if 'A' in parts:
                    a_index = parts.index('A')
                    ip_addr = parts[a_index + 1]
                    domain_name = parts[0]
                    if len(ip_addr.split('.')) != 4:
                        continue

                    records.append({'domain': domain_name.strip('.'), 'ip': ip_addr})
            except Exception:
                continue

    return {"server": dns['name'], "host": dns['host'], "count": len(records), "records": records}


@app.route("/action", methods=["POST", "OPTIONS"])
def index():    
    if request.method == 'OPTIONS':
        return '', 200   
    api_key = request.headers.get('X-Api-Key')
    if not api_key or api_key != AUTH_TOKEN:
        return jsonify({'error': 'Unauthorized: Invalid or missing API Key'}), 401
    
    data = request.json
    action = data.get('action')
    domain = data.get('domain_name', '').strip()
    ip = data.get('domain_ip', '').strip()
    selected_dns = data.get('dns_servers', [])
    if not selected_dns and action != 'query':
      return jsonify({'error': 'No DNS servers selected'}), 400


    if action == "query":
        all_dns_results = []
        for dns in DNS_SERVERS:
            res = query_records(dns, domain if domain else None, ip if ip else None)
            all_dns_results.append(res) 

        return jsonify({
            'status': 'Query Successful',
            'total_servers': len(all_dns_results),
            'results': all_dns_results
        }), 200


    elif action == "add":
        target_dns = [dns for dns in DNS_SERVERS if dns['name'] in selected_dns]
        add_summary = []
        for dns in target_dns:
            query_result = query_records(dns, domain=domain)
            exists = False
            if "records" in query_result:
                for rec in query_result["records"]:
                    if rec["domain"] == domain or rec["domain"] == domain:
                        exists = True
                        break
            if exists:
                add_summary.append(f"{dns['name']}: Already exists")
                continue
            record = f"{domain}\tA\t{ip}"
            cmd = f"echo '{record}' >> {dns['zone_file']} && service named restart"
            result = run_ssh_command(cmd, dns['host'], dns['user'], dns['password'])
            if "Error" in result or "SSH Error" in result:
                add_summary.append(f"{dns['name']}: Failed ({result})")
            else:
                add_summary.append(f"{dns['name']}: Added successfully")
 
    
        lookup_results = []

        for dns in target_dns:
            lookup = local_nslookup(domain, dns_ip=dns["data_ip"])
            lookup_results.append({
                "dns": dns["name"],
                "resolver": dns["host"],
                "result": lookup
            })         
        summary_text = "; ".join(add_summary)
        return jsonify({
            'status': summary_text,
            'nslookup': lookup_results
        }), 200


    elif action == "remove":
        target_dns = [dns for dns in DNS_SERVERS if dns['name'] in selected_dns]
        remove_summary = []
        for dns in target_dns:
            cmd = f"sed -i '/^{domain}\tA\t{ip}$/d' {dns['zone_file']} && service named restart"
            result = run_ssh_command(cmd, dns['host'], dns['user'], dns['password'])
            if "Error" in result or "SSH Error" in result:
                remove_summary.append(f"{dns['name']}: Failed ({result})")
            else:
                remove_summary.append(f"{dns['name']}: Removed successfully")
   

        lookup_results = []

        for dns in target_dns:
            lookup = local_nslookup(domain, dns_ip=dns["data_ip"])
            lookup_results.append({
                "dns": dns["name"],
                "resolver": dns["host"],
                "result": lookup
            })

        summary_text = "; ".join(remove_summary)
        return jsonify({
            'status': summary_text,
            'nslookup': lookup_results
        }), 200


    else:
        return jsonify({'error': 'Invalid action'}), 400


if __name__ == '__main__':
    app.run(host=App_Host, port=App_Port)
