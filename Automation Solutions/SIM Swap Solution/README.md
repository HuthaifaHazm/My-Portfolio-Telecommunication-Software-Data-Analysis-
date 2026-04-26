# SIM Swap Automation

## 📌 The Problem
In a high-pressure telecommunications environment, manual SIM swapping was a slow, manual process. Technicians had to manually interact with network nodes (HSS/PCRF), which led to:
* High resolution times (averaging 2 hours per day).
* High risk of manual entry errors.
* Lack of structured logging for audit and finance reporting.

## 🛠 My Solution
I developed a Python-based automation layer using the **Flask** framework to streamline this workflow. This service acts as a bridge between the support team and the core team.

### Key Logic & Features:
* **Validation Engine:** Automatically checks input prefixes and lengths to ensure only valid data reaches the network.
* **SOAP Orchestration:** Automates five distinct network actions in a single execution sequence.
* **Automated Data Capture:** Simultaneously updates technical audit logs and business Excel reports, ensuring 100% data consistency for the finance department.
* **Security-First Approach:** Implemented token-based authentication and environment-based configuration to protect network integrity.

📈 Impact
By implementing this automation, the ticket resolution time was saved 2 hours. 
Significantly improving the Quality of Service (QoS) and operational efficiency within the core department.


---

## 👨‍💻 Author
**Huthaifa Hazem Ismail**
*Telecommunications Engineer & Data Analyst & Software Development*