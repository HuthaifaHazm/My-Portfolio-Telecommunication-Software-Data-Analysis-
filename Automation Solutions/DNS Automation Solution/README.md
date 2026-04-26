# Multi-Node DNS Orchestration & Verification System

## 📌 The Problem
Managing DNS 'A' records across multiple enterprise name servers was a fragmented and time-consuming manual process. It involved:
* SSH-ing into 4+ separate servers individually.
* Manually editing sensitive Zone files (`/var/named/`).
* Manually restarting DNS services.
* Running manual `nslookup` or `dig` commands to verify propagation.
This process took ~30-40 minutes per batch of changes and carried a high risk of syntax errors.

## 🛠 My Solution
I built a full-stack Web Application (Flutter/Python) that acts as a centralized control plane for DNS management. It provides a "single-click" interface to query, add, or remove records across the entire DNS infrastructure simultaneously.

### Key Technical Features:
* **Centralized Orchestration:** Uses **Paramiko** to execute concurrent record management across multiple remote Linux DNS servers.
* **Automated Verification:** Integrates `dnspython` to perform immediate post-action `nslookup` against the specific nameservers to confirm successful propagation.
* **Idempotency & Safety:** Implements pre-check logic to prevent duplicate record creation and uses `sed` for precise, automated record removal.
* **Flutter Web Frontend:** Provides a professional, user-friendly interface for non-CLI users to manage infrastructure safely.
* **Secure API Communication:** Backend is hardened with **X-API-Key** authentication and **CORS** policy management.

## 💻 Logic Workflow
1. **Pre-Check:** System queries all target servers to see if the domain/IP already exists.
2. **Execution:** Appends the standardized 'A' record and restarts the `named` service via SSH.
3. **Verification:** The backend immediately resolves the domain against the server's data IP to ensure the record is live.

## 📈 Business Impact
* **Efficiency:** Reduced DNS record management time by **30 minutes per task**, allowing for near-instant updates.
* **Stability:** Standardized record formatting (`domain\tA\tip`) eliminates manual syntax errors that cause service outages.
* **Visibility:** Provides a unified view of all A-records across multiple zones in one search query.

---

## 👨‍💻 Author
**Huthaifa Hazem Ismail**
*Telecommunications Engineer & Data Analyst & Software Development*