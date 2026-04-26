# BIA Session Re-Assignment & IP Discovery API

## 📌 The Problem
The Business Intelligence & Analytics (BIA) department often requires the association between an MSISDN and a specific IP address for traffic analysis. However, static sessions can sometimes hang or provide stale data. Manually finding a user by IP, deactivating their session to force a re-attachment, and capturing the newly assigned IP was a multi-step manual process taking ~1 hour of daily engineering time.

## 🛠 My Solution
I developed a Flask-based automation API that performs "Closed-Loop" session management. It identifies a subscriber based on their current IP, forces a session refresh on the Core Network, and returns the new network parameters in a single JSON response.

### Key Technical Features:
* **Multi-Node Orchestration:** Securely coordinates actions between two distinct Network Elements (Server 1 for session deactivation and Server 2 for subscriber info retrieval).
* **Automated Session Teardown:** Uses **Paramiko** to execute CLI-level deactivation commands, forcing the UE (User Equipment) to perform a new Attach Procedure.
* **State Verification:** Implements a timed logic gate to wait for network propagation before re-querying the network for the newly assigned dynamic IP.
* **Complex Regex Extraction:** Parses raw signaling output to map MSISDN, IMSI, and Hexadecimal IP addresses into structured data.

## 💻 Logic Workflow
1. **Identify:** API receives a query IP and searches the core network for the associated IMSI/MSISDN.
2. **Deactivate:** Connects to the Gateway/EPC node to drop the current PDP/Session context.
3. **Re-Query:** After a short propagation delay, it fetches the fresh session data to confirm the new IP assignment.

## 📈 Business Impact
* **Efficiency:** Reduced a 60-minute manual troubleshooting task to a **5-second API call**.
* **Data Accuracy:** Ensures BIA teams are working with live, refreshed session data rather than stale cache entries.
* **Automation Ready:** The solution provides a standard JSON endpoint, allowing other internal departments to integrate session refreshing into their own dashboards.

---

## 👨‍💻 Author
**Huthaifa Hazem Ismail**
*Telecommunications Engineer & Data Analyst & Software Development*