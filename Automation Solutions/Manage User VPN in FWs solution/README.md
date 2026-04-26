# Corporate VPN Self-Service & Security Automation Portal

## 📌 The Problem
Managing VPN settings for a large workforce often creates a bottleneck for IT Departments. Users frequently need to update configurations or reset settings, requiring manual intervention on the company's core firewalls. This manual process is:
1. **Slow:** Users wait for tickets to be resolved.
2. **Risky:** Manual firewall changes are prone to human error.
3. **Insecure:** Standard password-only access is vulnerable to credential theft.

## 🛠 My Solution
I developed a **Self-Service Orchestration Layer** that allows employees to manage their VPN profiles securely. The system uses a **Flutter Web Frontend** and a **Python (Flask) Backend** to interface directly with enterprise firewall APIs.

### Key Technical Features:
* **Automated Profile Discovery:** The backend dynamically queries multiple firewall clusters (FW1, FW2, FW3) to locate the user's profile and retrieve their registered corporate email address.
* **OTP-Based Two-Factor Authentication (2FA):** Implemented a custom OTP engine that generates secure, time-sensitive verification codes sent via SMTP to ensure the user is authorized.
* **Firewall API Integration:** Uses RESTful API calls (`GET`, `POST`, `PUT`) to update firewall settings in real-time, replacing manual CLI or GUI entry.
* **Security Hardening:** * **Throttling:** Limits users to 5 OTP attempts per hour to mitigate abuse.
    * **State Management:** Uses an in-memory `otp_store` with expiration logic to prevent the use of stale or compromised codes.
    * **Information Leakage Protection:** Standardized API responses to prevent username discovery by unauthorized parties.

## 💻 Logic Workflow
1. **Identification:** User enters their username in the Flutter UI.
2. **Retrieval:** The backend scans all active firewall nodes to find the associated email address.
3. **Challenge:** An OTP is generated and emailed to the user's official corporate account.
4. **Validation:** The user enters the OTP; the backend verifies the code and the 120-second expiration window.
5. **Execution:** Upon successful verification, the backend pushes the configuration change to the specific firewall node holding that user's profile.

## 📈 Business Impact
* **Zero-Touch IT:** Reduced VPN-related support tickets by automating the most common configuration tasks.
* **Enhanced Security:** Added a 2FA layer to the VPN management process that didn't exist previously.
* **Service Availability:** Provided 24/7 self-service capabilities for remote employees across different time zones.

---

## 👨‍💻 Author
**Huthaifa Hazem Ismail**
*Telecommunications Engineer & Data Analyst & Software Development*